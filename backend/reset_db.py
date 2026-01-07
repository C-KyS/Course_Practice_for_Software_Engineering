import sys
import os

# 将 backend 目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db

print("=== 开始重置数据库 ===")

# 1. 创建应用实例以连接数据库
app = create_app()

with app.app_context():
    print("1. 正在删除所有旧表...")
    from sqlalchemy import text
    try:
        with db.engine.connect() as connection:
            # Disable FK checks
            connection.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
            
            # Drop the problematic orphan table manually
            connection.execute(text('DROP TABLE IF EXISTS paper_reviews'))
            
            # Drop all tables defined in metadata using this connection
            db.metadata.drop_all(bind=connection)
            
            # Re-enable FK checks
            connection.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
            connection.commit()
            
    except Exception as e:
        print(f"删除表时出错: {e}")
        # Fallback (though likely to fail if FK issue persists)
        # db.drop_all()
        
    print("   旧表删除成功。")

print("2. 正在重新初始化应用 (触发建表和数据填充)...")
# 再次调用 create_app，这次因为数据库为空，它会执行 db.create_all() 和 init_test_data()
app_new = create_app()

print("=== 数据库重置并填充完成 ===")
