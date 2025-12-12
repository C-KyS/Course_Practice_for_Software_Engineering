CREATE DATABASE IF NOT EXISTS graduation_project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE graduation_project_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL,
    name VARCHAR(100) NOT NULL,
    student_id VARCHAR(20), -- For students
    teacher_id VARCHAR(20), -- For teachers
    department VARCHAR(100),
    major VARCHAR(100),
    class_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    teacher_id INT NOT NULL,
    max_students INT DEFAULT 1,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- 3. Topic Applications Table (Student choices)
CREATE TABLE IF NOT EXISTS topic_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    topic_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- 4. Final Selections Table (Confirmed topic for student)
CREATE TABLE IF NOT EXISTS final_selections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    topic_id INT NOT NULL,
    confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- 5. Task Documents Table (任务书)
CREATE TABLE IF NOT EXISTS task_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    file_path VARCHAR(255),
    status ENUM('draft', 'submitted', 'approved', 'returned') DEFAULT 'draft',
    comments TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- 6. Opening Reports Table (开题报告)
CREATE TABLE IF NOT EXISTS opening_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    file_path VARCHAR(255),
    status ENUM('draft', 'submitted', 'approved', 'returned') DEFAULT 'draft',
    comments TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 7. Opening Defense Records Table (开题答辩记录)
CREATE TABLE IF NOT EXISTS opening_defense_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    defense_date DATETIME,
    location VARCHAR(100),
    questions TEXT, -- Q&A summary
    evaluation TEXT,
    result ENUM('pass', 'fail', 'conditional_pass'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 8. Guidance Records Table (指导记录)
CREATE TABLE IF NOT EXISTS guidance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    guidance_date DATE NOT NULL,
    content TEXT,
    attachment_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- 9. Midterm Checks Table (中期检查)
CREATE TABLE IF NOT EXISTS midterm_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    report_path VARCHAR(255),
    teacher_comments TEXT,
    admin_comments TEXT,
    status ENUM('pending', 'approved', 'warning') DEFAULT 'pending',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 10. Papers Table (论文)
CREATE TABLE IF NOT EXISTS papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    version VARCHAR(20), -- e.g., 'v1.0', 'final'
    file_path VARCHAR(255),
    type ENUM('draft', 'final') DEFAULT 'draft',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 11. Paper Reviews Table (论文评阅)
CREATE TABLE IF NOT EXISTS paper_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    reviewer_id INT NOT NULL, -- Could be teacher or another expert
    score DECIMAL(5, 2),
    comments TEXT,
    review_type ENUM('advisor', 'peer', 'blind') NOT NULL,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 12. Graduation Defense Table (毕业答辩)
CREATE TABLE IF NOT EXISTS graduation_defense (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    defense_date DATETIME,
    location VARCHAR(100),
    ppt_path VARCHAR(255),
    audio_record_path VARCHAR(255),
    defense_minutes TEXT, -- 答辩记录
    committee_comments TEXT,
    final_result ENUM('pass', 'fail', 'deferred'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 13. Scores Table (成绩)
CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    opening_score DECIMAL(5, 2),
    guidance_score DECIMAL(5, 2), -- 平时成绩
    advisor_review_score DECIMAL(5, 2), -- 指导教师评分
    defense_score DECIMAL(5, 2), -- 答辩成绩
    total_score DECIMAL(5, 2),
    status ENUM('draft', 'submitted', 'published') DEFAULT 'draft',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 14. Archives Table (归档)
CREATE TABLE IF NOT EXISTS archives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    archive_path VARCHAR(255), -- Path to zipped archive
    is_complete BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);