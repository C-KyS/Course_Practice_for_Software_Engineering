-- 迁移指导记录表结构
-- 添加缺失的列

USE graduation_project_db;

-- 检查并添加 project_id 列
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'graduation_project_db' 
    AND TABLE_NAME = 'guidance_records' 
    AND COLUMN_NAME = 'project_id');
    
SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE guidance_records ADD COLUMN project_id INT', 
    'SELECT "project_id already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加 record_date 列
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'graduation_project_db' 
    AND TABLE_NAME = 'guidance_records' 
    AND COLUMN_NAME = 'record_date');
    
SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE guidance_records ADD COLUMN record_date DATETIME DEFAULT CURRENT_TIMESTAMP', 
    'SELECT "record_date already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加 teacher_comment 列
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'graduation_project_db' 
    AND TABLE_NAME = 'guidance_records' 
    AND COLUMN_NAME = 'teacher_comment');
    
SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE guidance_records ADD COLUMN teacher_comment TEXT', 
    'SELECT "teacher_comment already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加 status 列
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'graduation_project_db' 
    AND TABLE_NAME = 'guidance_records' 
    AND COLUMN_NAME = 'status');
    
SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE guidance_records ADD COLUMN status INT DEFAULT 0', 
    'SELECT "status already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加 student_name 列
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'graduation_project_db' 
    AND TABLE_NAME = 'guidance_records' 
    AND COLUMN_NAME = 'student_name');
    
SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE guidance_records ADD COLUMN student_name VARCHAR(100)', 
    'SELECT "student_name already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加 teacher_name 列
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'graduation_project_db' 
    AND TABLE_NAME = 'guidance_records' 
    AND COLUMN_NAME = 'teacher_name');
    
SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE guidance_records ADD COLUMN teacher_name VARCHAR(100)', 
    'SELECT "teacher_name already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 设置默认值（如果有旧数据且 project_id 为 NULL）
UPDATE guidance_records SET project_id = 1 WHERE project_id IS NULL;

-- 添加外键约束（如果还没有）
-- 注意：如果外键已存在，这行会报错，可以忽略
ALTER TABLE guidance_records 
ADD CONSTRAINT fk_guidance_project 
FOREIGN KEY (project_id) REFERENCES projects(id);

