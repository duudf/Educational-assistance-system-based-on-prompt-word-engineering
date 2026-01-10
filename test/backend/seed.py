# seed.py

import click
from flask.cli import with_appcontext
from app import db
from models import User, Course, Assignment, Submission, PracticeRecord, FavoriteQuiz, AnalysisReport
import datetime
import json


@click.command('seed')
@with_appcontext
def seed_command():
    """清空数据库并填充所有模型的标准测试数据"""

    print("--- 开始清空数据库 ---")
    db.drop_all()
    db.create_all()
    print("--- 数据库已清空并重建 ---")

    print("\n--- 正在创建用户 ---")
    password = '111111'
    teacher_z = User(username='z', role='teacher');
    teacher_z.set_password(password)
    student_zz = User(username='zz', role='student');
    student_zz.set_password(password)
    student_zzz = User(username='zzz', role='student');
    student_zzz.set_password(password)
    student_zzzz = User(username='zzzz', role='student');
    student_zzzz.set_password(password)
    db.session.add_all([teacher_z, student_zz, student_zzz, student_zzzz])
    db.session.commit()
    print("用户创建完成: 1名教师, 3名学生。密码均为 '111111'")

    print("\n--- 正在创建课程 ---")
    course_prompt = Course(name='提示词工程入门', description='学习如何与AI高效对话', teacher=teacher_z)
    course_python = Course(name='Python编程基础', description='从零开始学习Python', teacher=teacher_z)
    course_ai = Course(name='人工智能导论', description='探索AI的核心概念', teacher=teacher_z)
    db.session.add_all([course_prompt, course_python, course_ai])
    db.session.commit()
    print("课程创建完成: 3门课程，均由 'z' 老师创建")

    print("\n--- 正在处理学生选课 ---")
    student_zz.enrolled_courses.extend([course_prompt, course_ai])
    student_zzz.enrolled_courses.extend([course_prompt, course_python])
    student_zzzz.enrolled_courses.append(course_python)
    db.session.commit()
    print("学生选课关系已建立")

    print("\n--- 正在创建作业 ---")
    assignment1 = Assignment(title='Prompt基础：编写清晰的指令', course=course_prompt,
                             due_date=datetime.datetime.utcnow() + datetime.timedelta(days=7))
    assignment2 = Assignment(title='Python基础：变量与循环', course=course_python,
                             due_date=datetime.datetime.utcnow() + datetime.timedelta(days=10))
    assignment3 = Assignment(title='已过期的作业', course=course_python,
                             due_date=datetime.datetime.utcnow() - datetime.timedelta(days=1))
    db.session.add_all([assignment1, assignment2, assignment3])
    db.session.commit()
    print("作业创建完成: 3份作业")

    print("\n--- 正在模拟学生提交作业 ---")
    sub1 = Submission(content='<p>这是 <strong>zz</strong> 对 Prompt 作业的回答。</p>', student=student_zz,
                      assignment=assignment1, status='submitted')
    sub2 = Submission(content='<p>这是 <strong>zzz</strong> 对 Prompt 作业的回答。</p>', student=student_zzz,
                      assignment=assignment1, status='graded', grade=95.0)
    sub3 = Submission(content='print("Hello, Python!")', student=student_zzz, assignment=assignment2, status='graded',
                      grade=88.5)
    db.session.add_all([sub1, sub2, sub3])
    db.session.commit()
    print("作业提交记录创建完成: 3条")

    print("\n--- 正在创建AI练习和收藏记录 (为学生 zz) ---")
    quiz_data1 = {"type": "简答题", "question": "什么是上下文学习(In-Context Learning)?", "answer": "...",
                  "explanation": "..."}
    p_record1 = PracticeRecord(student=student_zz, quiz_data=quiz_data1, user_answer="我的回答是...", ai_grade=80,
                               ai_feedback="回答基本正确，但可以更深入...")

    fav_quiz_data = {"type": "编程题", "question": "请用Python实现一个简单的斐波나契数列函数。", "answer": "...",
                     "explanation": "..."}
    fav1 = FavoriteQuiz(student=student_zz, quiz_data=fav_quiz_data)

    db.session.add_all([p_record1, fav1])
    db.session.commit()
    print("AI练习与收藏记录创建完成")

    print("\n--- 正在创建AI分析报告 (为学生 zz) ---")
    report_data = {
        "activity_score": 4, "performance_score": 5, "knowledge_mastery_score": 4,
        "innovation_score": 3, "consistency_score": 4, "potential_score": 5,
        "strengths": ["提示词理解能力强", "学习态度积极"],
        "suggestions": ["尝试更复杂的编程练习", "多参与课程讨论"],
        "summary": "该学生学习主动性强，在AI相关课程上表现出色，潜力巨大。"
    }
    analysis1 = AnalysisReport(student=student_zz, report_json=report_data)

    db.session.add(analysis1)
    db.session.commit()
    print("AI分析报告创建完成")

    print("\n\n✅✅✅ 所有测试数据已成功填充到数据库！ ✅✅✅")