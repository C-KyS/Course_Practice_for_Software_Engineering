from flask import Blueprint, request, jsonify, send_file
from app.extensions import db
from app.models import Paper, User, Project
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

bp = Blueprint('paper', __name__, url_prefix='/api/paper')

# 文件上传配置
UPLOAD_FOLDER = 'uploads/paper'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """确保上传文件夹存在"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_current_user():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return None
    return User.query.get(user_id)

@bp.route('/list', methods=['GET'])
def list_papers():
    """获取论文列表"""
    user = get_current_user()
    query = Paper.query

    # 权限控制：学生只能看自己的论文，老师可看所有，管理员可看所有
    if user and user.role == 'student':
        query = query.filter(Paper.student_id == user.id)

    papers = query.all()
    return jsonify([p.to_dict() for p in papers])

@bp.route('/upload', methods=['POST'])
def upload_paper():
    """上传论文文件（支持重新提交，覆盖已有记录）"""
    try:
        user = get_current_user()
        if not user or user.role != 'student':
            return jsonify({'error': '仅学生可上传论文'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        ensure_upload_folder()
        
        # 检查是否已有论文记录（用于重新提交）
        existing_paper = Paper.query.filter_by(student_id=user.id).first()
        
        # 如果已有记录，删除旧文件
        if existing_paper and existing_paper.file_path and os.path.exists(existing_paper.file_path):
            try:
                os.remove(existing_paper.file_path)
            except Exception as e:
                print(f"删除旧文件失败: {e}")
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 获取学生关联的项目信息（用于获取课题名称）
        project = Project.query.filter_by(student_id=user.id).first()
        title = project.title if project else filename  # 如果没有项目，使用文件名作为标题
        
        if existing_paper:
            # 更新已有记录（重新提交）
            existing_paper.title = title
            existing_paper.abstract = request.form.get('abstract', '无摘要')
            existing_paper.file_path = file_path
            existing_paper.version = request.form.get('version', '修改稿')  # 重新提交时版本改为"修改稿"
            existing_paper.review_status = '待评审'  # 重新提交后状态重置为待评审
            existing_paper.review_type = None
            existing_paper.reviewer_id = None
            existing_paper.review_comment = None
            existing_paper.modify_comment = None
            existing_paper.score = None
            existing_paper.upload_time = datetime.now()
            db.session.commit()
            return jsonify(existing_paper.to_dict()), 200
        else:
            # 创建新记录
            new_paper = Paper(
                title=title,
                abstract=request.form.get('abstract', '无摘要'),
                file_path=file_path,
                student_id=user.id,
                version=request.form.get('version', '初稿'),
                review_status='待评审',
                review_type=None,
                upload_time=datetime.now()
            )
            db.session.add(new_paper)
            db.session.commit()
            return jsonify(new_paper.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@bp.route('/review/<int:id>', methods=['POST'])
def review_paper(id):
    """教师评审论文"""
    user = get_current_user()
    if not user or user.role != 'teacher':
        return jsonify({'error': '仅教师可评审'}), 403
    paper = Paper.query.get_or_404(id)
    data = request.json
    paper.review_status = data.get('reviewStatus', '已评审')
    paper.review_type = data.get('reviewType', '一审')
    paper.reviewer_id = user.id
    paper.review_comment = data.get('reviewComment')
    paper.modify_comment = data.get('modifyComment')
    paper.score = data.get('score')
    db.session.commit()
    return jsonify(paper.to_dict())

@bp.route('/<int:id>', methods=['GET'])
def get_paper(id):
    """获取单个论文详情"""
    paper = Paper.query.get_or_404(id)
    return jsonify(paper.to_dict())

@bp.route('/delete', methods=['POST'])
def delete_papers():
    """批量删除论文"""
    data = request.json
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'message': 'No ids provided'}), 400
    Paper.query.filter(Paper.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200

@bp.route('/<int:id>', methods=['PUT'])
def update_paper(id):
    """修改论文信息"""
    paper = Paper.query.get_or_404(id)
    data = request.json

    if 'title' in data:
        paper.title = data['title']
    if 'abstract' in data:
        paper.abstract = data['abstract']
    if 'filePath' in data:
        paper.file_path = data['filePath']

    db.session.commit()
    return jsonify(paper.to_dict())

@bp.route('/download/<int:id>', methods=['GET'])
def download_paper(id):
    """下载论文文件"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    paper = Paper.query.get_or_404(id)
    
    # 权限检查：学生只能下载自己的论文，教师和管理员可以下载所有论文
    if user.role == 'student':
        if paper.student_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    # teacher 和 admin 角色可以下载所有论文，无需额外检查
    
    if not paper.file_path:
        return jsonify({'error': 'File not found'}), 404
    
    # 转换为绝对路径
    file_path = paper.file_path
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    # 获取原始文件名
    original_filename = os.path.basename(paper.file_path)
    if '_' in original_filename:
        parts = original_filename.split('_', 1)
        if len(parts) > 1:
            original_filename = parts[1]
    
    # 根据文件扩展名确定MIME类型
    file_ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
    mimetype_map = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    mimetype = mimetype_map.get(file_ext, 'application/octet-stream')
    
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=original_filename
    )