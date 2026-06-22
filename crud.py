from flask import Blueprint, request, jsonify, redirect
from db_connection import get_db_connection
import numpy as np
import json
import pymysql
from face_recognition_functions import Camera 

crud = Blueprint('crud', __name__)



@crud.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data sent'}), 400

    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')

    if not all([name, age, gender]):
        return jsonify({'error': 'All fields are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO users (name, age, gender) VALUES (%s, %s, %s)"
        values = (name, age, gender)
        cursor.execute(sql, values)
        user_id = cursor.lastrowid  
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500

@crud.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.json.get('user_id')  # Expect JSON
    if not user_id:
        return jsonify({"error": "No user ID provided"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error deleting user:", e)
        return jsonify({"error": "Failed to delete user"}), 500


@crud.route("/delete_recognized/<int:id>", methods=["DELETE"])
def delete_recognized(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "DELETE FROM recognized_faces WHERE id = %s"
            cursor.execute(sql, (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Record not found"}), 404
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()