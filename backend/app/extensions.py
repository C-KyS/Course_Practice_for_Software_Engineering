from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 初始化数据库实例
db = SQLAlchemy()

# 初始化跨域支持（允许前端访问后端）
cors = CORS()
