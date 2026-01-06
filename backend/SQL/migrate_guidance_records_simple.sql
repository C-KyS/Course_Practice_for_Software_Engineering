-- 迁移指导记录表结构 - 简单版本
-- 直接添加缺失的列（如果列已存在会报错，可以忽略）

USE graduation_project_db;

-- 添加 project_id 列（如果不存在）
ALTER TABLE guidance_records ADD COLUMN project_id INT;

-- 添加 record_date 列（如果不存在）
ALTER TABLE guidance_records ADD COLUMN record_date DATETIME DEFAULT CURRENT_TIMESTAMP;

-- 添加 teacher_comment 列（如果不存在）
ALTER TABLE guidance_records ADD COLUMN teacher_comment TEXT;

-- 添加 status 列（如果不存在）
ALTER TABLE guidance_records ADD COLUMN status INT DEFAULT 0;

-- 添加 student_name 列（如果不存在）
ALTER TABLE guidance_records ADD COLUMN student_name VARCHAR(100);

-- 添加 teacher_name 列（如果不存在）
ALTER TABLE guidance_records ADD COLUMN teacher_name VARCHAR(100);

-- 设置默认值（如果有旧数据且 project_id 为 NULL）
UPDATE guidance_records SET project_id = 1 WHERE project_id IS NULL;

-- 添加外键约束（如果还没有，如果已存在会报错，可以忽略）
ALTER TABLE guidance_records 
ADD CONSTRAINT fk_guidance_project 
FOREIGN KEY (project_id) REFERENCES projects(id);

