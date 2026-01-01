import datetime
import random
from app import app, db  # 导入你的flask app和db对象，和你的app.py保持一致
from models import User, Course, Assignment, Prompt, Submission, student_courses  # 导入所有模型

# 配置上下文（必须，否则无法操作数据库）
app.app_context().push()

# -------------------------- 清空原有测试数据（可选，防止重复） --------------------------
print("✅ 正在清空原有测试数据...")
Submission.query.delete()
Prompt.query.delete()
Assignment.query.delete()
db.session.execute(student_courses.delete()) # 清空多对多关联表
Course.query.delete()
User.query.filter(User.username.in_(['z', 'zz', 'zzz', 'zzzz'])).delete()
db.session.commit()

# -------------------------- 1. 创建用户数据（1个教师 + 3个学生） --------------------------
print("✅ 正在创建用户数据...")
# 创建1名教师 (核心！用于登录测试，用户名/密码可自定义)
teacher = User(username='z', role='teacher')
teacher.set_password('111111') # 密码：123456

# 创建3名学生
student1 = User(username='zz', role='student')
student1.set_password('111111')
student2 = User(username='zzz', role='student')
student2.set_password('111111')
student3 = User(username='zzzz', role='student')
student3.set_password('111111')

db.session.add_all([teacher, student1, student2, student3])
db.session.commit()

# -------------------------- 2. 创建教师的课程数据（2门课程） --------------------------
print("✅ 正在创建课程数据...")
course1 = Course(
    name='Python程序设计',
    description='Python基础+进阶教学',
    teacher_id=teacher.id  # 绑定给上面创建的教师
)
course2 = Course(
    name='人工智能导论',
    description='AI基础+大模型应用',
    teacher_id=teacher.id  # 绑定给上面创建的教师
)

db.session.add_all([course1, course2])
db.session.commit()

# -------------------------- 3. 学生选课（多对多关联，3个学生选2门课） --------------------------
print("✅ 正在创建学生选课数据...")
course1.students.append(student1)
course1.students.append(student2)
course2.students.append(student1)
course2.students.append(student3)
db.session.commit()

# -------------------------- 4. 创建课程作业（每门课2个作业，共4个作业） --------------------------
print("✅ 正在创建作业数据...")
today = datetime.datetime.now()
assignment1 = Assignment(
    title='Python作业-循环结构',
    content='完成10道Python循环练习题',
    due_date=today + datetime.timedelta(days=7),
    course_id=course1.id
)
assignment2 = Assignment(
    title='Python作业-函数定义',
    content='自定义5个常用Python函数',
    due_date=today + datetime.timedelta(days=5),
    course_id=course1.id
)
assignment3 = Assignment(
    title='AI作业-大模型原理',
    content='简述大模型的训练流程',
    due_date=today + datetime.timedelta(days=6),
    course_id=course2.id
)
assignment4 = Assignment(
    title='AI作业-提示词工程',
    content='编写3个高质量的AI提示词',
    due_date=today + datetime.timedelta(days=4),
    course_id=course2.id
)

db.session.add_all([assignment1, assignment2, assignment3, assignment4])
db.session.commit()

# -------------------------- 5. 创建作业提交记录（待批改+已批改，共6条，核心统计数据） --------------------------
print("✅ 正在创建作业提交数据...")
# 提交状态：有【待批改 submitted】和【已批改 graded】，用于统计待批改数量
submissions = [
    # 学生1提交的作业 (待批改)
    Submission(content='完成了循环练习题，全部正确', student_id=student1.id, assignment_id=assignment1.id, status='submitted'),
    Submission(content='函数定义作业已完成，包含注释', student_id=student1.id, assignment_id=assignment2.id, status='submitted'),
    # 学生2提交的作业 (待批改)
    Submission(content='循环题做了8道，2道待完善', student_id=student2.id, assignment_id=assignment1.id, status='submitted'),
    # 学生3提交的作业 (待批改)
    Submission(content='提示词工程作业已完成，符合要求', student_id=student3.id, assignment_id=assignment4.id, status='submitted'),
    # 已批改的作业（不会被统计到待批改里）
    Submission(content='大模型原理作业已完成', student_id=student1.id, assignment_id=assignment3.id, status='graded', grade=90.0),
    Submission(content='循环题全对', student_id=student2.id, assignment_id=assignment2.id, status='graded', grade=95.0)
]
db.session.add_all(submissions)
db.session.commit()

# -------------------------- 6. 创建教师的提示词数据（4条，用于统计） --------------------------
print("✅ 正在创建提示词数据...")
prompts = [
    Prompt(title='Python代码调试提示词', content='帮我调试这段Python代码，找出错误并修正，给出详细解释', teacher_id=teacher.id),
    Prompt(title='AI论文润色提示词', content='帮我润色这篇AI相关的论文，优化语句通顺度和逻辑结构', teacher_id=teacher.id),
    Prompt(title='作业批改提示词', content='帮我批改学生的Python作业，指出错误并给出正确答案和评分标准', teacher_id=teacher.id),
    Prompt(title='课程设计提示词', content='帮我设计一份Python课程的期末大作业，包含需求和评分标准', teacher_id=teacher.id)
]
db.session.add_all(prompts)
db.session.commit()

# -------------------------- 数据生成完成 --------------------------
print("🎉 测试数据生成完成！所有数据已正确关联！")
print(f"👉 教师账号：username=teacher1  password=123456")
print(f"👉 学生账号：username=student1/student2/student3  password=123456")
print(f"📊 生成的数据统计：")
print(f"   - 教师课程数：2门")
print(f"   - 选课学生数：3人 (去重后)")
print(f"   - 教师提示词数：4条")
print(f"   - 待批改作业数：4份")
print(f"✅ 重启Flask后端，前端看板即可看到真实数据！")