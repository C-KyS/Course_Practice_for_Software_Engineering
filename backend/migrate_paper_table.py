"""
迁移脚本：更新 papers 表结构
添加缺失的列：version, review_status, review_type, reviewer_id, review_comment, modify_comment, score
"""
from app import create_app
from app.extensions import db
from config import Config
from sqlalchemy import text

def migrate_paper_table():
    """迁移论文表结构"""
    app = create_app(Config)
    
    with app.app_context():
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'papers' not in tables:
            print("papers 表不存在，创建新表...")
            db.create_all()
            print("表创建完成！")
            return
        
        # 检查列是否存在
        columns = [col['name'] for col in inspector.get_columns('papers')]
        
        # 需要添加的列及其类型
        columns_to_add = [
            ('version', 'VARCHAR(32)'),
            ('review_status', 'VARCHAR(32)'),
            ('review_type', 'VARCHAR(32)'),
            ('reviewer_id', 'INTEGER'),
            ('review_comment', 'TEXT'),
            ('modify_comment', 'TEXT'),
            ('score', 'FLOAT')
        ]
        
        with db.engine.connect() as conn:
            for col_name, col_type in columns_to_add:
                if col_name not in columns:
                    print(f"正在添加列 {col_name}...")
                    try:
                        conn.execute(text(f"ALTER TABLE papers ADD COLUMN {col_name} {col_type}"))
                        print(f"列 {col_name} 添加成功")
                    except Exception as e:
                        print(f"添加列 {col_name} 失败: {str(e)}")
            
            conn.commit()
        
        print("迁移完成！")

if __name__ == '__main__':
    migrate_paper_table()
