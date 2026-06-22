A Thesis Study on Facial Recognition Performance (FRR/FAR) and Real-Time Processing Speeds.  This research-oriented implementation explores the intersection of Computer Vision and data analytics.

User flow:

<img width="710" height="375" alt="image" src="https://github.com/user-attachments/assets/ed924b99-8f49-4896-abcb-c126f49c35c3" />

1. Registration:
   - User enters name, age, and gender in the registration form.
   - On submit, the page sends POST /register with the form data.
   - If registration succeeds, it opens a modal and starts face capture using /video_feed.
   - The JS code then sends POST /register_face/<user_id> to begin face registration.
   - The page polls GET /status/<user_id> every second until the backend reports state "done".
   - After completion, it refreshes the registered users list with GET /userslist.

   Registration flow:
   - Submit registration form -> POST /register -> open modal -> load /video_feed -> POST /register_face/<user_id> -> poll /status/<user_id> until done -> close modal and refresh users.

2. Recognition:
   - The recognition section displays a live camera feed from /recog_feed.
   - The user selects camera resolution (1440p or 1080p) and the page loads current settings from GET /get_resolution.
   - When the user presses "Recognize Face", the page sends POST /start_recognition and disables the button while scanning.
   - Recognition progress is reflected in the status text and button state, with a fallback timeout if SSE updates are delayed.
   - Server-sent events from /stream notify the page when recognition updates are ready.
   - On update, the page refreshes the active section (registered users, recognized log, or stats) and re-enables the button.

   Recognition flow:
   - Load /recog_feed -> read resolution from GET /get_resolution -> change with POST /set_resolution -> click recognize -> POST /start_recognition -> SSE /stream refreshes active section and re-enables button.

Important frontend functions in static/js/main.js:
- initSSE(): opens EventSource to /stream for live updates.
- register_form.onsubmit: handles registration, sends POST /register, starts /register_face, polls /status/<id>, and then calls fetchUsers() to reload the registered users list.
- fetchUsers(): loads current registered users from /userslist.
- fetchRecognized(): loads recognition log entries from /recognized_today.
- fetchStats(): loads summary counts and metrics from /recognition_stats.
- fetchAgeDistribution() and fetchGenderDistribution(): load demographic charts.
- recognizeBtn click handler: sends /start_recognition and sets a fallback timeout if SSE does not restore button state.
- Sidebar navigation: controls which section is visible and triggers data refresh when switching tabs.

Page flow summary:
- Page load initializes EventSource on /stream and loads the instruction/stats section with fetchStats(), fetchAgeDistribution(), and fetchGenderDistribution().
- Registration flow:
  - Submit the form -> POST /register.
  - On success, open the registration modal and start the face capture feed using /video_feed.
  - Send POST /register_face/<user_id> and poll GET /status/<user_id> until the backend reports "done".
  - After capture completion, close the modal, reset the form, and refresh the registered users list with fetchUsers().
- User list flow:
  - fetchUsers() calls /userslist and populates the registration table.
  - Users can be removed via POST /delete_user from the table, then fetchUsers() refreshes the view.
- Recognition flow:
  - The recognition tab shows the live image from /recog_feed.
  - The selected resolution is loaded from /get_resolution and changed via POST /set_resolution.
  - Pressing "Recognize Face" sends POST /start_recognition, disables the button, and updates the status text.
  - SSE updates from /stream re-enable the button and refresh the active section when new data arrives.
- Recognized log flow:
  - fetchRecognized() loads /recognized_today and renders the log table.
  - Individual log rows can be deleted with DELETE /delete_recognized/<id>.
- Filter/stat flow:
  - Changing the min age, max age, gender, or scan type builds filter query parameters.
  - Filters are applied by calling fetchStats(), fetchAgeDistribution(), and fetchGenderDistribution() with those query parameters.

Backend endpoints used by this page:
- GET /hypothesis_frr_far -> renders templates/hypoFARFRR/frrfar.html
- POST /register -> registers a new user record
- POST /register_face/<user_id> -> begins face capture for the registered user
- GET /status/<user_id> -> returns capture status for registration
- GET /userslist -> returns registered users for the table
- GET /recog_feed -> serves the live recognition video stream
- GET /video_feed -> serves the registration camera stream used in the modal
- GET /get_resolution -> returns currently selected camera resolution
- POST /set_resolution -> changes the resolution for the camera
- POST /start_recognition -> enables recognition mode
- GET /stream -> sends SSE update events to the page
- GET /recognized_today -> returns the recognition log shown in the recognition section
- GET /recognition_stats -> returns summary values for stat cards
- GET /age_distribution and GET /gender_distribution -> return demographic counts used by filters

Important page elements:
- #registration-form: form for creating users.
- #usersTable: displays the registered users list.
- #cameraFeed: recognition video image element, loaded from /recog_feed.
- #editDialog and #editFeed: modal dialog and registration stream image used during face capture.
- #recognizeBtn: button that starts recognition in the page.
- .sum_filter controls: min age, max age, gender, and scan type filters produce query strings for stats and demographics.
- .stats-grid cards: display totals, recognized/unrecognized counts, FPS averages, face recognition counts, dlib counts, and accuracy/failure metrics.

Important behavior details:
- The page uses server-sent events to avoid frequent polling and to react when new recognition data is available.
- A fallback timeout is added after starting recognition so the button returns to active state if SSE updates are delayed.
- Recognition log rows include a button to delete individual log entries via DELETE /delete_recognized/<id>.
- Registered users can be removed with POST /delete_user.
- The camera resolution selector persists the current choice and updates the backend immediately.

Notes for manual maintenance:
- This page is the main FRR/FAR hypothesis interface in the project.
- Any changes to the recognition flow or registration flow should also update the endpoints referenced above.
- If adding new page sections, ensure the sidebar navigation code in main.js refreshes the corresponding data.

Full page flow summary:
1. Page load:
   - Initialize SSE connection to /stream.
   - Load summary/metrics and demographics with fetchStats(), fetchAgeDistribution(), and fetchGenderDistribution().
   - Sidebar navigation is ready to switch between instructions, registration, and recognition.
2. Registration flow:
   - User submits the registration form.
   - JS sends POST /register with the form data.
   - On success, the registration modal opens and /video_feed begins the live camera stream.
   - JS sends POST /register_face/<user_id> and polls GET /status/<user_id> until state is "done".
   - When done, the modal closes, the form resets, and fetchUsers() reloads the user table.
3. Recognition flow:
   - Recognition tab loads /recog_feed into #cameraFeed.
   - Selected resolution is read from GET /get_resolution and changed with POST /set_resolution.
   - Clicking "Recognize Face" sends POST /start_recognition and disables the button while scanning.
   - The backend sends SSE updates via /stream, which re-enable the button and refresh visible data.
4. Data refresh flow:
   - Filters build query strings for min age, max age, gender, and scan type.
   - Changes trigger fetchStats(), fetchAgeDistribution(), and fetchGenderDistribution() with filter parameters.
   - Recognized log refreshes via fetchRecognized() from /recognized_today.
5. Cleanup actions:
   - Registered users may be deleted with POST /delete_user.
   - Recognized logs may be deleted with DELETE /delete_recognized/<id>.
