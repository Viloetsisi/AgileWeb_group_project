from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ------------------------------
# 用户账户模型
# ------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False)
    documents = db.relationship("Document", backref="user", lazy=True)


# ------------------------------
# 用户填写的详细资料
# ------------------------------
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    full_name = db.Column(db.String(120))           # 姓名
    age = db.Column(db.Integer)                     # 年龄
    birth_date = db.Column(db.Date)                 # 出生年月日
    education = db.Column(db.String(100))           # 学历
    graduation_date = db.Column(db.Date)            # 毕业时间
    school = db.Column(db.String(200))              # 毕业学校
    expected_company = db.Column(db.String(200))    # 期望公司
    career_goal = db.Column(db.String(200))         # 期望职位方向
    self_description = db.Column(db.Text)           # 自我介绍
    internship_experience = db.Column(db.Text)      # 实习经历

    is_shared = db.Column(db.Boolean, default=False)  # 是否愿意公开资料给他人


# ------------------------------
# 用户上传的 PDF 文件（证书、奖状）
# ------------------------------
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    file_name = db.Column(db.String(200))           # 显示名称
    file_path = db.Column(db.String(300))           # 实际存储路径
    file_type = db.Column(db.String(50))            # 类型：证书/奖项/实习证明等
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

    is_shared = db.Column(db.Boolean, default=False)  # 是否公开此文件
