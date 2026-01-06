"""
迁移指导记录表结构
将旧的 guidance_records 表结构迁移到新的结构
"""
from app import create_app
from app.extensions import db
from app.models import Project
from config import Config

def migrate_guidance_table():
    """迁移指导记录表结构"""
    app = create_app(Config)
    
    with app.app_context():
        try:
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'guidance_records' not in tables:
                print("表 guidance_records 不存在，将使用模型创建")
                db.create_all()
                return
            
            # 获取现有列
            columns = [col['name'] for col in inspector.get_columns('guidance_records')]
            print(f"当前表的列: {columns}")
            
            # 检查是否需要迁移
            needs_migration = False
            
            # 检查是否有旧列
            if 'student_id' in columns or 'teacher_id' in columns:
                needs_migration = True
                print("检测到旧表结构，需要迁移...")
            
            # 检查是否缺少新列
            required_columns = ['project_id', 'record_date', 'teacher_comment', 'status', 'student_name', 'teacher_name']
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                needs_migration = True
                print(f"缺少以下列: {missing_columns}")
            
            if not needs_migration:
                print("表结构已是最新，无需迁移")
                return
            
            print("开始迁移表结构...")
            
            # 1. 添加新列（如果不存在）
            if 'project_id' not in columns:
                print("添加 project_id 列...")
                try:
                    db.engine.execute("ALTER TABLE guidance_records ADD COLUMN project_id INT")
                    print("  ✓ project_id 添加成功")
                except Exception as e:
                    print(f"  ✗ 添加 project_id 失败: {e}")
                    # 如果失败，可能是列已存在，继续
            
            if 'record_date' not in columns:
                print("添加 record_date 列...")
                try:
                    db.engine.execute("ALTER TABLE guidance_records ADD COLUMN record_date DATETIME DEFAULT CURRENT_TIMESTAMP")
                    print("  ✓ record_date 添加成功")
                except Exception as e:
                    print(f"  ✗ 添加 record_date 失败: {e}")
            
            if 'teacher_comment' not in columns:
                print("添加 teacher_comment 列...")
                try:
                    db.engine.execute("ALTER TABLE guidance_records ADD COLUMN teacher_comment TEXT")
                    print("  ✓ teacher_comment 添加成功")
                except Exception as e:
                    print(f"  ✗ 添加 teacher_comment 失败: {e}")
            
            if 'status' not in columns:
                print("添加 status 列...")
                try:
                    db.engine.execute("ALTER TABLE guidance_records ADD COLUMN status INT DEFAULT 0")
                    print("  ✓ status 添加成功")
                except Exception as e:
                    print(f"  ✗ 添加 status 失败: {e}")
            
            if 'student_name' not in columns:
                print("添加 student_name 列...")
                try:
                    db.engine.execute("ALTER TABLE guidance_records ADD COLUMN student_name VARCHAR(100)")
                    print("  ✓ student_name 添加成功")
                except Exception as e:
                    print(f"  ✗ 添加 student_name 失败: {e}")
            
            if 'teacher_name' not in columns:
                print("添加 teacher_name 列...")
                try:
                    db.engine.execute("ALTER TABLE guidance_records ADD COLUMN teacher_name VARCHAR(100)")
                    print("  ✓ teacher_name 添加成功")
                except Exception as e:
                    print(f"  ✗ 添加 teacher_name 失败: {e}")
            
            # 2. 如果有旧列，迁移数据
            if 'student_id' in columns and 'teacher_id' in columns:
                print("迁移旧数据...")
                try:
                    # 获取所有旧记录
                    old_records = db.engine.execute("SELECT id, student_id, teacher_id, guidance_date, content FROM guidance_records WHERE project_id IS NULL")
                    
                    migrated_count = 0
                    for record in old_records:
                        record_id, student_id, teacher_id, guidance_date, content = record
                        # 查找对应的项目
                        project = Project.query.filter_by(student_id=student_id, teacher_id=teacher_id).first()
                        if project:
                            # 更新记录
                            update_sql = f"""
                                UPDATE guidance_records 
                                SET project_id = {project.id}
                                WHERE id = {record_id}
                            """
                            if guidance_date:
                                update_sql = update_sql.replace(
                                    "SET project_id",
                                    f"SET project_id = {project.id}, record_date = '{guidance_date}'"
                                )
                            db.engine.execute(update_sql)
                            migrated_count += 1
                            print(f"  ✓ 迁移记录 {record_id}: project_id = {project.id}")
                        else:
                            # 如果找不到项目，使用默认值
                            db.engine.execute(f"UPDATE guidance_records SET project_id = 1 WHERE id = {record_id}")
                            print(f"  ⚠ 记录 {record_id} 找不到对应项目，使用默认 project_id = 1")
                    
                    print(f"数据迁移完成！共迁移 {migrated_count} 条记录")
                except Exception as e:
                    print(f"  ✗ 数据迁移失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 3. 设置 project_id 的默认值（如果还有 NULL 值）
            try:
                null_count = db.engine.execute("SELECT COUNT(*) FROM guidance_records WHERE project_id IS NULL").scalar()
                if null_count > 0:
                    print(f"设置 {null_count} 条记录的默认 project_id...")
                    db.engine.execute("UPDATE guidance_records SET project_id = 1 WHERE project_id IS NULL")
                    print("  ✓ 默认值设置完成")
            except Exception as e:
                print(f"  ✗ 设置默认值失败: {e}")
            
            # 4. 添加外键约束（如果还没有）
            try:
                # 检查外键是否存在
                fk_info = db.engine.execute("""
                    SELECT CONSTRAINT_NAME 
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_NAME = 'guidance_records' 
                    AND COLUMN_NAME = 'project_id'
                    AND TABLE_SCHEMA = DATABASE()
                """).fetchall()
                
                if not fk_info:
                    print("添加 project_id 外键约束...")
                    db.engine.execute("""
                        ALTER TABLE guidance_records 
                        ADD CONSTRAINT fk_guidance_project 
                        FOREIGN KEY (project_id) REFERENCES projects(id)
                    """)
                    print("  ✓ 外键约束添加成功")
                else:
                    print("  ✓ 外键约束已存在")
            except Exception as e:
                print(f"  ⚠ 添加外键约束失败（可能已存在）: {e}")
            
            print("\n迁移完成！")
            
        except Exception as e:
            print(f"迁移过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    migrate_guidance_table()

