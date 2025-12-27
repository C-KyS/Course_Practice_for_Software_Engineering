from flask import Flask, send_from_directory
from app.extensions import db, cors
from config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    cors.init_app(app)

    # 注册蓝图 (模块化路由)
    from app.api import guidance
    app.register_blueprint(guidance.bp)
    
    from app.api import paper
    app.register_blueprint(paper.bp)
    
    from app.api import task
    app.register_blueprint(task.bp)

    # 创建数据库表 (仅用于开发环境快速初始化)
    with app.app_context():
        # 检查并修复任务书表结构
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'task_documents' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('task_documents')]
                if 'project_id' not in columns:
                    # 删除旧表，让Flask重新创建
                    print("检测到旧的任务书表结构，删除旧表以重新创建...")
                    db.session.execute(text("DROP TABLE IF EXISTS task_documents"))
                    db.session.commit()
                    print("旧表已删除，将重新创建")
        except Exception as e:
            print(f"检查表结构时出错: {e}")
            db.session.rollback()
        
        db.create_all()
        # 初始化测试数据
        init_test_data()

# --- 新增代码：配置前端静态文件路径 ---
    # 逻辑：当前文件(__init__.py) -> app目录 -> backend目录 -> 项目根目录 -> frontend目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(current_dir, '..', '..', 'frontend')
    frontend_dir = os.path.abspath(frontend_dir)

    @app.route('/')
    def index():
        # 访问根路径 http://127.0.0.1:8080/ 时，返回 index.html
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        # 访问 http://127.0.0.1:8080/styles.css 等资源时，从 frontend 目录寻找
        return send_from_directory(frontend_dir, filename)
    # --- 新增代码结束 ---

    return app

def init_test_data():
    """初始化一些测试数据，避免数据库为空"""
    from app.models import User, Project, GuidanceRecord, Paper
    
    if User.query.first():
        return

    # 创建用户
    student = User(username='202101001', name='图图', role='student')
    teacher = User(username='T1001', name='David', role='teacher')
    admin = User(username='admin', name='教科办', role='admin')
    
    db.session.add_all([student, teacher, admin])
    db.session.commit()
    
    # 创建课题
    project = Project(title='基于深度学习的图像识别系统研究', student=student, teacher=teacher)
    db.session.add(project)
    db.session.commit()
    
    # 创建一条指导记录 (已注释，保持初始为空)
    # record = GuidanceRecord(project=project, content='第一次指导记录内容', teacher_comment='同意开题')
    # db.session.add(record)
    # db.session.commit()

    # 记得创建一条论文管理记录
