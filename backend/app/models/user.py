from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False) # 学号/工号
    name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), nullable=False) # student, teacher, admin
    
    # 关系：一个学生有一个课题，一个老师指导多个课题
    # 这里简化处理，具体关系在 Project 表体现

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'role': self.role
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    student = db.relationship('User', foreign_keys=[student_id], backref='student_project')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='teacher_projects')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'studentName': self.student.name if self.student else '',
            'teacherName': self.teacher.name if self.teacher else ''
        }
