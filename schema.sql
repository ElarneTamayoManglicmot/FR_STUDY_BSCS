-- Create thesis database schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT,
    course VARCHAR(255),
    gender VARCHAR(50),
    face_encoding TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recognized faces table
CREATE TABLE IF NOT EXISTS recognized_faces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    accuracy DECIMAL(5,2),
    processing_speed DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detected_by_face_recognition TINYINT(1) DEFAULT 0,
    detected_by_dlib TINYINT(1) DEFAULT 0,
    isRegister TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_user_id ON recognized_faces(user_id);
CREATE INDEX idx_created_at ON recognized_faces(created_at);
