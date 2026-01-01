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


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text)
    due_date = db.Column(db.DateTime)

    # 关联到所属的课程 (外键)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


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
    assignment = db.relationship('Assignment', backref='submissions')


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