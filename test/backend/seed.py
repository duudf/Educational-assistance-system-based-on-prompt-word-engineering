import os
from datetime import datetime, timedelta, timezone
from app import app, db
from models import User, Course, Assignment, Submission, GradingRole, RoleCallLog

# --- 配置区 ---
TEACHER_USERNAME = 'z'
TEACHER_PASSWORD = '111111'
NUM_STUDENTS = 10
NUM_COURSES_PER_TEACHER = 3
NUM_ASSIGNMENTS_PER_COURSE = 4
NUM_SUBMISSIONS_PER_ASSIGNMENT = 2  # 每个作业有几个学生提交
NUM_ROLES = 5


def run_seed():
    """主函数：清理并填充数据库"""
    with app.app_context():
        print("--- 开始数据填充脚本 ---")

        # 1. 安全地删除旧数据库文件
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_path):
            print(f"正在删除旧数据库: {db_path}")
            os.remove(db_path)
            print("旧数据库已删除。")

        # 2. 创建所有表
        print("正在根据最新模型创建所有数据库表...")
        db.create_all()
        print("数据库表创建成功！")

        # 3. 创建核心用户
        print("正在创建核心用户...")
        # 创建教师
        teacher = User(username=TEACHER_USERNAME, role='teacher')
        teacher.set_password(TEACHER_PASSWORD)
        db.session.add(teacher)
        print(f"教师 '{TEACHER_USERNAME}' 创建成功。")

        # 创建学生
        students = []
        for i in range(1, NUM_STUDENTS + 1):
            student = User(username=f'student{i}', role='student')
            student.set_password('111111')  # 所有学生密码统一
            students.append(student)
        db.session.add_all(students)
        print(f"{NUM_STUDENTS} 名学生创建成功。")

        # 提交用户创建
        db.session.commit()

        # 4. 创建课程，并随机分配一些学生
        print("\n正在创建课程并分配学生...")
        courses = []
        course_titles = ["人工智能导论", "Python编程基础", "提示词工程入门", "机器学习实战", "深度学习应用"]
        for i in range(min(NUM_COURSES_PER_TEACHER, len(course_titles))):
            course = Course(
                name=course_titles[i],
                description=f"探索{course_titles[i]}的核心概念与实践。",
                teacher_id=teacher.id
            )
            # 为每门课程随机选择 5 个学生
            enrolled_students = students[i * 2: i * 2 + 5]
            course.students.extend(enrolled_students)
            courses.append(course)
        db.session.add_all(courses)
        print(f"{len(courses)} 门课程创建成功。")
        db.session.commit()

        # 5. 为每门课程创建作业
        print("\n正在为课程创建作业...")
        assignments = []
        for course in courses:
            for i in range(1, NUM_ASSIGNMENTS_PER_COURSE + 1):
                assignment = Assignment(
                    title=f"{course.name} - 作业 {i}",
                    content=f"这是关于 {course.name} 的第 {i} 次作业的具体要求...",
                    due_date=datetime.now(timezone.utc) + timedelta(days=7 + i),
                    course_id=course.id
                )
                assignments.append(assignment)
        db.session.add_all(assignments)
        print(f"{len(assignments)} 个作业创建成功。")
        db.session.commit()

        # 6. 为每个作业创建一些提交记录
        print("\n正在创建作业提交记录...")
        submissions = []
        for assignment in assignments:
            # 找到选了这门课的学生
            course_students = assignment.course.students.all()
            for i in range(min(NUM_SUBMISSIONS_PER_ASSIGNMENT, len(course_students))):
                submission = Submission(
                    content=f"这是学生 {course_students[i].username} 对作业 '{assignment.title}' 的回答。",
                    status='submitted',
                    student_id=course_students[i].id,
                    assignment_id=assignment.id
                )
                submissions.append(submission)
        db.session.add_all(submissions)
        print(f"{len(submissions)} 条提交记录创建成功。")
        db.session.commit()

        # 7. 创建 AI 评分角色 (GradingRole)
        print("\n正在创建AI评分角色...")
        roles = []
        role_names = ["严厉的教授", "鼓励型导师", "代码审查官", "简洁性评论员", "语法检查员"]
        for i in range(NUM_ROLES):
            role = GradingRole(
                name=role_names[i],
                description=f"这是一个{role_names[i]}角色的AI，专注于从特定角度进行评审。",
                prompt_content=f"# Role: {role_names[i]}\n\n# Task:\nYour task is to review the submission based on the provided criteria.",
                creator_id=teacher.id,
                is_system=False
            )
            roles.append(role)
        db.session.add_all(roles)
        print(f"{len(roles)} 个AI评分角色创建成功。")
        db.session.commit()

        # 8. 创建一些角色调用日志 (RoleCallLog)
        print("\n正在创建角色调用日志...")
        logs = []
        if roles and students:
            for i in range(10):  # 创建10条日志
                log = RoleCallLog(
                    role_id=roles[i % len(roles)].id,
                    user_id=students[i % len(students)].id
                )
                logs.append(log)
            db.session.add_all(logs)
            print(f"{len(logs)} 条角色调用日志创建成功。")
            db.session.commit()

        print("\n--- 数据填充成功完成！ ---")


if __name__ == '__main__':
    run_seed()