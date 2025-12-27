from app.extensions import db
from datetime import datetime

class TaskDocument(db.Model):
    __tablename__ = 'task_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # 学生初稿文件路径
    student_draft_path = db.Column(db.String(255), nullable=True)
    # 学生是否已提交给教师 (0-未提交, 1-已提交)
    student_submitted = db.Column(db.Integer, default=0)
    
    # 教师修改稿文件路径
    teacher_revision_path = db.Column(db.String(255), nullable=True)
    # 教师是否已提交给教务处 (0-未提交, 1-已提交)
    teacher_submitted = db.Column(db.Integer, default=0)
    
    # 教务处审核状态: None-未审核, 'approved'-通过, 'returned'-退回
    admin_status = db.Column(db.String(20), nullable=True)
    
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('app.models.user.Project', backref='task_documents')

    def to_dict(self):
        return {
            'id': self.id,
            'projectId': self.project_id,
            'studentName': self.project.student.name if self.project and self.project.student else '未知',
            'teacherName': self.project.teacher.name if self.project and self.project.teacher else '未知',
            'studentDraftPath': self.student_draft_path,
            'studentSubmitted': self.student_submitted,
            'teacherRevisionPath': self.teacher_revision_path,
            'teacherSubmitted': self.teacher_submitted,
            'adminStatus': self.admin_status,
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

