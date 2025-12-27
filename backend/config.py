import os

class Config:
    # 使用 SQLite 作为本地数据库，方便演示
    # 实际部署可改为 MySQL: 'mysql+pymysql://user:password@localhost/db_name'
    # basedir = os.path.abspath(os.path.dirname(__file__))
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # MySQL 配置 (请根据实际情况修改 用户名:密码@地址:端口/数据库名)
    # 格式: mysql+pymysql://username:password@host:port/database_name
    
    # 数据库名: graduation_project_db
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Tu.050424@localhost:3306/graduation_project_db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:cyh20041102@localhost:3306/graduation_project_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev-secret-key'
