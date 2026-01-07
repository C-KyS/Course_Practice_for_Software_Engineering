import sys
import os

# 将 backend 目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"{'ID':<5} {'Username':<15} {'Name':<15} {'Role':<10}")
    print("-" * 50)
    for user in users:
        print(f"{user.id:<5} {user.username:<15} {user.name:<15} {user.role:<10}")
