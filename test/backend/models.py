# models.py
import datetime
from sqlalchemy.dialects.sqlite import JSON # 兼容 SQLite 的 JSON 类型
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()

# -------------------- 模型定义开始 --------------------

# 学生-课程关联表 (用于多对多关系)
student_courses = db.Table('student_courses',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                           db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
                           )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), nullable=False, default='student')  # 角色字段

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)

    # 关联到创建该课程的教师 (外键)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 'teacher' 属性让我们能通过 Course.teacher 访问到创建者 User 对象
    teacher = db.relationship('User', backref='courses_taught')  # 将 backref 改为 courses_taught 避免与 User.courses 冲突

    # 关联到该课程下的所有作业 (一对多关系)
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic')

    # 关联到所有选修该课程的学生 (多对多关系)
    students = db.relationship('User', secondary=student_courses,
                               backref=db.backref('enrolled_courses', lazy='dynamic'),
                               lazy='dynamic')





class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # 关联到创建该提示词的教师
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher = db.relationship('User', backref='prompts')


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    submission_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(64), default='submitted')  # e.g., 'submitted', 'graded'
    grade = db.Column(db.Float)

    # 关联到提交该作业的学生
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student = db.relationship('User', backref='submissions')

    # 关联到对应的作业
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    # assignment = db.relationship('Assignment', backref='submissions')


# --- ↓↓↓ 在文件底部添加新模型 ↓↓↓ ---
class AnalysisReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 关联到学生 (一对一关系)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    student = db.relationship('User', backref=db.backref('analysis_report', uselist=False))

    # 使用 JSON 类型存储 AI 返回的完整报告
    report_json = db.Column(JSON, nullable=False)

    # 记录最后更新时间
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# models.py
class PracticeRecord(db.Model):
    """AI 出题练习记录"""
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('User', backref='practice_records')

    # 存储完整的题目 JSON 数据
    quiz_data = db.Column(JSON, nullable=False)

    # 学生的答案
    user_answer = db.Column(db.Text)

    # AI 的评分 (0-100)
    ai_grade = db.Column(db.Integer)

    # AI 的评语
    ai_feedback = db.Column(db.Text)

    # 练习时间
    practice_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class FavoriteQuiz(db.Model):
    """学生收藏的题目"""
    id = db.Column(db.Integer, primary_key=True)
    # 关联到学生
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('User', backref='favorite_quizzes')

    # 直接存储题目的 JSON 数据
    quiz_data = db.Column(JSON, nullable=False)
    add_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# 1. 新增：提示词模板表 (对应你截图里的“默认助手”、“作业助手”等)
class PromptTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 例如：'简答题-关键词评分法'
    description = db.Column(db.String(256))  # 例如：'根据关键词命中情况给分'
    # 模板核心内容，里面会有占位符 {criteria}
    template_content = db.Column(db.Text, nullable=False)
    is_system = db.Column(db.Boolean, default=False)  # 是否为系统预设


# 2. 修改：作业表，增加评分标准字段
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text)  # 作业题目
    due_date = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    # --- ↓↓↓ 新增字段 ↓↓↓ ---
    # 老师针对这道题写的具体得分点 (例如："提到TCP得2分...")
    grading_criteria = db.Column(db.Text)

    submissions = db.relationship('Submission', backref='assignment', cascade="all, delete-orphan")



class GradingRole(db.Model):
    """AI 评分角色表"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 角色名称，如 "严厉教授"
    description = db.Column(db.String(256))  # 简短描述，给学生看

    # 这里存放该角色的完整提示词配置（包含得分点逻辑、语气、格式要求）
    # 这就是你说的“一个单独的文本”
    prompt_content = db.Column(db.Text, nullable=False)

    is_system = db.Column(db.Boolean, default=False)  # True=系统默认，False=教师创建

    # 如果是教师创建的，关联到教师ID
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    creator = db.relationship('User', backref='created_roles')

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content': self.prompt_content,
            'is_system': self.is_system,
            'creator': self.creator.username if self.creator else "系统内置",
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

def to_dict_list(self):
    return {
        'id': self.id,
        'role_name': self.role_name,
        'content': self.short_intro or self.prompt_template[:50] + "...", # 预览内容
        'teacher_name': self.teacher.username if self.teacher else "系统内置", # 判断是否为系统创建
        'importance': 5 if not self.teacher_id else 4, # 系统角色默认5星，教师4星
        'status': self.status,
        'category_name': self.category,
        'is_system': True if not self.teacher_id else False # 增加一个标识位
    }

from datetime import datetime
class RoleCallLog(db.Model):
    __tablename__ = 'role_call_log'
    id = db.Column(db.Integer, primary_key=True)
    # 关联到被调用的角色ID
    role_id = db.Column(db.Integer, db.ForeignKey('grading_role.id'), nullable=False)
    # 关联到发起调用的用户ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 调用发生的时间，默认是记录创建的时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 建立关系（可选，但推荐）
    role = db.relationship('GradingRole', backref=db.backref('call_logs', lazy=True))
    user = db.relationship('User', backref=db.backref('role_calls', lazy=True))

    def __repr__(self):
        return f'<RoleCallLog role_id={self.role_id} user_id={self.user_id}>'