import sys
import os

# 将 backend 目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import TaskDocument, GuidanceRecord, Paper, Project

app = create_app()

with app.app_context():
    print("=== Existing Task Documents ===")
    tasks = TaskDocument.query.all()
    for t in tasks:
        print(f"ID: {t.id}, ProjectID: {t.project_id}, StudentSub: {t.student_submitted}, TeacherSub: {t.teacher_submitted}, AdminStatus: {t.admin_status}")

    print("\n=== Existing Guidance Records ===")
    records = GuidanceRecord.query.all()
    for r in records:
        print(f"ID: {r.id}, ProjectID: {r.project_id}, Status: {r.status}, Comment: {r.teacher_comment}")

    print("\n=== Existing Papers ===")
    papers = Paper.query.all()
    for p in papers:
        print(f"ID: {p.id}, StudentID: {p.student_id}, Title: {p.title}, Status: {p.review_status}")
