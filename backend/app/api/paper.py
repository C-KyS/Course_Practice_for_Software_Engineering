from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Paper, User

bp = Blueprint('paper', __name__, url_prefix='/api/paper')

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
    """上传论文（仅保存元数据，未处理文件上传）"""
    user = get_current_user()
    data = request.json

    # 权限控制：仅学生可上传
    if not user or user.role != 'student':
        return jsonify({'error': '仅学生可上传论文'}), 403

    new_paper = Paper(
        title=data.get('title'),
        abstract=data.get('abstract'),
        file_path=data.get('filePath'),
        student_id=user.id,
        version=data.get('version'),  # 新增
        review_status='待评审',        # 默认
        review_type=data.get('reviewType'),  # 可选
    )
    db.session.add(new_paper)
    db.session.commit()
    return jsonify(new_paper.to_dict()), 201

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
    db.session.commit()
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