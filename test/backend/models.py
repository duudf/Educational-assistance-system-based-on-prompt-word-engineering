# models.py
import datetime
import uuid

import shortuuid
from sqlalchemy.dialects.sqlite import JSON # 兼容 SQLite 的 JSON 类型
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()


def generate_short_id(model):
    """
    为指定的模型生成一个唯一的8位短ID。
    它会检查数据库确保生成的ID尚不存在。
    """
    # 使用字母表'23456789ABCDEFGHJKLMNPQRSTUVWXYZ'避免混淆的字符(0/O, 1/I)
    alphabet = '23456789'
    shortuuid.set_alphabet(alphabet)

    while True:
        # 生成一个8位的短ID
        new_id = shortuuid.random(length=6)
        # 检查这个ID是否已经存在于指定的模型表中
        if not model.query.filter_by(public_id=new_id).first():
            return new_id
# -------------------- 模型定义开始 --------------------

# 学生-课程关联表 (用于多对多关系)
student_courses = db.Table('student_courses',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                           db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
                           )


class User(db.Model):
    public_id = db.Column(db.String(6), unique=True, nullable=False, default=lambda: generate_short_id(User))
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), nullable=False, default='student')  # 角色字段

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    public_id = db.Column(db.String(6), unique=True, nullable=False, default=lambda: generate_short_id(Course))
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
    public_id = db.Column(db.String(6), unique=True, nullable=False, default=lambda: generate_short_id(Assignment))
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text)  # 作业题目
    due_date = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    # --- ↓↓↓ 新增字段 ↓↓↓ ---
    # 老师针对这道题写的具体得分点 (例如："提到TCP得2分...")
    grading_criteria = db.Column(db.Text)

    submissions = db.relationship('Submission', backref='assignment', cascade="all, delete-orphan")
from datetime import datetime, timezone

class GradingRole(db.Model):
    """AI 评分角色表"""
    __tablename__ = 'grading_role'  # 明确指定表名，这是一个好习惯
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    prompt_content = db.Column(db.Text, nullable=False)
    is_system = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    creator = db.relationship('User', backref='created_roles')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- [核心修改 1] ---
    # 在 GradingRole 模型中定义与 RoleCallLog 的关系，并设置级联删除策略。
    # 当一个 GradingRole 被删除时，所有相关的日志记录将自动被删除，从而修复 IntegrityError。
    call_logs = db.relationship('RoleCallLog', backref='role', cascade="all, delete-orphan", lazy=True)

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


class RoleCallLog(db.Model):
    """AI 角色调用日志表"""
    __tablename__ = 'role_call_log'
    id = db.Column(db.Integer, primary_key=True)
    # 关联到被调用的角色ID
    role_id = db.Column(db.Integer, db.ForeignKey('grading_role.id'), nullable=False)
    # 关联到发起调用的用户ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 调用发生的时间，默认是记录创建的时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- [核心修改 2] ---
    # 移除了这里的 role 关系定义，因为它现在由 GradingRole.call_logs 的 backref='role' 自动创建，
    # 这样就解决了 InvalidRequestError 命名冲突的问题。

    # 与 User 的关系保持不变
    user = db.relationship('User', backref=db.backref('role_calls', lazy=True))

    def __repr__(self):
        return f'<RoleCallLog role_id={self.role_id} user_id={self.user_id}>'


# ----------------------------------------------------
# 这是一个独立的函数，它不属于任何类，请确保它在文件的顶层作用域，而不是缩进在某个类里面。
# 如果这个函数之前是写在 GradingRole 类里面的，那是不对的。
def to_dict_list(self):
    return {
        'id': self.id,
        'role_name': self.role_name,
        'content': self.short_intro or self.prompt_template[:50] + "...",
        'teacher_name': self.teacher.username if self.teacher else "系统内置",
        'importance': 5 if not self.teacher_id else 4,
        'status': self.status,
        'category_name': self.category,
        'is_system': True if not self.teacher_id else False
    }