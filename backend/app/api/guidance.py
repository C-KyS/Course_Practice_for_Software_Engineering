from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import GuidanceRecord, Project, User

# 创建蓝图，url_prefix 定义了该模块所有接口的前缀
bp = Blueprint('guidance', __name__, url_prefix='/api/guidance')

# 模拟当前登录用户 (实际项目中应从 Session/Token 获取)
# 为了演示方便，我们假设请求头中包含 'X-User-Id'
def get_current_user():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return None
    return User.query.get(user_id)

@bp.route('/records', methods=['GET'])
def get_records():
    """获取指导记录列表"""
    user = get_current_user()
    
    # 如果没有用户，返回所有记录（用于演示）
    if not user:
        records = GuidanceRecord.query.all()
        return jsonify([r.to_dict() for r in records])

    query = GuidanceRecord.query.join(Project)

    # 权限控制逻辑
    if user.role == 'student':
        # 学生只能看自己课题的记录
        query = query.filter(Project.student_id == user.id)
    elif user.role == 'teacher':
        # 老师看自己指导的课题
        query = query.filter(Project.teacher_id == user.id)
    elif user.role == 'admin':
        # 教科办只能看到已提交的记录（status=1）
        query = query.filter(GuidanceRecord.status == 1)

    records = query.all()
    return jsonify([r.to_dict() for r in records])

@bp.route('/records', methods=['POST'])
def create_record():
    """新增指导记录"""
    user = get_current_user()
    # 临时允许无用户操作，方便演示
    # if not user:
    #     return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    
    # 如果是学生，自动关联到自己的课题
    project_id = data.get('projectId')
    
    # 临时逻辑：如果前端传了 projectId 就用，否则尝试查找
    if user and user.role == 'student' and not project_id:
        project = Project.query.filter_by(student_id=user.id).first()
        if project:
            project_id = project.id

    # 如果还是没有 projectId，为了演示不报错，可以给一个默认值或者报错
    if not project_id:
        # return jsonify({'error': 'No project found'}), 400
        project_id = 1 # 假设有一个默认课题

    new_record = GuidanceRecord(
        project_id=project_id,
        content=data.get('content'), 
        status=data.get('status', 0) # 默认为0(草稿)
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify(new_record.to_dict()), 201

@bp.route('/records', methods=['DELETE'])
def delete_records():
    """批量删除指导记录"""
    data = request.json
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'message': 'No ids provided'}), 400
        
    GuidanceRecord.query.filter(GuidanceRecord.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200

@bp.route('/records/<int:id>', methods=['PUT'])
def update_record(id):
    """修改指导记录 (包括老师填写意见)"""
    record = GuidanceRecord.query.get_or_404(id)
    data = request.json
    
    if 'content' in data:
        record.content = data['content']
    if 'teacherComment' in data:
        record.teacher_comment = data['teacherComment']
    if 'status' in data:
        record.status = data['status']
        
    db.session.commit()
    return jsonify(record.to_dict())

@bp.route('/info', methods=['GET'])
def get_student_info():
    """获取当前用户的课题基本信息 (用于模块顶部显示)"""
    user = get_current_user()
    
    # 如果没有用户，返回默认项目信息（用于演示）
    if not user:
        project = Project.query.first()
        if project:
            return jsonify(project.to_dict())
        return jsonify({
            'id': 1,
            'studentName': '图图',
            'teacherName': 'David',
            'title': '基于深度学习的图像识别系统研究'
        })
        
    # 简单逻辑：如果是学生，返回自己的课题；如果是老师，返回第一个指导的课题(演示用)
    project = None
    if user.role == 'student':
        project = Project.query.filter_by(student_id=user.id).first()
    elif user.role == 'teacher':
        project = Project.query.filter_by(teacher_id=user.id).first()
    
    # 如果找不到项目，返回默认值
    if project:
        return jsonify(project.to_dict())
    else:
        # 返回第一个项目或默认值
        default_project = Project.query.first()
        if default_project:
            return jsonify(default_project.to_dict())
        return jsonify({
            'id': 1,
            'studentName': '图图',
            'teacherName': 'David',
            'title': '基于深度学习的图像识别系统研究'
        })
