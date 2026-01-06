from flask import Blueprint, request, jsonify, send_file, Response
from app.extensions import db
from app.models import GuidanceRecord, Project, User
import os
import io
import uuid
from werkzeug.utils import secure_filename

# 创建蓝图，url_prefix 定义了该模块所有接口的前缀
bp = Blueprint('guidance', __name__, url_prefix='/api/guidance')

# 文件上传配置
UPLOAD_FOLDER = 'uploads/guidance'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """确保上传文件夹存在"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    try:
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

        # content可能是文件路径或文件名
        content = data.get('content')
        # 如果传入了filePath，使用filePath；否则使用content（可能是文件名）
        file_path = data.get('filePath') or content
        
        new_record = GuidanceRecord(
            project_id=project_id,
            content=file_path,  # 保存文件路径
            status=data.get('status', 0), # 默认为0(草稿)
            student_name=data.get('studentName'), # 保存自定义学生姓名
            teacher_name=data.get('teacherName') # 保存自定义教师姓名
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify(new_record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({'error': f'创建记录失败: {error_msg}'}), 500

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
    
    if 'filePath' in data:
        # 如果传入了文件路径，更新content为文件路径
        record.content = data['filePath']
    elif 'content' in data:
        record.content = data['content']
    if 'teacherComment' in data:
        record.teacher_comment = data['teacherComment']
    if 'status' in data:
        record.status = data['status']
    if 'studentName' in data:
        record.student_name = data['studentName']
    if 'teacherName' in data:
        record.teacher_name = data['teacherName']
        
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

@bp.route('/upload', methods=['POST'])
def upload_file():
    """上传指导记录文件"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        ensure_upload_folder()
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 返回文件路径和原始文件名
        return jsonify({
            'filePath': file_path,
            'originalFilename': filename,
            'uniqueFilename': unique_filename
        }), 200
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@bp.route('/records/<int:record_id>/download', methods=['GET'])
def download_record_file(record_id):
    """下载指导记录文件"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    record = GuidanceRecord.query.get_or_404(record_id)
    
    # 权限检查
    if user.role == 'student':
        # 学生只能下载自己课题的记录
        if record.project and record.project.student_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    elif user.role == 'teacher':
        # 教师只能下载自己指导的课题的记录
        if record.project and record.project.teacher_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    # admin可以下载所有记录
    
    if not record.content or record.content == '未上传文件' or record.content == '无内容':
        return jsonify({'error': 'File not found'}), 404
    
    # 获取文件路径
    # content字段存储的是文件路径（完整路径或相对路径）
    file_path = record.content
    
    # 如果content是文件名（不包含路径分隔符），尝试从上传文件夹查找
    if not file_path or ('/' not in file_path and '\\' not in file_path):
        # 查找匹配的文件（可能带有UUID前缀）
        ensure_upload_folder()
        if os.path.exists(UPLOAD_FOLDER) and file_path:
            found = False
            for filename in os.listdir(UPLOAD_FOLDER):
                # 检查文件名是否以原始文件名结尾
                if filename.endswith('_' + file_path) or filename == file_path:
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    found = True
                    break
            if not found:
                # 如果找不到，使用content作为文件名
                file_path = os.path.join(UPLOAD_FOLDER, file_path) if file_path else None
    
    if not file_path:
        return jsonify({'error': 'File path not found'}), 404
    
    # 转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    # 获取原始文件名（从文件路径中提取）
    filename_base = os.path.basename(file_path)
    if '_' in filename_base:
        # 如果文件名包含UUID前缀，提取原始文件名
        parts = filename_base.split('_', 1)
        if len(parts) > 1:
            original_filename = parts[1]
        else:
            original_filename = filename_base
    else:
        original_filename = filename_base
    
    # 根据文件扩展名设置MIME类型
    mimetype = 'application/octet-stream'  # 默认二进制流
    if original_filename.endswith('.docx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif original_filename.endswith('.doc'):
        mimetype = 'application/msword'
    elif original_filename.endswith('.pdf'):
        mimetype = 'application/pdf'
    elif original_filename.endswith('.txt'):
        mimetype = 'text/plain'
    elif original_filename.endswith('.xls'):
        mimetype = 'application/vnd.ms-excel'
    elif original_filename.endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=original_filename  # 保持原始文件名
    )
