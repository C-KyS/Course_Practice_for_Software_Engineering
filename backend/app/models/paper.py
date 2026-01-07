from app.extensions import db
from datetime import datetime

class Paper(db.Model):
    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    abstract = db.Column(db.Text)
    upload_time = db.Column(db.DateTime)
    file_path = db.Column(db.String(256))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    version = db.Column(db.String(32))  # 论文版本，如"初稿""修改稿"
    review_status = db.Column(db.String(32))  # 评审状态，如"待评审""已评审"
    review_type = db.Column(db.String(32))  # 评审类型，如"一审""二审"
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 评审人
    review_comment = db.Column(db.Text)  # 评审意见
    modify_comment = db.Column(db.Text)  # 修改意见
    score = db.Column(db.Float)  # 成绩

    student = db.relationship('User', foreign_keys=[student_id])

    def to_dict(self):
        # 获取学生关联的项目信息（用于获取指导教师）
        teacher_name = None
        if self.student:
            from app.models import Project
            project = Project.query.filter_by(student_id=self.student.id).first()
            if project and project.teacher:
                teacher_name = project.teacher.name
        
        # 提取原始文件名（去除UUID前缀和路径）
        original_filename = None
        if self.file_path:
            import os
            filename = os.path.basename(self.file_path)
            # 如果文件名包含UUID前缀（格式：uuid_filename.ext），提取原始文件名
            if '_' in filename:
                parts = filename.split('_', 1)
                if len(parts) > 1:
                    original_filename = parts[1]
                else:
                    original_filename = filename
            else:
                original_filename = filename
        
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'uploadTime': self.upload_time.strftime('%Y-%m-%d %H:%M:%S') if self.upload_time else None,
            'filePath': self.file_path,
            'fileName': original_filename,  # 添加原始文件名字段
            'studentId': self.student_id,
            'studentName': self.student.name if self.student else None,
            'teacherName': teacher_name,
            'version': self.version,
            'reviewStatus': self.review_status,
            'reviewType': self.review_type,
            'reviewerId': self.reviewer_id,
            'reviewComment': self.review_comment,
            'modifyComment': self.modify_comment,
            'score': self.score
        }