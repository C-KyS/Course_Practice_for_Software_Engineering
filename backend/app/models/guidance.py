from app.extensions import db
from datetime import datetime

class GuidanceRecord(db.Model):
    __tablename__ = 'guidance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=True) # 指导内容描述或文件路径
    teacher_comment = db.Column(db.Text, nullable=True) # 审查意见
    
    # 状态：0-草稿, 1-已提交给教科办
    status = db.Column(db.Integer, default=0) 
    
    project = db.relationship('app.models.user.Project', backref='guidance_records')

    def to_dict(self):
        return {
            'id': self.id,
            'projectId': self.project_id,
            'studentName': self.project.student.name if self.project and self.project.student else '未知',
            'teacherName': self.project.teacher.name if self.project and self.project.teacher else '未知',
            'date': self.record_date.strftime('%Y-%m-%d'),
            'content': self.content,
            'teacherComment': self.teacher_comment,
            'status': self.status
        }
