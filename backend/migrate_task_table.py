"""
迁移脚本：更新 task_documents 表结构
将旧的表结构（student_id, teacher_id）迁移到新结构（project_id）
"""
from app import create_app
from app.extensions import db
from app.models import TaskDocument, Project
from config import Config

def migrate_task_table():
    """迁移任务书表结构"""
    app = create_app(Config)
    
    with app.app_context():
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'task_documents' not in tables:
            print("表不存在，创建新表...")
            db.create_all()
            print("表创建完成！")
            return
        
        # 检查列是否存在
        columns = [col['name'] for col in inspector.get_columns('task_documents')]
        
        if 'project_id' in columns:
            print("表结构已是最新，无需迁移")
            return
        
        print("开始迁移表结构...")
        
        # 如果存在旧列，需要迁移数据
        if 'student_id' in columns and 'teacher_id' in columns:
            print("检测到旧表结构，开始迁移数据...")
            
            # 1. 添加新列
            print("添加新列 project_id...")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN project_id INT")
            
            # 2. 迁移数据：根据 student_id 和 teacher_id 查找对应的 project_id
            print("迁移数据...")
            # 获取所有旧记录
            old_records = db.engine.execute("SELECT id, student_id, teacher_id FROM task_documents")
            
            for record in old_records:
                task_id, student_id, teacher_id = record
                # 查找对应的项目
                project = Project.query.filter_by(student_id=student_id, teacher_id=teacher_id).first()
                if project:
                    db.engine.execute(
                        f"UPDATE task_documents SET project_id = {project.id} WHERE id = {task_id}"
                    )
                    print(f"  迁移记录 {task_id}: project_id = {project.id}")
                else:
                    print(f"  警告：记录 {task_id} 找不到对应的项目，跳过")
            
            # 3. 添加新列
            print("添加其他新列...")
            if 'student_draft_path' not in columns:
                db.engine.execute("ALTER TABLE task_documents ADD COLUMN student_draft_path VARCHAR(255)")
            if 'student_submitted' not in columns:
                db.engine.execute("ALTER TABLE task_documents ADD COLUMN student_submitted INT DEFAULT 0")
            if 'teacher_revision_path' not in columns:
                db.engine.execute("ALTER TABLE task_documents ADD COLUMN teacher_revision_path VARCHAR(255)")
            if 'teacher_submitted' not in columns:
                db.engine.execute("ALTER TABLE task_documents ADD COLUMN teacher_submitted INT DEFAULT 0")
            if 'admin_status' not in columns:
                db.engine.execute("ALTER TABLE task_documents ADD COLUMN admin_status VARCHAR(20)")
            
            # 4. 设置 project_id 为 NOT NULL（在数据迁移完成后）
            print("设置 project_id 为 NOT NULL...")
            db.engine.execute("ALTER TABLE task_documents MODIFY COLUMN project_id INT NOT NULL")
            
            # 5. 添加外键约束
            print("添加外键约束...")
            try:
                db.engine.execute("ALTER TABLE task_documents ADD CONSTRAINT fk_task_project FOREIGN KEY (project_id) REFERENCES projects(id)")
            except Exception as e:
                print(f"  外键约束可能已存在: {e}")
            
            # 6. 删除旧列（可选，如果需要的话）
            # db.engine.execute("ALTER TABLE task_documents DROP COLUMN student_id")
            # db.engine.execute("ALTER TABLE task_documents DROP COLUMN teacher_id")
            
            print("数据迁移完成！")
        else:
            # 如果不存在旧列，直接添加新列
            print("添加新列...")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN project_id INT")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN student_draft_path VARCHAR(255)")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN student_submitted INT DEFAULT 0")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN teacher_revision_path VARCHAR(255)")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN teacher_submitted INT DEFAULT 0")
            db.engine.execute("ALTER TABLE task_documents ADD COLUMN admin_status VARCHAR(20)")
            
            # 设置默认值（如果有旧数据）
            # 这里需要根据实际情况设置 project_id
        
        print("迁移完成！")

if __name__ == '__main__':
    migrate_task_table()

