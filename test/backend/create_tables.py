from app import app, db
# 必须导入新模型，否则 create_all 找不到它
from models import GradingRole

with app.app_context():
    # create_all 会自动检测还没创建的表，并创建它们
    # 已经存在的表（如 User, Assignment）不会受影响
    db.create_all()
    print(">>> 成功创建 grading_role 表！")