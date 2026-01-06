from app.extensions import db
from datetime import datetime

class GuidanceRecord(db.Model):
    __tablename__ = 'guidance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=True) # 指导内容描述或文件路径
    teacher_comment = db.Column(db.Text, nullable=True) # 审查意见
    
    # 自定义学生姓名和教师姓名（允许与项目关联的不同）
    student_name = db.Column(db.String(100), nullable=True)
    teacher_name = db.Column(db.String(100), nullable=True)
    
    # 状态：0-草稿, 1-已提交给教科办
    status = db.Column(db.Integer, default=0) 
    
    project = db.relationship('app.models.user.Project', backref='guidance_records')

    def to_dict(self):
        # 优先使用自定义的姓名，如果为None则从项目关联获取
        # 注意：空字符串('')被视为有效值，只有None才会回退到项目关联的值
        if self.student_name is not None:
            student_name = self.student_name
        elif self.project and self.project.student:
            student_name = self.project.student.name
        else:
            student_name = '未知'
            
        if self.teacher_name is not None:
            teacher_name = self.teacher_name
        elif self.project and self.project.teacher:
            teacher_name = self.project.teacher.name
        else:
            teacher_name = '未知'
        
        # 处理content：如果是文件路径，提取文件名用于显示
        content_display = self.content
        if self.content and ('/' in self.content or '\\' in self.content):
            # 如果是文件路径，提取文件名
            import os
            filename = os.path.basename(self.content)
            # 如果文件名包含UUID前缀，提取原始文件名
            if '_' in filename:
                parts = filename.split('_', 1)
                if len(parts) > 1:
                    content_display = parts[1]
            else:
                content_display = filename
        
        return {
            'id': self.id,
            'projectId': self.project_id,
            'studentName': student_name,
            'teacherName': teacher_name,
            'date': self.record_date.strftime('%Y-%m-%d'),
            'content': content_display,  # 显示文件名
            'filePath': self.content if (self.content and ('/' in self.content or '\\' in self.content)) else None,  # 保存完整路径
            'teacherComment': self.teacher_comment,
            'status': self.status
        }
