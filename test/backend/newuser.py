from app import app, db  # 跟你的项目一致，不用改
from models import User  # 导入你的用户模型
from werkzeug.security import generate_password_hash

# 必须的上下文配置，复制即可
app.app_context().push()

# -------------------------- 【只需要修改这里！】 --------------------------
# 自定义你要新增的账号信息，想加几个改几个
new_username = "admin"  # 账号名（唯一，不能重复）
new_password = "111111"  # 登录密码（明文即可，脚本自动加密）
new_role = "admin"  # 角色：teacher=教师 / student=学生
# -------------------------------------------------------------------------

# 1. 检查账号是否已存在（防止重复）
if User.query.filter_by(username=new_username).first():
    print(f"❌ 账号 {new_username} 已存在！换个用户名试试")
else:
    # 2. 创建新用户 + 自动生成加密密码
    new_user = User()
    new_user.username = new_username
    new_user.role = new_role
    new_user.password_hash = generate_password_hash(new_password)  # 核心：自动加密！

    # 3. 写入数据库
    db.session.add(new_user)
    db.session.commit()
    print(f"🎉 账号新增成功！✅")
    print(f"👉 账号：{new_username}")
    print(f"👉 密码：{new_password}")
    print(f"👉 角色：{new_role}")