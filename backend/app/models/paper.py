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
    version = db.Column(db.String(32))  # 论文版本，如“初稿”“修改稿”
    review_status = db.Column(db.String(32))  # 评审状态，如“待评审”“已评审”
    review_type = db.Column(db.String(32))  # 评审类型，如“一审”“二审”
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 评审人
    review_comment = db.Column(db.Text)  # 评审意见
    modify_comment = db.Column(db.Text)  # 修改意见

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'uploadTime': self.upload_time.strftime('%Y-%m-%d %H:%M:%S') if self.upload_time else None,
            'filePath': self.file_path,
            'studentId': self.student_id,
            'version': self.version,
            'reviewStatus': self.review_status,
            'reviewType': self.review_type,
            'reviewerId': self.reviewer_id,
            'reviewComment': self.review_comment,
            'modifyComment': self.modify_comment
        }