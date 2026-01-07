# 毕业设计管理系统 (Graduation Project Management System)

这是一个基于 Web 的毕业设计全流程管理系统，旨在简化学生、教师和教务办在毕业设计过程中的交互与管理。

## 功能模块

系统包含以下核心模块：

1.  **选题管理**：学生选题、教师确认。
2.  **任务书管理**：任务书下达、审核与查看。
3.  **指导记录**：学生提交指导记录，教师批阅。
4.  **论文管理**：
    *   **学生**：上传论文初稿/终稿，查看评审意见。
    *   **教师**：在线评审论文，打分并提出修改意见。
    *   **教务办**：汇总查询论文，导出数据。
5.  **答辩管理**：(开发中) 答辩安排与成绩录入。
6.  **归档管理**：(开发中) 最终材料归档。

## 技术栈

*   **前端**: HTML5, CSS3 (Apple Design 风格), Vanilla JavaScript (原生 JS)
*   **后端**: Python 3, Flask 框架
*   **数据库**: SQLite (通过 SQLAlchemy ORM 管理)

## 快速开始

### 1. 环境准备

确保您的系统中已安装 Python 3.8 或更高版本。

### 2. 安装依赖

在项目根目录下打开终端，运行以下命令安装后端依赖：

```bash
pip install -r backend/requirements.txt
```

### 3. 运行系统

在项目根目录下，运行启动脚本：

```bash
python backend/run.py
```

或者：

```bash
python3 backend/run.py
```

*注意：首次运行时，系统会自动初始化 SQLite 数据库并填充测试数据（包含默认的学生、教师和管理员账号）。*

### 4. 访问系统

打开浏览器，访问以下地址：

http://127.0.0.1:8080

### 5. 默认测试账号

系统内置了角色切换功能（模拟登录），您可以在页面右上角或通过修改 Header 进行测试。默认初始化的用户如下：

*   **学生**: 图图 (ID: 1)
*   **教师**: David (ID: 2)
*   **管理员**: 教科办 (ID: 3)

*注：当前版本前端通过 `localStorage` 和请求头 `X-User-Id` 模拟身份切换，生产环境需替换为正式的登录鉴权模块。*

## 项目结构

```
.
├── backend/                # 后端代码
│   ├── app/                # 应用核心逻辑
│   │   ├── api/            # API 接口 (guidance, paper, task)
│   │   ├── models/         # 数据库模型
│   │   ├── extensions.py   # Flask 扩展初始化
│   │   └── __init__.py     # App 工厂函数与路由配置
│   ├── SQL/                # SQL 脚本 (建表、迁移)
│   ├── uploads/            # 文件上传存储目录 (按模块分类)
│   ├── config.py           # 配置文件
│   ├── run.py              # 启动入口
│   ├── requirements.txt    # 依赖列表
│   ├── reset_db.py         # 数据库重置工具
│   ├── debug_*.py          # 调试辅助脚本
│   └── instance/           # 数据库文件 (运行后生成)
├── frontend/               # 前端代码
│   ├── index.html          # 主页面
│   ├── script.js           # 业务逻辑
│   └── styles.css          # 样式表
└── README.md               # 项目说明
```

## 常见问题

*   **上传失败/数据库报错**: 如果遇到 "unknown column" 等数据库错误，可能是因为表结构更新。请尝试删除 `backend/instance/app.db` (或类似名称的 .db 文件) 后重启应用，系统会重新创建最新的数据库结构。
*   **端口被占用**: 如果 8080 端口被占用，请修改 `backend/run.py` 中的 `port` 参数。
