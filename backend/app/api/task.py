from flask import Blueprint, request, jsonify, send_file
from app.extensions import db
from app.models import TaskDocument, Project, User
import os
import uuid
from werkzeug.utils import secure_filename

# 创建蓝图
bp = Blueprint('task', __name__, url_prefix='/api/task')

# 模拟当前登录用户
def get_current_user():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return None
    return User.query.get(user_id)

# 文件上传配置
UPLOAD_FOLDER = 'uploads/task'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """确保上传文件夹存在"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/upload', methods=['POST'])
def upload_file():
    """上传文件（学生初稿或教师修改稿）"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        file_type = request.form.get('fileType')  # 'student_draft' 或 'teacher_revision'
        project_id = request.form.get('projectId')
        
        # 处理project_id，如果是字符串"null"或空字符串，设为None
        if project_id and project_id.strip() and project_id != 'null':
            try:
                project_id = int(project_id)
            except:
                project_id = None
        else:
            project_id = None
        
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
        
        # 确保目录存在（UPLOAD_FOLDER已经通过ensure_upload_folder()创建）
        file.save(file_path)
        
        # 获取或创建任务书记录
        project = None
        if project_id:
            project = Project.query.get(project_id)
            if not project:
                # 如果文件已保存，删除它
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                return jsonify({'error': 'Project not found'}), 404
            task_doc = TaskDocument.query.filter_by(project_id=project_id).first()
        else:
            # 如果没有project_id，尝试根据用户查找
            if user.role == 'student':
                project = Project.query.filter_by(student_id=user.id).first()
            elif user.role == 'teacher':
                project = Project.query.filter_by(teacher_id=user.id).first()
            else:
                # 如果文件已保存，删除它
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                return jsonify({'error': 'Invalid user role'}), 400
            
            if not project:
                # 如果文件已保存，删除它
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                return jsonify({'error': 'Project not found'}), 404
            
            task_doc = TaskDocument.query.filter_by(project_id=project.id).first()
        
        if not task_doc:
            # 创建新记录
            task_doc = TaskDocument(project_id=project.id)
            db.session.add(task_doc)
        
        # 更新文件路径
        if file_type == 'student_draft':
            # 删除旧文件（如果存在）
            if task_doc.student_draft_path and os.path.exists(task_doc.student_draft_path):
                try:
                    os.remove(task_doc.student_draft_path)
                except:
                    pass
            task_doc.student_draft_path = file_path
        elif file_type == 'teacher_revision':
            # 删除旧文件（如果存在）
            if task_doc.teacher_revision_path and os.path.exists(task_doc.teacher_revision_path):
                try:
                    os.remove(task_doc.teacher_revision_path)
                except:
                    pass
            task_doc.teacher_revision_path = file_path
        else:
            # 如果文件已保存，删除它
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            return jsonify({'error': 'Invalid file type'}), 400
        
        db.session.commit()
        return jsonify(task_doc.to_dict()), 200
    except Exception as e:
        # 记录错误并返回JSON错误响应
        import traceback
        print(f"Upload error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@bp.route('/info', methods=['GET'])
def get_task_info():
    """获取任务书信息"""
    user = get_current_user()
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 根据用户角色查找项目
    if user.role == 'student':
        project = Project.query.filter_by(student_id=user.id).first()
    elif user.role == 'teacher':
        project = Project.query.filter_by(teacher_id=user.id).first()
    else:
        # admin可以查看所有
        project = Project.query.first()
    
    if not project:
        return jsonify({
            'projectId': None,
            'studentDraftPath': None,
            'studentSubmitted': 0,
            'teacherRevisionPath': None,
            'teacherSubmitted': 0,
            'adminStatus': None
        })
    
    task_doc = TaskDocument.query.filter_by(project_id=project.id).first()
    
    if not task_doc:
        return jsonify({
            'projectId': project.id,
            'studentDraftPath': None,
            'studentSubmitted': 0,
            'teacherRevisionPath': None,
            'teacherSubmitted': 0,
            'adminStatus': None
        })
    
    return jsonify(task_doc.to_dict())

@bp.route('/submit', methods=['POST'])
def submit_task():
    """提交任务书（学生提交给教师，或教师提交给教务处）"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    submit_type = data.get('submitType')  # 'student' 或 'teacher'
    project_id = data.get('projectId')
    
    # 查找项目
    if project_id:
        project = Project.query.get(project_id)
    else:
        if user.role == 'student':
            project = Project.query.filter_by(student_id=user.id).first()
        elif user.role == 'teacher':
            project = Project.query.filter_by(teacher_id=user.id).first()
        else:
            return jsonify({'error': 'Invalid user role'}), 400
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    task_doc = TaskDocument.query.filter_by(project_id=project.id).first()
    
    if not task_doc:
        return jsonify({'error': 'Task document not found'}), 404
    
    # 检查是否已通过，如果已通过则不允许再提交
    if task_doc.admin_status == 'approved':
        return jsonify({'error': 'Task document already approved, cannot resubmit'}), 400
    
    if submit_type == 'student':
        # 学生提交给教师
        if user.role != 'student':
            return jsonify({'error': 'Only students can submit drafts'}), 403
        
        if not task_doc.student_draft_path:
            return jsonify({'error': 'No draft file uploaded'}), 400
        
        task_doc.student_submitted = 1
    elif submit_type == 'teacher':
        # 教师提交给教务处
        if user.role != 'teacher':
            return jsonify({'error': 'Only teachers can submit revisions'}), 403
        
        if not task_doc.teacher_revision_path:
            return jsonify({'error': 'No revision file uploaded'}), 400
        
        if task_doc.student_submitted != 1:
            return jsonify({'error': 'Student draft not submitted yet'}), 400
        
        # 如果被退回，允许重新提交
        task_doc.teacher_submitted = 1
        # 重新提交后，不清除退回状态，保留'returned'标记，但实际状态变为待审核
        # 这样前端可以通过admin_status='returned'来判断是否曾经被退回过
        # 如果admin_status='returned'但teacher_submitted=1，说明是退回后重新提交的
    else:
        return jsonify({'error': 'Invalid submit type'}), 400
    
    db.session.commit()
    return jsonify(task_doc.to_dict()), 200

@bp.route('/list', methods=['GET'])
def get_task_list():
    """获取任务书列表（教务处用）"""
    user = get_current_user()
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 返回所有记录（包括通过、退回和待审核的），只有主动删除的记录才不显示
    # 条件：曾经提交过（teacher_submitted曾经为1）或者当前状态不为None
    task_docs = TaskDocument.query.filter(
        (TaskDocument.teacher_submitted == 1) | 
        (TaskDocument.admin_status != None)
    ).all()
    return jsonify([td.to_dict() for td in task_docs])

@bp.route('/review', methods=['POST'])
def review_task():
    """教务处审核任务书（通过或退回）"""
    user = get_current_user()
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    task_id = data.get('taskId')
    action = data.get('action')  # 'approve' 或 'return'
    
    task_doc = TaskDocument.query.get_or_404(task_id)
    
    if task_doc.teacher_submitted != 1:
        return jsonify({'error': 'Task not submitted by teacher yet'}), 400
    
    if action == 'approve':
        task_doc.admin_status = 'approved'
    elif action == 'return':
        # 退回时重置状态，允许重新提交
        task_doc.admin_status = 'returned'
        task_doc.student_submitted = 0
        task_doc.teacher_submitted = 0
        # 注意：不删除文件路径，保留已上传的文件，但允许重新上传覆盖
        # 标记曾经被退回过（通过保留admin_status='returned'来标记）
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    db.session.commit()
    return jsonify(task_doc.to_dict()), 200

@bp.route('/delete-file', methods=['POST'])
def delete_file():
    """删除文件（学生或教师删除已上传的文件）"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    file_type = data.get('fileType')  # 'student_draft' 或 'teacher_revision'
    project_id = data.get('projectId')
    
    # 查找项目
    if project_id:
        project = Project.query.get(project_id)
    else:
        if user.role == 'student':
            project = Project.query.filter_by(student_id=user.id).first()
        elif user.role == 'teacher':
            project = Project.query.filter_by(teacher_id=user.id).first()
        else:
            return jsonify({'error': 'Invalid user role'}), 400
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    task_doc = TaskDocument.query.filter_by(project_id=project.id).first()
    
    if not task_doc:
        return jsonify({'error': 'Task document not found'}), 404
    
    # 权限检查
    if user.role == 'student' and file_type != 'student_draft':
        return jsonify({'error': 'Unauthorized'}), 403
    if user.role == 'teacher' and file_type != 'teacher_revision':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # 检查是否已提交，已提交的不能删除（除非被退回）
    if file_type == 'student_draft' and task_doc.student_submitted == 1 and task_doc.admin_status != 'returned':
        return jsonify({'error': 'Cannot delete submitted file'}), 400
    if file_type == 'teacher_revision' and task_doc.teacher_submitted == 1 and task_doc.admin_status != 'returned':
        return jsonify({'error': 'Cannot delete submitted file'}), 400
    
    # 删除文件
    file_path = None
    if file_type == 'student_draft':
        file_path = task_doc.student_draft_path
        task_doc.student_draft_path = None
    elif file_type == 'teacher_revision':
        file_path = task_doc.teacher_revision_path
        task_doc.teacher_revision_path = None
    
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass
    
    db.session.commit()
    return jsonify(task_doc.to_dict()), 200

@bp.route('/delete', methods=['DELETE'])
def delete_task():
    """删除任务书记录（教务处用）"""
    user = get_current_user()
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    task_id = data.get('taskId')
    
    task_doc = TaskDocument.query.get_or_404(task_id)
    
    # 删除文件
    if task_doc.student_draft_path and os.path.exists(task_doc.student_draft_path):
        try:
            os.remove(task_doc.student_draft_path)
        except:
            pass
    
    if task_doc.teacher_revision_path and os.path.exists(task_doc.teacher_revision_path):
        try:
            os.remove(task_doc.teacher_revision_path)
        except:
            pass
    
    # 重置所有状态，而不是删除记录，让业务重新开始
    task_doc.student_draft_path = None
    task_doc.student_submitted = 0
    task_doc.teacher_revision_path = None
    task_doc.teacher_submitted = 0
    task_doc.admin_status = None
    
    db.session.commit()
    
    return jsonify(task_doc.to_dict()), 200

@bp.route('/download/<int:task_id>', methods=['GET'])
def download_file(task_id):
    """下载文件"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    task_doc = TaskDocument.query.get_or_404(task_id)
    file_type = request.args.get('type')  # 'student_draft' 或 'teacher_revision'
    
    file_path = None
    if file_type == 'student_draft':
        file_path = task_doc.student_draft_path
    elif file_type == 'teacher_revision':
        file_path = task_doc.teacher_revision_path
    
    if not file_path:
        return jsonify({'error': 'File not found'}), 404
    
    # 转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    # 权限检查
    project = Project.query.get(task_doc.project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if user.role == 'student':
        # 学生可以下载自己的初稿和教师的修改稿
        if project.student_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        # 学生可以下载两种类型的文件
    elif user.role == 'teacher':
        # 教师可以下载学生的初稿和自己的修改稿
        if project.teacher_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        # 教师可以下载两种类型的文件
    # admin可以下载所有文件
    
    # 获取原始文件名
    original_filename = os.path.basename(file_path)
    # 移除UUID前缀
    if '_' in original_filename:
        original_filename = '_'.join(original_filename.split('_')[1:])
    
    return send_file(file_path, as_attachment=True, download_name=original_filename)

