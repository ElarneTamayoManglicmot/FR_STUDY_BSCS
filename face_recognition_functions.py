import threading
from collections import deque
import time
from datetime import datetime, date
import json
from db_connection import get_db_connection
import cv2
import numpy as np
import face_recognition
import pymysql
from flask import Flask, request, render_template, redirect, url_for, Response, jsonify, Blueprint

face_recog_bp = Blueprint("face_recog_bp", __name__)

current_user_id = None
fps_history = deque()  
FPS_WINDOW = 3600
fps_last_hour = 0.0

capture_status = {}      # For face registration
status_lock = threading.Lock()

recog_matches = []       # For recognition alerts
recog_lock = threading.Lock()

last_ping_time = None
heartbeat_lock = threading.Lock()
HEARTBEAT_TIMEOUT = 10  # seconds

recog_threshold = 0.5
recog_threshold_lock = threading.Lock()

min_face_height = 120
min_face_height_lock = threading.Lock()

recognition_enabled = False
recognition_enabled_lock = threading.Lock()

selected_resolution = "1440p"
selected_resolution_lock = threading.Lock()

# SSE Event for real-time updates
db_updated_event = threading.Event()

# Database saving lock to prevent race conditions
saving_lock = threading.Lock()



# Camera Class
class Camera:
    def __init__(self):
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.start_stop_lock = threading.Lock()
        self.pending_resolution = None

    def start(self):
        with self.start_stop_lock:
            if self.running:
                return
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                # Fallback
                self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                raise RuntimeError("Camera could not be opened")
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
            self.last_start = time.time()
            self.running = True
            self.thread = threading.Thread(target=self._update, daemon=True)
            self.thread.start()

    def _update(self):
        while self.running:
            if self.pending_resolution:
                res = self.pending_resolution
                self.pending_resolution = None
                
                if res == "1080p":
                    width, height = 1920, 1080
                else:  # 1440p
                    width, height = 2560, 1440
                
                if self.cap:
                    self.cap.release()
                
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(0)
                
                try:
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                except Exception:
                    pass

                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                print(f"Camera re-initialized to {res}")
                time.sleep(1.0)

            if not self.cap or not self.cap.isOpened():
                time.sleep(0.01)
                continue

            success, frame = self.cap.read()
            if not success:
                time.sleep(0.01)
                continue
            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def set_resolution(self, resolution="1440p"):
        """Change camera resolution dynamically"""
        if not self.cap or not self.cap.isOpened():
            return
        
        self.pending_resolution = resolution

    def stop(self):
        with self.start_stop_lock:
            if not self.running:
                return
            self.running = False
            if self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass
            self.cap = None
            self.frame = None
            self.thread = None


camera = Camera()


# Heartbeat Watchdog
def heartbeat_watchdog():
    global last_ping_time
    while True:
        time.sleep(1)
        with heartbeat_lock:
            if last_ping_time is not None and (time.time() - last_ping_time > HEARTBEAT_TIMEOUT):
                if camera.running:
                    camera.stop()
                last_ping_time = None


threading.Thread(target=heartbeat_watchdog, daemon=True).start()


# Face Registration Worker
def process_face(user_id):
    countdown = 3
    start_time = None
    encoding_saved = False

    # Ensure camera is running
    if not camera.running:
        try:
            camera.start()
        except Exception as e:
            print("Failed to start camera:", e)
            return

    with status_lock:
        capture_status[user_id] = {"state": "pending", "remaining": countdown}

    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.02)
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame, model="hog")
        

        if len(faces) == 1:
            isDetectedDLIB = 1
            if start_time is None:
                start_time = time.time()
            elapsed = int(time.time() - start_time)
            remaining = max(0, countdown - elapsed)

            with status_lock:
                capture_status[user_id] = {"state": "countdown", "remaining": remaining}

            if remaining <= 0 and not encoding_saved:
                encodings = face_recognition.face_encodings(rgb_frame, faces)
                isDetectedFR = 1 
                if encodings:
                    encoding_str = json.dumps(encodings[0].tolist())
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE users SET face_encoding=%s WHERE id=%s",
                            (encoding_str, user_id),
                        )
                        cur.execute(
                            """
                            INSERT INTO recognized_faces (
                                user_id,
                                accuracy,
                                processing_speed,
                                created_at,
                                detected_by_face_recognition,
                                detected_by_dlib,
                                isRegister
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, 1)
                            """,
                            (
                                user_id,
                                None,
                                None,
                                datetime.now(),
                                isDetectedFR,           
                                isDetectedDLIB           
                            )
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        print(f"Face encoding saved for user_id={user_id}")
                        # Signal SSE update
                        db_updated_event.set()
                        db_updated_event.clear()
                    except Exception as e:
                        print("Error saving encoding:", e)
                    encoding_saved = True
                    with status_lock:
                        capture_status[user_id] = {"state": "done", "remaining": 0}
                    break
                    camera.stop()
        else:
            start_time = None
            with status_lock:
                capture_status[user_id]["state"] = "pending"


        time.sleep(0.02)

@face_recog_bp.route("/register_face/<int:user_id>", methods=["POST"])
def register_face(user_id):
    with status_lock:
        capture_status[user_id] = {
            "state": "pending",
            "remaining": 3
        }
    t = threading.Thread(target=process_face, args=(user_id,), daemon=True)
    t.start()
    return "", 204

# Face Recognition Worker
def load_known_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, face_encoding FROM users WHERE face_encoding IS NOT NULL")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    known_users = []

    for row in rows:
        user_id = row['id']
        name = row['name']
        encoding_json = row['face_encoding']
        if not encoding_json:
            continue
        try:
            encoding_array = np.array(json.loads(encoding_json))
            known_users.append((user_id, name, encoding_array))
        except Exception as e:
            print(f"Error parsing user encoding for {name}: {e}")
            continue

    return known_users


def recognize_faces(frame, known_users, threshold, resolution="unknown"):
    start_time = time.time()

    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(rgb_frame, model="hog")
    encodings = face_recognition.face_encodings(rgb_frame, faces)

    if len(faces) > 1:
        return [{
            "box": (top, right, bottom, left),
            "name": "Multiple Faces",
            "accuracy": 0,
            "recognized": False,
            "reason": "multiple_faces"
        } for (top, right, bottom, left) in faces]

    if not faces:
        return [{"name": "No Face Detected", "accuracy": 0, "recognized": False, "reason": "no_detection"}]

    matches = []

    for (top, right, bottom, left), encoding in zip(faces, encodings):
        box_height_full = (bottom - top) * 2

        with min_face_height_lock:
            current_min = min_face_height

        if box_height_full < current_min:
            matches.append({
                "name": "Too Small – Ignored",
                "accuracy": 0,
                "box": (top, right, bottom, left),
                "recognized": False,
                "reason": "min_face_height"
            })
            continue

        best_match = None
        best_dist = 1.0

        for user_id, name, known_encoding in known_users:
            try:
                dist = np.linalg.norm(known_encoding - encoding)
            except Exception:
                continue
            if dist < best_dist:
                best_dist = dist
                best_match = {"id": user_id, "name": name, "distance": dist}

        if best_match and best_dist < threshold:
            accuracy = max(0, (1 - best_dist) * 100)
            best_match.update({
                "accuracy": int(accuracy),
                "box": (top, right, bottom, left),
                "recognized": True,
                "reason": "matched",
            })
            matches.append(best_match)
        else:
            matches.append({
                "name": "Unknown",
                "accuracy": 0,
                "box": (top, right, bottom, left),
                "recognized": False,
                "reason": "unknown"
            })

    return matches


# Streaming Generators
def gen_frames():
    while True:
        if not camera.running:
            time.sleep(0.05)
            continue

        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame, model="hog")

        # Draw boxes
        for (top, right, bottom, left) in faces:
            cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), (0, 255, 0), 2)

        success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not success:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


def gen_recog_frames():
    global recog_matches, recognition_enabled, fps_last_hour
    last_refresh = 0
    refresh_interval = 5
    known_users = []
    recognition_start_time = None
    RECOG_TIMEOUT = 3.0 # seconds

    fps_frame_count = 0
    fps_start_time = time.time()
    current_fps = 0.0

    while True:
        fps_frame_count += 1
        now = time.time()
        elapsed = now - fps_start_time

        if elapsed >= 1.0:
            current_fps = fps_frame_count / elapsed
            fps_frame_count = 0
            fps_start_time = now

            fps_history.append((now, current_fps))

            while fps_history and fps_history[0][0] < now - FPS_WINDOW:
                fps_history.popleft()

            if fps_history:
                fps_last_hour = sum(f for _, f in fps_history) / len(fps_history)
            else:
                fps_last_hour = 0.0

        if not camera.running:
            try:
                camera.start()
            except Exception:
                time.sleep(1)
                continue
            time.sleep(0.05)

        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        # Check if recognition is enabled
        with recognition_enabled_lock:
            is_recognition_enabled = recognition_enabled

        if is_recognition_enabled:
            # Initialize or track timeout
            if recognition_start_time is None:
                recognition_start_time = time.time()
            
            # Check for timeout (no face detected for 3 seconds)
            # Note: We reset this if a face IS detected but not recognized yet? 
            # User said "if there is no face detected it will automatically stop"
            # So if faces list is empty for 3 seconds, stop.

            # Perform full recognition
            if time.time() - last_refresh > refresh_interval:
                known_users = load_known_users()
                last_refresh = time.time()

            with recog_threshold_lock:
                current_threshold = recog_threshold

            # DUAL RESOLUTION PROCESSING
            # Process 1440p
            start_1440 = time.time()
            matches_1440p = recognize_faces(frame, known_users, current_threshold, resolution="1440p")
            time_1440 = time.time() - start_1440
            speed_1440 = round(1.0 / time_1440 if time_1440 > 0 else 0, 2)
            
            # Downscale to 1080p and process
            frame_1080p = cv2.resize(frame, (1920, 1080))
            start_1080 = time.time()
            matches_1080p = recognize_faces(frame_1080p, known_users, current_threshold, resolution="1080p")
            time_1080 = time.time() - start_1080
            speed_1080 = round(1.0 / time_1080 if time_1080 > 0 else 0, 2)
            
            # Combine results - use best match but keep both metrics
            best_match = None
            accuracy_1440p = None
            accuracy_1080p = None
            
            # Check 1440p first
            for match in matches_1440p:
                if match.get("recognized", False):
                    best_match = match.copy()
                    accuracy_1440p = match.get("accuracy")
                    break
            
            # Check 1080p
            for match in matches_1080p:
                if match.get("recognized", False):
                    if best_match:
                        # Both detected - check if same person
                        if match.get("id") == best_match.get("id"):
                            # Same person in both resolutions
                            accuracy_1080p = match.get("accuracy")
                        else:
                            # Different people - use higher confidence
                            if match.get("accuracy", 0) > best_match.get("accuracy", 0):
                                best_match = match.copy()
                                accuracy_1440p = None
                                accuracy_1080p = match.get("accuracy")
                    else:
                        # Only 1080p detected
                        best_match = match.copy()
                        accuracy_1080p = match.get("accuracy")
                    break
            
            # Set final matches with both metrics
            if best_match:
                best_match["accuracy_1440p"] = accuracy_1440p
                best_match["accuracy_1080p"] = accuracy_1080p
                best_match["speed_1440p"] = speed_1440
                best_match["speed_1080p"] = speed_1080
                
                # Determine which resolution(s) detected
                if accuracy_1440p and accuracy_1080p:
                    best_match["detected_resolution"] = "both"
                elif accuracy_1440p:
                    best_match["detected_resolution"] = "1440p"
                else:
                    best_match["detected_resolution"] = "1080p"
                
                matches = [best_match]
            else:
                # No detection
                matches = [{
                    "name": "No Face Detected",
                    "accuracy": 0,
                    "recognized": False,
                    "reason": "no_detection",
                    "accuracy_1440p": None,
                    "accuracy_1080p": None,
                    "speed_1440p": speed_1440,
                    "speed_1080p": speed_1080,
                    "detected_resolution": None
                }]
            
            # Calculate total processing time
            processing_time = time_1440 + time_1080
            processing_speed = round(1.0 / processing_time if processing_time > 0 else 0, 2)

            # --- TIMEOUT LOGIC ---
            # If No Face Detected in BOTH resolutions, check timeout
            if not matches_1440p[0].get("box") and not matches_1080p[0].get("box"):
                if recognition_start_time and (time.time() - recognition_start_time > RECOG_TIMEOUT):
                    print(f"Recognition timed out after {RECOG_TIMEOUT}s of no face detection")
                    with recognition_enabled_lock:
                        recognition_enabled = False
                    recognition_start_time = None
                    # Signal SSE to reset button
                    db_updated_event.set()
                    db_updated_event.clear()
            else:
                # A face was detected (even if not recognized), reset/maintain start time if we want to give more time?
                # User said "3 seconds if there is no face detected". 
                # If a face IS detected, we can either keep the timeout running or reset it.
                # Let's reset it so the 3s ONLY applies to "No Face" scenario.
                recognition_start_time = time.time()

            with recog_lock:
                recog_matches = matches.copy()

            # Check if we have a successful recognition
            recognized_someone = False
            for match in matches:
                # Save if recognized OR if it's an "Unknown" face (but not "Too Small")
                if match.get("recognized", False) or match.get("reason") == "unknown":
                    recognized_someone = True # Treat as 'processed' so we stop
                    
                    user_id_to_save = match.get("id") # will be None if unknown
                    detected_resolution = match.get("detected_resolution")

                    # Save to database immediately
                    try:
                        with saving_lock:
                            # Re-check recognition_enabled inside the lock to prevent race condition
                            with recognition_enabled_lock:
                                if not recognition_enabled:
                                    break
                                # Set to false immediately inside the lock
                                recognition_enabled = False

                            conn = get_db_connection()
                            cur = conn.cursor()
                            
                            # Get detection flags from already processed match results
                            isDetectedDLIB = 1 # If we reached here, a face was at least seen
                            isDetectedFR = 1 if match.get("recognized", False) or match.get("reason") == "unknown" else 0
                        
                        # Extract separate metrics
                        accuracy_1440p = match.get("accuracy_1440p")
                        accuracy_1080p = match.get("accuracy_1080p")
                        speed_1440p = match.get("speed_1440p")
                        speed_1080p = match.get("speed_1080p")
                        
                        cur.execute(
                            """
                            INSERT INTO recognized_faces (
                                user_id,
                                accuracy,
                                processing_speed,
                                created_at,
                                detected_by_face_recognition,
                                detected_by_dlib,
                                isRegister,
                                detected_resolution,
                                accuracy_1440p,
                                accuracy_1080p,
                                speed_1440p,
                                speed_1080p
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, %s)
                            """,
                            (
                                user_id_to_save,
                                match.get("accuracy"),
                                processing_speed,
                                datetime.now(),
                                isDetectedFR,
                                isDetectedDLIB,
                                detected_resolution,
                                accuracy_1440p,
                                accuracy_1080p,
                                speed_1440p,
                                speed_1080p
                            )
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        print(f"Saved recognition: {match.get('name')} - Accuracy: {match.get('accuracy')}% - Speed: {processing_speed} fps - Resolution: {detected_resolution}")
                        # Signal SSE update
                        db_updated_event.set()
                        db_updated_event.clear()
                    except Exception as e:
                        print("Error saving recognition:", e)
                    
                    print("Recognition stopped after successful match")
                    break

            # Draw boxes
            for match in matches:
                if "box" not in match:
                    continue
                top, right, bottom, left = match["box"]
                if match.get("reason") == "min_face_height":
                    color = (0, 165, 255)
                    label = "Too Small" # Added label for min_face_height
                elif match.get("reason") == "multiple_faces":
                    color = (0, 0, 255)
                    label = "Only one face allowed"
                elif match.get("recognized", False):
                    color = (0, 255, 0)
                    label = f"{match.get('name', 'Unknown')} ({match.get('accuracy',0)}%)"
                else:
                    color = (0, 0, 255)
                    label = "Unknown"
                try:
                    cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), color, 2)
                    cv2.putText(frame, label, (left*2, max(10, top*2-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                except Exception:
                    pass
        else:
            # Reset tracking when recognition is disabled
            recognition_start_time = None
            
            # Just show face detection boxes without recognition
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb_frame, model="hog")
            
            
            if len(faces) > 1:
                color = (0, 0, 255)
                label = "Only one face allowed"
            else:
                color = (255, 255, 0)
                label = "Face Detected"

            for (top, right, bottom, left) in faces:
                cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), color, 2)
                cv2.putText(frame, label, (left*2, max(10, top*2-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not success:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

@face_recog_bp.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@face_recog_bp.route("/hypothesis_frame_processing_speed")
def recog_page():
    return render_template("hypoFR/recog.html")

    
@face_recog_bp.route("/hypothesis_frame_per_second")
def fps_page():
    return render_template("hypoFPS/recog.html")
    
@face_recog_bp.route("/hypothesis_frr_far")
def frrfar_page():
    return render_template("hypoFARFRR/frrfar.html")


@face_recog_bp.route("/recog_feed")
def recog_feed():
    return Response(gen_recog_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@face_recog_bp.route("/status/<int:user_id>")
def status(user_id):
    with status_lock:
        state = capture_status.get(user_id, {"state": "pending", "remaining": 3})
        return jsonify(state)


@face_recog_bp.route("/status_recog")
def status_recog():
    with recog_lock:
        return jsonify(recog_matches)


@face_recog_bp.route("/set_threshold", methods=["POST"])
def set_threshold():
    global recog_threshold
    try:
        val = request.form.get("threshold")
        val = float(val)
        val = max(0.1, min(1.0, val))
        with recog_threshold_lock:
            recog_threshold = val
        return jsonify({"status": "ok", "threshold": recog_threshold})
    except Exception as e:
        print("set_threshold error:", e)
        return jsonify({"error": "invalid threshold"}), 400


@face_recog_bp.route("/get_threshold")
def get_threshold():
    with recog_threshold_lock:
        return jsonify({"threshold": recog_threshold})


@face_recog_bp.route("/set_min_face_height", methods=["POST"])
def set_min_face_height():
    global min_face_height
    try:
        val = request.form.get("min_height")
        val = int(val)
        val = max(20, min(2000, val))
        with min_face_height_lock:
            min_face_height = val
        return jsonify({"status": "ok", "min_height": min_face_height})
    except Exception as e:
        print("set_min_face_height error:", e)
        return jsonify({"error": "invalid min_height"}), 400


@face_recog_bp.route("/get_min_face_height")
def get_min_face_height():
    with min_face_height_lock:
        return jsonify({"min_height": min_face_height})


@face_recog_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    global last_ping_time
    with heartbeat_lock:
        last_ping_time = time.time()
    return jsonify({"status": "ok"})


@face_recog_bp.route("/stop_camera")
def stop_camera():
    camera.stop()
    return "Camera stopped."

@face_recog_bp.route("/start_recognition", methods=["POST"])
def start_recognition():
    global recognition_enabled
    
    with recognition_enabled_lock:
        recognition_enabled = True
    return jsonify({"status": "ok", "recognition_enabled": True})

@face_recog_bp.route("/stop_recognition", methods=["POST"])
def stop_recognition():
    global recognition_enabled
    with recognition_enabled_lock:
        recognition_enabled = False
    return jsonify({"status": "ok", "recognition_enabled": False})

@face_recog_bp.route("/get_recognition_status")
def get_recognition_status():
    with recognition_enabled_lock:
        return jsonify({"recognition_enabled": recognition_enabled})

@face_recog_bp.route("/set_resolution", methods=["POST"])
def set_resolution():
    global selected_resolution
    try:
        data = request.get_json()
        resolution = data.get("resolution", "1440p")
        
        if resolution not in ["1440p", "1080p"]:
            return jsonify({"error": "Invalid resolution"}), 400
        
        with selected_resolution_lock:
            selected_resolution = resolution
            
        camera.set_resolution(resolution)
        
        return jsonify({"status": "ok", "resolution": selected_resolution})
    except Exception as e:
        print("set_resolution error:", e)
        return jsonify({"error": str(e)}), 400

@face_recog_bp.route("/get_resolution")
def get_resolution():
    with selected_resolution_lock:
        return jsonify({"resolution": selected_resolution})

@face_recog_bp.route("/stream")
def stream():
    def event_stream():
        # Send initial ping to establish connection
        yield "data: {\"type\": \"connected\"}\n\n"
        while True:
            # Wait for the event to be set (with a timeout to keep the connection alive)
            if db_updated_event.wait(timeout=30.0):
                yield "data: {\"type\": \"update\"}\n\n"
            else:
                # Periodic ping to prevent timeout
                yield "data: {\"type\": \"ping\"}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

@face_recog_bp.route("/recognized_today")
def recognized_today():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)


        min_age = request.args.get("min_age")
        max_age = request.args.get("max_age")
        gender = request.args.get("gender")

        filters = []
        params = []

        if min_age:
            filters.append("u.age >= %s")
            params.append(min_age)

        if max_age:
            filters.append("u.age <= %s")
            params.append(max_age)

        if gender and gender.lower() != "all":
            filters.append("u.gender = %s")
            params.append(gender)

        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause

        cur.execute(f"""
            SELECT
                rf.id,
                u.name,
                rf.accuracy,
                rf.processing_speed,
                rf.created_at,
                rf.isRegister,
                rf.detected_resolution,
                rf.accuracy_1440p,
                rf.accuracy_1080p,
                rf.speed_1440p,
                rf.speed_1080p,
                rf.detected_by_face_recognition,
                rf.detected_by_dlib
            FROM recognized_faces rf
            LEFT JOIN users u ON rf.user_id = u.id
            {where_clause}
            ORDER BY rf.created_at DESC
        """, params)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = []
        for row in rows:
            data.append({
                "id": row["id"],
                "name": row["name"],
                "accuracy": row["accuracy"],
                "processing_speed": row["processing_speed"],
                "seen_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "isRegister": row["isRegister"],
                "detected_resolution": row["detected_resolution"],
                "accuracy_1440p": row["accuracy_1440p"],
                "accuracy_1080p": row["accuracy_1080p"],
                "speed_1440p": row["speed_1440p"],
                "speed_1080p": row["speed_1080p"],
                "detected_by_face_recognition": row["detected_by_face_recognition"],
                "detected_by_dlib": row["detected_by_dlib"]
            })

        return jsonify(data)

    except Exception as e:
        print("recognized_today error:", repr(e))
        return jsonify([])

@face_recog_bp.route("/userslist")
def users_list():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor) 

        today = date.today().strftime("%Y-%m-%d")

        cur.execute("""
            SELECT id, name, gender, age
            FROM users
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = []
        for row in rows:
            data.append({
                "id": row.get("id"),
                "name": row.get('name'),
                "gender": row.get('gender'),
                "age": row.get('age'),
            })

        return jsonify(data)

    except Exception as e:
        print("users_today error:", repr(e))
        return jsonify([])

def gen_frame_feed():
    global recog_matches, fps_last_hour
    last_refresh = 0
    refresh_interval = 5
    known_users = []

    fps_frame_count = 0
    fps_start_time = time.time()
    current_fps = 0.0

    while True:
        fps_frame_count += 1
        now = time.time()
        elapsed = now - fps_start_time

        if elapsed >= 1.0:
            current_fps = fps_frame_count / elapsed
            fps_frame_count = 0
            fps_start_time = now

            fps_history.append((now, current_fps))

            while fps_history and fps_history[0][0] < now - FPS_WINDOW:
                fps_history.popleft()

            if fps_history:
                fps_last_hour = sum(f for _, f in fps_history) / len(fps_history)
            else:
                fps_last_hour = 0.0

        if not camera.running:
            try:
                camera.start()
            except Exception:
                time.sleep(1)
                continue
            time.sleep(0.05)

        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        if time.time() - last_refresh > refresh_interval:
            known_users = load_known_users()
            last_refresh = time.time()

        with recog_threshold_lock:
            current_threshold = recog_threshold

        matches = recognize_faces(frame, known_users, current_threshold)

        with recog_lock:
            recog_matches = matches.copy()

        # Draw results
        for match in matches:
            if "box" not in match:
                continue
            top, right, bottom, left = match["box"]
            if match.get("reason") == "min_face_height":
                color = (0, 165, 255)
                label = "Too Small"
            elif match.get("recognized", False):
                color = (0, 255, 0)
                label = f"{match.get('name', 'Unknown')} ({match.get('accuracy',0)}%)"
            else:
                color = (0, 0, 255)
                label = "Unknown"
            try:
                cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), color, 2)
                cv2.putText(frame, label, (left*2, max(10, top*2-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            except Exception:
                pass

        cv2.putText(
            frame,
            f"FPS (1h avg): {fps_last_hour:.2f}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"FPS: {current_fps:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 0),
            2
        )

        success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not success:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

@face_recog_bp.route("/frame_feed")
def frame_feed():
    return Response(gen_frame_feed(), mimetype="multipart/x-mixed-replace; boundary=frame")

@face_recog_bp.route("/fps_data")
def fps_data():
    """Return FPS history data for the SVG line graph, downsampled for performance."""
    try:
        if not fps_history:
            return jsonify({"times": [], "values": [], "avg": 0})

        history_list = list(fps_history)
        start_time = history_list[0][0]

        # Downsample: max 360 points (1 per ~10s for 1 hour)
        max_points = 360
        if len(history_list) > max_points:
            step = len(history_list) / max_points
            sampled = []
            for i in range(max_points):
                chunk_start = int(i * step)
                chunk_end = int((i + 1) * step)
                chunk = history_list[chunk_start:chunk_end]
                if chunk:
                    avg_time = sum(t for t, _ in chunk) / len(chunk)
                    avg_fps = sum(f for _, f in chunk) / len(chunk)
                    sampled.append((avg_time, avg_fps))
            history_list = sampled

        times = [round((t - start_time) / 60, 4) for t, _ in history_list]
        values = [round(f, 2) for _, f in history_list]
        avg = round(sum(values) / len(values), 2) if values else 0

        return jsonify({"times": times, "values": values, "avg": avg})
    except Exception as e:
        print("fps_data error:", e)
        return jsonify({"times": [], "values": [], "avg": 0})

@face_recog_bp.route("/recognition_stats")
def recognition_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        min_age = request.args.get("min_age")
        max_age = request.args.get("max_age")
        gender = request.args.get("gender")

        filters = []
        params = []

        if min_age:
            filters.append("u.age >= %s")
            params.append(min_age)

        if max_age:
            filters.append("u.age <= %s")
            params.append(max_age)

        if gender and gender.lower() != "all":
            filters.append("u.gender = %s")
            params.append(gender)

        is_register = request.args.get("is_register")
        if is_register and is_register.lower() != "all":
            if is_register.lower() == "register":
                filters.append("rf.isRegister = 1")
            elif is_register.lower() == "recognize":
                filters.append("rf.isRegister = 0")

        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause  

        cur.execute(f"""
            SELECT
                COUNT(*) AS total,
                SUM(rf.user_id IS NOT NULL) AS recognized,
                SUM(rf.user_id IS NULL) AS unrecognized,
                SUM(rf.detected_by_face_recognition) AS dbfr,
                SUM(rf.detected_by_dlib) AS dlib,
                AVG(rf.processing_speed) AS avg_processing_speed,
                SUM(CASE WHEN rf.user_id IS NOT NULL AND rf.isRegister = 0 AND (rf.accuracy_1440p IS NULL OR rf.accuracy_1080p IS NULL) THEN 1 ELSE 0 END) AS accuracy_fails,
                SUM(CASE WHEN rf.user_id IS NOT NULL AND rf.isRegister = 0 AND rf.accuracy_1440p IS NULL THEN 1 ELSE 0 END) AS fail_1440p,
                SUM(CASE WHEN rf.user_id IS NOT NULL AND rf.isRegister = 0 AND rf.accuracy_1080p IS NULL THEN 1 ELSE 0 END) AS fail_1080p
            FROM recognized_faces rf
            LEFT JOIN users u ON rf.user_id = u.id
            {where_clause}
        """, params)

        row = cur.fetchone()
        cur.close()
        conn.close()

        return jsonify({
            "total": row["total"] or 0,
            "recognized": row["recognized"] or 0,
            "unrecognized": row["unrecognized"] or 0,
            "dbfr": row["dbfr"] or 0,
            "dlib": row["dlib"] or 0,
            "processing_speed": float(row["avg_processing_speed"] or 0),
            "accuracy_fails": int(row["accuracy_fails"] or 0),
            "fail_1440p": int(row["fail_1440p"] or 0),
            "fail_1080p": int(row["fail_1080p"] or 0)
        })

    except Exception as e:
        print("recognition_stats error:", repr(e))
        return jsonify({
            "total": 0,
            "recognized": 0,
            "unrecognized": 0,
            "dbfr": 0,
            "dlib": 0,
            "processing_speed": 0,
            "accuracy_fails": 0,
            "fail_1440p": 0,
            "fail_1080p": 0
        })


@face_recog_bp.route("/age_distribution")
def age_distribution():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        min_age = request.args.get("min_age")
        max_age = request.args.get("max_age")
        gender = request.args.get("gender")

        filters = []
        params = []

        if min_age:
            filters.append("age >= %s")
            params.append(min_age)

        if max_age:
            filters.append("age <= %s")
            params.append(max_age)

        if gender and gender.lower() != "all":
            filters.append("gender = %s")
            params.append(gender)

        # Build WHERE clause
        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause

        cur.execute(f"""
            SELECT
                age,
                COUNT(*) AS count
            FROM users
            {where_clause}
            GROUP BY age
            ORDER BY age
        """, params)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:
        print("age_distribution error:", repr(e))
        return jsonify([])

@face_recog_bp.route("/gender_distribution")
def gender_distribution():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        min_age = request.args.get("min_age")
        max_age = request.args.get("max_age")
        gender = request.args.get("gender")

        filters = []
        params = []

        if min_age:
            filters.append("age >= %s")
            params.append(min_age)

        if max_age:
            filters.append("age <= %s")
            params.append(max_age)

        if gender and gender.lower() != "all":
            filters.append("gender = %s")
            params.append(gender)

        # Build WHERE clause
        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause

        cur.execute(f"""
            SELECT
                gender,
                COUNT(*) AS count
            FROM users
            {where_clause}
            GROUP BY gender
            ORDER BY count DESC
        """, params)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:
        print("gender_distribution error:", repr(e))
        return jsonify([])