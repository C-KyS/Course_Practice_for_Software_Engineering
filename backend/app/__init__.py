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
        
        # 检查并修复指导记录表结构
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'guidance_records' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('guidance_records')]
                missing_columns = []
                
                # 检查必需的列
                required_columns = {
                    'project_id': 'INT',
                    'record_date': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                    'teacher_comment': 'TEXT',
                    'status': 'INT DEFAULT 0',
                    'student_name': 'VARCHAR(100)',
                    'teacher_name': 'VARCHAR(100)'
                }
                
                for col_name, col_def in required_columns.items():
                    if col_name not in columns:
                        missing_columns.append((col_name, col_def))
                
                if missing_columns:
                    print(f"检测到指导记录表缺少列，正在添加: {[col[0] for col in missing_columns]}")
                    for col_name, col_def in missing_columns:
                        try:
                            db.session.execute(text(f"ALTER TABLE guidance_records ADD COLUMN {col_name} {col_def}"))
                            print(f"  ✓ 添加列 {col_name} 成功")
                        except Exception as e:
                            print(f"  ✗ 添加列 {col_name} 失败: {e}")
                    
                    db.session.commit()
                    print("指导记录表结构更新完成")
        except Exception as e:
            print(f"检查指导记录表结构时出错: {e}")
            db.session.rollback()
        
        # 检查并修复论文表结构
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'papers' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('papers')]
                missing_columns = []
                
                # 检查必需的列
                required_columns = {
                    'title': 'VARCHAR(128)',
                    'abstract': 'TEXT',
                    'upload_time': 'DATETIME',
                    'review_status': 'VARCHAR(32)',
                    'review_type': 'VARCHAR(32)',
                    'reviewer_id': 'INT',
                    'review_comment': 'TEXT',
                    'modify_comment': 'TEXT',
                    'score': 'FLOAT'
                }
                
                for col_name, col_def in required_columns.items():
                    if col_name not in columns:
                        missing_columns.append((col_name, col_def))
                
                if missing_columns:
                    print(f"检测到论文表缺少列，正在添加: {[col[0] for col in missing_columns]}")
                    for col_name, col_def in missing_columns:
                        try:
                            # 对于外键列，先添加列，再添加外键约束
                            if col_name == 'reviewer_id':
                                db.session.execute(text(f"ALTER TABLE papers ADD COLUMN {col_name} {col_def}"))
                                try:
                                    db.session.execute(text(f"ALTER TABLE papers ADD FOREIGN KEY ({col_name}) REFERENCES users(id)"))
                                except:
                                    pass  # 外键可能已存在
                            else:
                                db.session.execute(text(f"ALTER TABLE papers ADD COLUMN {col_name} {col_def}"))
                            print(f"  ✓ 添加列 {col_name} 成功")
                        except Exception as e:
                            print(f"  ✗ 添加列 {col_name} 失败: {e}")
                    
                    db.session.commit()
                    print("论文表结构更新完成")
        except Exception as e:
            print(f"检查论文表结构时出错: {e}")
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
    from app.models import User, Project, GuidanceRecord, Paper, TaskDocument
    from datetime import datetime, timedelta
    
    if User.query.first():
        return

    print("正在初始化测试数据...")

    # 1. 创建用户
    # 学生
    s1 = User(username='202101001', name='图图', role='student')
    s2 = User(username='202101002', name='张三', role='student')
    s3 = User(username='202101003', name='李四', role='student')
    # 教师
    t1 = User(username='T1001', name='David', role='teacher')
    t2 = User(username='T1002', name='王老师', role='teacher')
    # 管理员
    admin = User(username='admin', name='教科办', role='admin')
    
    db.session.add_all([s1, s2, s3, t1, t2, admin])
    db.session.commit()
    
    # 2. 创建课题
    p1 = Project(title='基于深度学习的图像识别系统研究', student=s1, teacher=t1)
    p2 = Project(title='企业级SaaS平台架构设计', student=s2, teacher=t2)
    p3 = Project(title='物联网在智能家居中的应用', student=s3, teacher=t1)
    
    db.session.add_all([p1, p2, p3])
    db.session.commit()

    # 3. 创建任务书数据 (Task Documents)
    # 场景1：项目1 (图图) - 流程完全结束，教务处已通过
    td1 = TaskDocument(
        project_id=p1.id,
        student_draft_path='uploads/task/task_draft_student1.pdf',
        student_submitted=1,
        teacher_revision_path='uploads/task/task_revised_teacher1.pdf',
        teacher_submitted=1,
        admin_status='approved',
        updated_at=datetime.now()
    )

    # 场景2：项目2 (张三) - 学生已提交，等待教师审核
    td2 = TaskDocument(
        project_id=p2.id,
        student_draft_path='uploads/task/task_draft_student2.pdf',
        student_submitted=1,
        teacher_revision_path=None,
        teacher_submitted=0,
        admin_status=None,
        updated_at=datetime.now()
    )

    # 场景3：项目3 (李四) - 教师已提交，但被教务处退回
    td3 = TaskDocument(
        project_id=p3.id,
        student_draft_path='uploads/task/task_draft_student3.pdf',
        student_submitted=1,
        teacher_revision_path='uploads/task/task_revised_teacher3.pdf',
        teacher_submitted=1,
        admin_status='returned',
        updated_at=datetime.now()
    )
    db.session.add_all([td1, td2, td3])

    # 4. 创建指导记录数据 (Guidance Records)
    # 项目1 (图图)
    gr1 = GuidanceRecord(
        project_id=p1.id,
        record_date=datetime(2025, 11, 1, 10, 0, 0),
        content='讨论毕业设计选题的可行性与初期规划',
        teacher_comment='通过',
        student_name='图图',
        teacher_name='David',
        status=1
    )
    gr2 = GuidanceRecord(
        project_id=p1.id,
        record_date=datetime(2025, 12, 15, 14, 30, 0),
        content='检查系统需求分析文档，提出修改建议',
        teacher_comment='通过',
        student_name='图图',
        teacher_name='David',
        status=1
    )

    # 项目2 (张三)
    gr3 = GuidanceRecord(
        project_id=p2.id,
        record_date=datetime(2025, 11, 5, 9, 0, 0),
        content='确定SaaS平台的总体架构',
        teacher_comment='通过',
        student_name='张三',
        teacher_name='王老师',
        status=1
    )
    gr4 = GuidanceRecord(
        project_id=p2.id,
        record_date=datetime(2026, 1, 5, 16, 0, 0),
        content='中期进度汇报，目前进度之后',
        teacher_comment='不通过',
        student_name='张三',
        teacher_name='王老师',
        status=1
    )

    # 项目3 (李四)
    gr5 = GuidanceRecord(
        project_id=p3.id,
        record_date=datetime(2026, 1, 2, 11, 0, 0),
        content='物联网硬件选型讨论',
        teacher_comment=None,
        student_name='李四',
        teacher_name='David',
        status=0
    )
    db.session.add_all([gr1, gr2, gr3, gr4, gr5])
    
    # 5. 创建论文数据 (模拟不同状态)
    
    # Case 1: 图图 - 已提交，已评审 (高分)
    paper1 = Paper(
        title='基于深度学习的图像识别系统研究',
        abstract='本文提出了一种新的基于CNN的图像识别算法...',
        file_path='图图_论文初稿.pdf',
        student_id=s1.id,
        version='初稿',
        review_status='已评审',
        review_type='一审',
        reviewer_id=t1.id,
        review_comment='论文结构完整，实验数据详实，创新点突出。建议在引言部分增加更多相关工作的对比。',
        modify_comment='请修改参考文献格式。',
        score=92.5,
        upload_time=datetime.now()
    )
    
    # Case 2: 张三 - 已提交，待评审
    paper2 = Paper(
        title='企业级SaaS平台架构设计与实现',
        abstract='本文探讨了多租户SaaS平台的数据库设计与性能优化...',
        file_path='uploads/paper/paper_student2_v1.pdf',
        student_id=s2.id,
        version='初稿',
        review_status='待评审',
        review_type=None,
        upload_time=datetime.now()
    )
    
    # Case 3: 李四 - 论文已评审，分数较低，需要二审
    paper3 = Paper(
        title='基于MQTT的智能家居控制系统',
        abstract='本系统实现了基于MQTT协议的轻量级智能家居控制...',
        file_path='uploads/paper/paper_student3_v1.pdf',
        student_id=s3.id,
        version='初稿',
        review_status='已评审',
        review_type='一审',
        reviewer_id=t1.id,
        review_comment='整体架构可以，但硬件测试数据不充分，建议补充实验章节。',
        modify_comment='需补充第三章实验数据',
        score=68.5,
        upload_time=datetime(2025, 12, 20, 9, 0, 0)
    )
    
    db.session.add_all([paper1, paper2, paper3])
    db.session.commit()

    print("测试数据初始化完成！")
