import os

import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Course, Assignment, Submission, Prompt, AnalysisReport, FavoriteQuiz, PracticeRecord, \
    GradingRole, student_courses, PromptTemplate, RolePrompt, RoleCallLog
from sqlalchemy import or_
student_courses, PromptTemplate
from flask_migrate import Migrate
import openai
import json
import requests
import json
import time
import re
from sqlalchemy import or_, func

# from seed import seed_command   # 更新数据库
app = Flask(__name__)
app.config.from_object(Config)

# 初始化
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
# app.cli.add_command(seed_command) # 更新数据库

# ======================================================================
# 1. 辅助函数/装饰器
# ======================================================================

def token_required(f):
    """装饰器：用于需要认证的接口，从Token中解析用户"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Token')
        if not token:
            return jsonify({'code': 50014, 'message': 'Token 缺失'}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({'code': 50014, 'message': 'Token中缺少用户信息'}), 401
            current_user = db.session.get(User, int(user_id))
        except (jwt.InvalidTokenError, ValueError, Exception):
            return jsonify({'code': 50014, 'message': 'Token 无效或已损坏'}), 401

        if current_user is None:
            return jsonify({'code': 50008, 'message': '根据Token找不到用户'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# ======================================================================
# 2. 用户认证与信息 (User Authentication & Info)
# ======================================================================

@app.route('/user/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username, password, role = data.get('username'), data.get('password'), data.get('role')
    if not all([username, password, role]):
        return jsonify({"code": 50000, "message": "用户名、密码和角色均不能为空"}), 400
    if role not in ['student', 'teacher']:
        return jsonify({"code": 50000, "message": "无效的角色"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"code": 50000, "message": "用户名已存在"}), 400
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"code": 20000, "message": "注册成功"})


@app.route('/user/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user is None or not user.check_password(data.get('password')):
        return jsonify({"code": 50008, "message": "用户名或密码错误"}), 401
    token = jwt.encode({
        'user_id': user.id,
         # 必须写成 datetime.datetime.utcnow()
'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({"code": 20000, "data": {"token": token}})


@app.route('/user/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({"code": 20000, "data": "success"})


@app.route('/user/info', methods=['GET'])
@token_required
def get_user_info(current_user):
    """获取用户信息"""
    return jsonify({
        "code": 20000,
        "data": {
            "roles": [current_user.role],
            "name": current_user.username,
            "avatar": "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif"
        }
    })


# ======================================================================
# 3. 仪表盘数据 (Dashboard Data)
# ======================================================================

@app.route('/dashboard/data', methods=['GET'])
@token_required
def get_dashboard_data(current_user):
    """获取仪表盘统计数据"""
    if current_user.role == 'teacher':
        teacher_courses = current_user.courses_taught
        course_ids = [c.id for c in teacher_courses]

        unique_student_ids = set()
        for course in teacher_courses:
            for student in course.students:
                unique_student_ids.add(student.id)

        review_count = 0
        if course_ids:
            assignment_ids = [a.id for a in Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()]
            if assignment_ids:
                review_count = Submission.query.filter(Submission.assignment_id.in_(assignment_ids),
                                                       Submission.status == 'submitted').count()

        recent_assignments_data = []
        if course_ids:
            recent_assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).order_by(
                Assignment.id.desc()).limit(5).all()
            recent_assignments_data = [{'title': a.title, 'course_name': a.course.name,
                                        'due_date': a.due_date.strftime('%Y-%m-%d') if a.due_date else 'N/A'} for a in
                                       recent_assignments]

        return jsonify({'code': 20000, 'data': {
            'studentCount': len(unique_student_ids),
            'courseCount': len(teacher_courses),
            'promptCount': Prompt.query.filter_by(teacher_id=current_user.id).count(),
            'reviewCount': review_count,
            'recent_assignments': recent_assignments_data
        }})


    elif current_user.role == 'student':
        enrolled_courses = current_user.enrolled_courses.all()
        course_ids = [c.id for c in enrolled_courses]
        # 计算已提交作业数
        submitted_count = Submission.query.filter_by(student_id=current_user.id).count()
        # 计算所有作业总数
        total_assignments_count = 0
        if course_ids:
            total_assignments_count = Assignment.query.filter(Assignment.course_id.in_(course_ids)).count()
        # 待完成作业数 = 总作业数 - 已提交作业数
        pending_count = total_assignments_count - submitted_count
        return jsonify({'code': 20000, 'data': {
            'courseCount': len(enrolled_courses),
            'pendingCount': pending_count,
            'submittedCount': submitted_count,
            # (其他前端可能需要的数据)
            'recent_assignments': []
        }})
    return jsonify({'code': 50000, 'message': '未知角色'})





@app.route('/courses', methods=['GET'])
@token_required
def get_courses(current_user):
    """获取课程列表，支持分页和多条件模糊搜索"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search_term = request.args.get('search', None, type=str)
    fetch_all_for_student = request.args.get('all', 'false').lower() == 'true'

    # --- ↓↓↓ 核心修改：使用教师名字进行过滤 ↓↓↓ ---
    # 1. 总是从基础查询开始
    base_query = Course.query

    # 2. 根据角色确定数据范围
    if current_user.role == 'teacher':
        # 通过关联的 User 模型的 username 字段进行过滤
        query = base_query.join(User, Course.teacher_id == User.id).filter(User.username == current_user.username)

    elif current_user.role == 'student':
        if fetch_all_for_student:
            query = base_query
        else:
            enrolled_course_ids = {c.id for c in current_user.enrolled_courses}
            query = base_query.filter(Course.id.in_(enrolled_course_ids)) if enrolled_course_ids else base_query.filter(
                False)
    else:
        query = base_query
    # --- ↑↑↑ 修改结束 ↑↑↑ ---

    # 3. 在已确定的数据范围上，应用搜索过滤器
    # (为了避免与上面的 .join() 冲突，我们在这里也做一次 join)
    if search_term:
        conditions = [
            Course.name.like(f"%{search_term}%"),
            User.username.like(f"%{search_term}%")
        ]
        try:
            search_id = int(search_term)
            conditions.append(Course.id == search_id)
        except ValueError:
            pass
        # 确保在应用 User.username 搜索前已经 join 了 User 表
        query = query.join(User, Course.teacher_id == User.id, isouter=True).filter(or_(*conditions))

    pagination = query.order_by(Course.id.desc()).paginate(page=page, per_page=limit, error_out=False)
    courses = pagination.items
    total = pagination.total

    # --- ↓↓↓ 核心修复：无论何时都为学生预加载已选课程ID ↓↓↓ ---
    enrolled_course_ids = set()
    if current_user.role == 'student':
        # 显式执行查询，确保数据被加载
        enrolled_course_ids = {c.id for c in current_user.enrolled_courses.all()}
    # --- ↑↑↑ 修复结束 ↑↑↑ ---

    items = []
    for course in courses:
        items.append({
            'id': course.id,
            'name': course.name,
            'teacher_name': course.teacher.username if course.teacher else 'N/A',
            'student_count': course.students.count(),
            'description': course.description,
            'is_enrolled': course.id in enrolled_course_ids if 'enrolled_course_ids' in locals() else False
        })

    return jsonify({'code': 20000, 'data': {'total': total, 'items': items}})


@app.route('/courses/list', methods=['GET'])
@token_required
def get_course_list(current_user):
    """
    获取课程下拉列表。
    - 教师访问时：返回自己创建的所有课程。
    - 学生访问时：只返回自己已选的所有课程。
    """
    courses = []
    if current_user.role == 'teacher':
        # 教师看到的是自己创建的所有课程
        courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.name).all()
    elif current_user.role == 'student':
        # --- ↓↓↓ 核心修改：为学生返回已选课程 ↓↓↓ ---
        # 学生看到的应该是自己已经选修的课程
        courses = current_user.enrolled_courses.order_by(Course.name).all()
        # --- ↑↑↑ 修改结束 ↑↑↑ ---

    course_list = [{'id': c.id, 'name': c.name} for c in courses]

    return jsonify({'code': 20000, 'data': {'items': course_list}})


# ======================================================================
# 5. 作业管理 (Assignment Management)
# ======================================================================

@app.route('/assignments', methods=['GET'])
@token_required
def get_assignments(current_user):
    """获取作业列表（分页）"""
    page, limit = request.args.get('page', 1, type=int), request.args.get('limit', 20, type=int)
    query = Assignment.query
    if current_user.role == 'teacher':
        course_ids = [c.id for c in current_user.courses_taught]
        query = query.filter(Assignment.course_id.in_(course_ids)) if course_ids else query.filter(False)
    elif current_user.role == 'student':
        course_ids = [c.id for c in current_user.enrolled_courses]
        query = query.filter(Assignment.course_id.in_(course_ids)) if course_ids else query.filter(False)

    pagination = query.order_by(Assignment.id.desc()).paginate(page=page, per_page=limit, error_out=False)
    return jsonify({'code': 20000, 'data': {
        'total': pagination.total,
        'items': [{'id': a.id, 'title': a.title, 'course_name': a.course.name,
                   'due_date': a.due_date.strftime('%Y-%m-%d %H:%M') if a.due_date else 'N/A',
                   'submission_count': len(a.submissions)} for a in pagination.items]
    }})


@app.route('/assignments/<int:id>', methods=['GET'])
@token_required
def get_assignment_detail(current_user, id):
    """获取单个作业详情"""
    assignment = db.session.get(Assignment, id)
    if not assignment: return jsonify({'code': 404, 'message': '作业不存在'}), 404
    if current_user.role == 'teacher' and assignment.course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '无权访问'}), 403
    return jsonify({'code': 20000, 'data': {
        'id': assignment.id, 'title': assignment.title, 'content': assignment.content,
        'display_time': assignment.due_date.isoformat() if assignment.due_date else None,
        'course_id': assignment.course_id
    }})


@app.route('/assignments', methods=['POST'])
@token_required
def create_assignment(current_user):
    """创建新作业"""
    if current_user.role != 'teacher': return jsonify({'code': 403, 'message': '只有教师可创建'}), 403
    data = request.get_json()
    course = db.session.get(Course, data.get('course_id'))
    if not course or course.teacher_id != current_user.id:
        return jsonify({'code': 400, 'message': '无效的课程ID'}), 400
    new_assignment = Assignment(
        title=data.get('title'), content=data.get('content'), course_id=data.get('course_id'),
        due_date=datetime.datetime.fromisoformat(data.get('display_time')) if data.get('display_time') else None
    )
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({'code': 20000, 'data': {'id': new_assignment.id}, 'message': '创建成功'})


@app.route('/assignments/<int:id>', methods=['PUT'])
@token_required
def update_assignment(current_user, id):
    """更新作业"""
    assignment = db.session.get(Assignment, id)
    if not assignment: return jsonify({'code': 404, 'message': '作业不存在'}), 404
    if current_user.role != 'teacher' or assignment.course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '无权修改'}), 403
    data = request.get_json()
    assignment.title = data.get('title', assignment.title)
    assignment.content = data.get('content', assignment.content)
    assignment.due_date = datetime.datetime.fromisoformat(data.get('display_time')) if data.get(
        'display_time') else None
    db.session.commit()
    return jsonify({'code': 20000, 'message': '更新成功'})


@app.route('/courses', methods=['POST'])
@token_required
def create_course(current_user):
    """创建新课程"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '只有教师才能创建课程'}), 403

    data = request.get_json()
    if not data or not data.get('name') or not data.get('description'):
        return jsonify({'code': 400, 'message': '课程名称和描述不能为空'}), 400

    new_course = Course(
        name=data.get('name'),
        description=data.get('description'),
        teacher_id=current_user.id  # 将课程与当前登录的教师关联
    )
    db.session.add(new_course)
    db.session.commit()

    return jsonify({'code': 20000, 'data': {'id': new_course.id}, 'message': '创建成功'})
# --- ↑↑↑ 添加结束 ↑↑↑ ---

@app.route('/courses/<int:id>', methods=['GET'])
@token_required
def get_course_detail(current_user, id):
    """获取单个课程详情"""
    # 1. 查询课程
    course = db.session.get(Course, id)

    # 2. 检查课程是否存在
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在'}), 404

    # 3. (可选) 安全检查：确保教师只能查看自己课程的详情
    if current_user.role == 'teacher' and course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '无权访问此课程'}), 403

    # 4. 准备要返回的数据
    data = {
        'id': course.id,
        'name': course.name,
        'description': course.description
    }

    # --- ↓↓↓ 确保函数总是有返回值 ↓↓↓ ---
    # 5. 返回成功的响应
    return jsonify({'code': 20000, 'data': data})



@app.route('/courses/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(current_user, course_id):
    """删除一个课程"""
    # 1. 权限校验：必须是教师才能执行删除操作
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '您没有权限执行此操作'}), 403

    # 2. 查找课程
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在'}), 404

    # 3. [至关重要] 身份校验：确保当前教师是该课程的创建者
    if course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '您只能删除自己创建的课程'}), 403

    # 4. 执行删除操作
    # 注意：如果有关联的学生选课记录，您需要考虑如何处理。
    # 这里的简单删除会依赖于数据库的外键约束（比如级联删除或置空）。
    db.session.delete(course)
    db.session.commit()

    return jsonify({'code': 20000, 'message': '课程删除成功'})

# --- ↑↑↑ 新增结束 ↑↑↑ ---


@app.route('/students', methods=['GET'])
@token_required
def get_students(current_user):
    """获取学生列表，支持按课程ID筛选和分页（最终健壮版）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    course_id_str = request.args.get('course_id')

    # 1. 总是从一个基础查询开始：所有角色为'student'的用户
    query = User.query.filter_by(role='student')

    # 2. 如果前端传入了 course_id，则应用筛选
    if course_id_str and course_id_str.isdigit():
        course_id = int(course_id_str)
        course = db.session.get(Course, course_id)

        if course:
            # 安全检查
            if current_user.role == 'teacher' and course.teacher_id != current_user.id:
                return jsonify({'code': 403, 'message': '无权访问该课程的学生列表'}), 403

            # --- ↓↓↓ 核心修改：使用子查询进行筛选 ↓↓↓ ---
            # 步骤 a: 在 student_courses 表中找出所有 course_id 匹配的学生 ID
            student_ids_subquery = db.session.query(student_courses.c.user_id).filter(
                student_courses.c.course_id == course_id)

            # 步骤 b: 在 User 表中筛选出 ID 在上面子查询结果中的学生
            query = query.filter(User.id.in_(student_ids_subquery))
            # --- ↑↑↑ 修改结束 ↑↑↑ ---
        else:
            # 如果课程ID无效，返回空结果
            query = query.filter(False)

    # 3. 对最终确定的查询对象进行排序和分页
    pagination = query.order_by(User.id.asc()).paginate(page=page, per_page=limit, error_out=False)
    students = pagination.items
    total = pagination.total

    # 4. 构建返回数据 (保持不变)
    items = []
    for student in students:
        items.append({
            'id': student.id,
            'name': student.username,
            'enrolled_course_count': student.enrolled_courses.count(),
            'submission_count': len(student.submissions)
        })

    return jsonify({'code': 20000, 'data': {'total': total, 'items': items}})


# ======================================================================
# 8. AI 智能分析 (AI Analysis) - 完整最终版
# ======================================================================


@app.route('/students/<int:student_id>/analysis', methods=['GET'])
@token_required
def get_student_analysis(current_user, student_id):
    print("=" * 50)
    print(f"收到请求: {request.method} {request.path}")
    print(f"完整的 URL Query 参数 (request.args): {request.args}")
    print(f"获取 'force_refresh' 的值: {request.args.get('force_refresh')}")
    print("=" * 50)

    """使用 AI 分析单个学生的学习情况，支持缓存、强制刷新和对比"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    student = db.session.get(User, student_id)
    if not student or student.role != 'student':
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    # ✅ 修复后代码（兼容 'true'/'True'/'TRUE' 所有格式，无参数时默认false）
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'

    report_record = AnalysisReport.query.filter_by(student_id=student_id).first()
    previous_report = report_record.report_json if report_record else None

    # 如果不需要强制刷新，并且有旧报告，直接返回
    if previous_report and not force_refresh:
        print(f"为学生 {student_id} 找到了缓存的AI报告，直接返回。")
        return jsonify({'code': 20000, 'data': {
            'current': previous_report,
            'previous': None,  # 首次加载时，previous 为 null
            'last_updated': report_record.last_updated.isoformat()
        }})

    # --- 开始生成新报告 ---
    print(f"为学生 {student_id} 生成新的AI报告 (强制刷新: {force_refresh})")

    submissions = Submission.query.filter_by(student_id=student.id).order_by(Submission.submission_date.desc()).all()
    if not submissions:
        return jsonify({'code': 400, 'message': '该学生暂无学习数据可供分析'}), 400

    analysis_data_str = ""
    for sub in submissions:
        # --- ↓↓↓ 在这里增加一个安全检查 ↓↓↓ ---
        if not sub.assignment:
            print(f"警告：跳过一条孤立的提交记录 (ID: {sub.id}), 它关联的作业已被删除。")
            continue  # 跳过本次循环
        # --- ↑↑↑ 检查结束 ↑↑↑ ---
        analysis_data_str += (
            f"- 作业:{sub.assignment.title}, 课程:{sub.assignment.course.name}, "
            f"提交于:{sub.submission_date.strftime('%Y-%m-%d')}, 成绩:{sub.grade if sub.grade is not None else '未批改'}\n"
        )

    if not analysis_data_str:
        return jsonify({'code': 400, 'message': '该学生暂无有效的学习数据可供分析'}), 400

    old_report_context = ""
    if previous_report and force_refresh:  # 只有在强制刷新且存在旧报告时才加入上下文
        old_report_context = f"""
        这是对该学生上一次的分析报告，请在此基础上结合最新数据进行更新和对比，重点分析学生的变化和进步:
        {json.dumps(previous_report, ensure_ascii=False, indent=2)}
        """

    prompt = f"""
    你是一位专业的教育数据分析师。请根据学生 "{student.username}" 的最新作业提交记录，进行深入分析。
    {old_report_context}

    学生的最新作业数据如下:
    {analysis_data_str}

    请从以下六个维度进行分析并给出1-5分的整数评分: 学习积极性(activity_score), 成绩表现(performance_score), 知识掌握度(knowledge_mastery_score), 探索创新性(innovation_score), 稳定性与毅力(consistency_score), 发展潜力(potential_score)。
    同时，请提供以下分析内容: 潜在强项(strengths)数组, 改进建议(suggestions)数组, 综合评价(summary)文本。
    请严格按照以下JSON格式返回，不要包含任何其他多余的文字、解释或代码块标记:
    {{
      "activity_score": <评分>, "performance_score": <评分>, "knowledge_mastery_score": <评分>,
      "innovation_score": <评分>, "consistency_score": <评分>, "potential_score": <评分>,
      "strengths": ["强项1"], "suggestions": ["建议1"], "summary": "<总结文本>"
    }}
    """

    try:
        client = openai.OpenAI(
            api_key=app.config['SILICONFLOW_API_KEY'],
            base_url="https://api.siliconflow.cn/v1"
        )
        completion = client.chat.completions.create(
            model="alibaba/Qwen2-7B-Instruct",
            messages=[
                {"role": "system", "content": "你是一个数据分析助手，只会返回严格的JSON格式数据。"},
                {"role": "user", "content": prompt}
            ]
        )
        ai_response_content = completion.choices[0].message.content

        cleaned_json_string = ai_response_content.strip()
        if cleaned_json_string.startswith("```json"): cleaned_json_string = cleaned_json_string[7:].strip()
        if cleaned_json_string.endswith("```"): cleaned_json_string = cleaned_json_string[:-3].strip()

        current_report = json.loads(cleaned_json_string)

        if report_record:
            report_record.report_json = current_report
            # 更新 last_updated 时间
            report_record.last_updated = datetime.datetime.utcnow()
        else:
            report_record = AnalysisReport(student_id=student_id, report_json=current_report)
            db.session.add(report_record)
        db.session.commit()

        return jsonify({'code': 20000, 'data': {
            'current': current_report,
            'previous': previous_report,
            'last_updated': report_record.last_updated.isoformat()
        }})

    except openai.APIError as e:
        print(f"SiliconFlow API 返回错误: {e}")
        return jsonify({'code': 500, 'message': f'AI服务返回错误: {e.status_code}'}), 500
    except json.JSONDecodeError as e:
        print(f"解析AI返回的JSON失败: {e}")
        print(f"原始返回内容: {ai_response_content}")
        return jsonify({'code': 500, 'message': 'AI返回的数据格式无法解析'}), 500
    except Exception as e:
        print(f"AI分析失败: {e}")
        return jsonify({'code': 500, 'message': 'AI分析服务暂时不可用'}), 500


# ======================================================================
# 9. 分析与统计 API (Analysis & Statistics) - 新增模块
# ======================================================================

@app.route('/analysis/daily_submissions', methods=['GET'])
@token_required
def get_daily_submissions(current_user):
    """统计最近7天每日的作业提交量"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '只有教师可以查看统计'}), 403

    # 1. 准备日期标签 (最近7天)
    today = datetime.date.today()
    date_labels = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    # 2. 获取当前教师的所有课程ID
    course_ids = [c.id for c in current_user.courses_taught]

    # 3. 按天统计作业提交量
    submission_counts = []
    if course_ids:
        for date_str in date_labels:
            day_start = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            day_end = day_start + datetime.timedelta(days=1)

            # 找到属于该教师课程下的所有作业ID
            assignment_ids = [a.id for a in Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()]

            if assignment_ids:
                # 统计在指定日期范围内，这些作业的提交数量
                count = Submission.query.filter(
                    Submission.assignment_id.in_(assignment_ids),
                    Submission.submission_date >= day_start,
                    Submission.submission_date < day_end
                ).count()
                submission_counts.append(count)
            else:
                submission_counts.append(0)
    else:
        submission_counts = [0] * 7  # 如果没有课程，则每天都是0

    # 4. 准备X轴标签 (月-日)
    xaxis_labels = [datetime.datetime.strptime(d, '%Y-%m-%d').strftime('%m-%d') for d in date_labels]

    data = {
        'xaxis_labels': xaxis_labels,
        'submission_data': submission_counts
    }

    return jsonify({'code': 20000, 'data': data})


# ======================================================================
# 6. 作业提交管理 (Submission Management) - 新增模块
# ======================================================================

@app.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@token_required
def get_submissions_by_assignment(current_user, assignment_id):
    """获取指定作业的【全班学生】提交状态列表"""
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return jsonify({'code': 404, 'message': '作业不存在'}), 404

    # 安全检查 (保持不变)
    if current_user.role == 'teacher' and assignment.course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '无权访问'}), 403

    # --- ↓↓↓ 核心逻辑重构 ↓↓↓ ---

    # 1. 获取该作业所属课程的【所有】学生
    course_students = assignment.course.students.order_by(User.id).all()
    if not course_students:
        return jsonify({'code': 20000, 'data': {'items': []}})  # 如果课程没有学生，返回空列表

    # 2. 一次性获取该作业的所有提交记录，并存入一个字典以便快速查找
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    submissions_map = {sub.student_id: sub for sub in submissions}

    # 3. 遍历【全班学生名单】，为每个学生构建状态信息
    student_status_list = []
    for student in course_students:
        # 尝试从字典中获取该学生的提交记录
        submission = submissions_map.get(student.id)

        # 根据是否存在提交记录来决定状态
        if submission:
            # 如果找到了提交记录
            status = submission.status  # 'submitted' 或 'graded'
            submission_id = submission.id
            submission_date = submission.submission_date.strftime(
                '%Y-%m-%d %H:%M') if submission.submission_date else None
            grade = submission.grade
        else:
            # 如果没找到，说明该学生【未提交】
            status = 'unsubmitted'
            submission_id = None
            submission_date = None
            grade = None

        student_status_list.append({
            'student_id': student.id,
            'student_name': student.username,
            'status': status,
            'submission_id': submission_id,
            'submission_date': submission_date,
            'grade': grade
        })
    # --- ↑↑↑ 逻辑重构结束 ↑↑↑ ---

    return jsonify({'code': 20000, 'data': {'items': student_status_list}})


@app.route('/submissions/<int:submission_id>', methods=['GET'])
@token_required
def get_submission_detail(current_user, submission_id):
    """获取单个提交的详情"""
    submission = db.session.get(Submission, submission_id)
    if not submission:
        return jsonify({'code': 404, 'message': '提交记录不存在'}), 404

    # 安全检查：确保教师只能查看自己课程下的提交
    if current_user.role == 'teacher' and submission.assignment.course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '无权访问此提交'}), 403

    return jsonify({'code': 20000, 'data': {
        'submission_id': submission.id,
        'student_name': submission.student.username,
        'assignment_title': submission.assignment.title,
        'content': submission.content,
        'grade': submission.grade,
        'status': submission.status
    }})


# --- ↓↓↓ (可选，但推荐) 添加一个用于批改/打分的接口 ↓↓↓ ---
@app.route('/submissions/<int:submission_id>/grade', methods=['POST'])
@token_required
def grade_submission(current_user, submission_id):
    """为一次提交打分"""
    submission = db.session.get(Submission, submission_id)
    if not submission:
        return jsonify({'code': 404, 'message': '提交记录不存在'}), 404

    if current_user.role != 'teacher' or submission.assignment.course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '无权批改此作业'}), 403

    data = request.get_json()
    grade = data.get('grade')

    if grade is None or not isinstance(grade, (int, float)) or not 0 <= grade <= 100:
        return jsonify({'code': 400, 'message': '无效的分数'}), 400

    submission.grade = grade
    submission.status = 'graded'  # 打分后自动将状态更新为“已批改”
    db.session.commit()

    return jsonify({'code': 20000, 'message': '批改成功'})


# ======================================================================
# 课程选修 (Course Enrollment) - 新增
# ======================================================================


@app.route('/courses/enroll', methods=['POST'])
@token_required
def enroll_course(current_user):
    """学生选课/退课接口"""
    if current_user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生才能进行此操作'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '缺少请求数据'}), 400

    course_id = data.get('course_id')
    action = data.get('action')  # 'enroll' (选课) or 'drop' (退课)

    if not course_id or not action:
        return jsonify({'code': 400, 'message': '缺少 course_id 或 action 参数'}), 400

    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在'}), 404

    # 检查学生是否已经选了这门课
    # 使用 .filter() 会比 .all() 更高效，因为它只检查存在性
    is_enrolled = current_user.enrolled_courses.filter(Course.id == course_id).count() > 0

    print(f"学生 {current_user.username} 正在对课程 '{course.name}' 执行 '{action}' 操作。当前选课状态: {is_enrolled}")

    if action == 'enroll':
        if is_enrolled:
            print(f"操作失败：学生已选该课程，无法重复选择。")
            return jsonify({'code': 400, 'message': '您已选择该课程，请勿重复操作'}), 400
        # 将课程添加到学生的已选课程列表中
        current_user.enrolled_courses.append(course)
        message = '选课成功'
        print(f"操作成功：已为学生添加课程。")

    elif action == 'drop':
        if not is_enrolled:
            print(f"操作失败：学生未选该课程，无法退课。")
            return jsonify({'code': 400, 'message': '您未选择该课程，无法退课'}), 400
        # 从学生的已选课程列表中移除该课程
        current_user.enrolled_courses.remove(course)
        message = '退课成功'
        print(f"操作成功：已为学生移除课程。")

    else:
        return jsonify({'code': 400, 'message': '无效的操作'}), 400

    # 提交数据库会话以保存更改
    db.session.commit()
    return jsonify({'code': 20000, 'message': message})



@app.route('/student/assignments', methods=['GET'])
@token_required
def get_student_assignments(current_user):
    """获取当前登录学生的所有作业列表，支持按课程筛选和排序"""
    if current_user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生才能访问'}), 403

    # 1. 获取所有 URL 参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort = request.args.get('sort', '+due_date')  # 默认按截止日期升序
    course_id = request.args.get('course_id', None, type=int)

    # 2. 获取学生已选的所有课程ID
    enrolled_course_ids = {c.id for c in current_user.enrolled_courses}

    if not enrolled_course_ids:
        # 如果学生没选课，直接返回空列表
        return jsonify({'code': 20000, 'data': {'total': 0, 'items': []}})

    # 3. 根据是否传入 course_id，确定要查询的课程范围
    target_course_ids = enrolled_course_ids
    if course_id:
        if course_id in enrolled_course_ids:
            target_course_ids = {course_id}
        else:
            return jsonify({'code': 20000, 'data': {'total': 0, 'items': []}})

    # 4. 在确定的课程范围内查询所有作业
    query = Assignment.query.filter(Assignment.course_id.in_(target_course_ids))

    # 5. 应用排序逻辑，并处理 NULL 值
    if sort == '-due_date':
        # 按截止日期降序，将 NULL 值排在最后
        query = query.order_by(Assignment.due_date.desc().nulls_last())
    elif sort == '+due_date':
        # 按截止日期升序，将 NULL 值排在最后
        query = query.order_by(Assignment.due_date.asc().nulls_last())
    elif sort == '-course':
        query = query.join(Course).order_by(Course.name.desc())
    elif sort == '+course':
        query = query.join(Course).order_by(Course.name.asc())
    else:  # 默认按ID升序
        query = query.order_by(Assignment.id.asc())

    # 6. 获取该学生的所有提交记录，存入字典以便快速查找
    # 为了优化，我们先获取分页后的作业ID
    paginated_query_ids = [a.id for a in query.paginate(page=page, per_page=limit, error_out=False).items]
    submissions = Submission.query.filter(
        Submission.student_id == current_user.id,
        Submission.assignment_id.in_(paginated_query_ids)
    ).all()
    submissions_map = {sub.assignment_id: sub for sub in submissions}

    # 7. 执行分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    assignments = pagination.items
    total = pagination.total

    # 8. 构建返回列表
    items = []
    for assignment in assignments:
        submission = submissions_map.get(assignment.id)
        status = 'pending'  # 待完成
        if submission:
            status = submission.status  # 'submitted' (已提交) 或 'graded' (已批改)
        elif assignment.due_date and datetime.datetime.utcnow() > assignment.due_date:
            status = 'expired'  # 已过期

        items.append({
            'id': assignment.id,
            'title': assignment.title,
            'course_name': assignment.course.name,
            # ✅ 正确：加上 %
'due_date': assignment.due_date.strftime('%Y-%m-%d %H:%M') if assignment.due_date else None,
            'status': status
        })

    return jsonify({'code': 20000, 'data': {'total': total, 'items': items}})


@app.route('/student/assignments/<int:assignment_id>/submission-detail', methods=['GET'])
@token_required
def get_student_submission_for_assignment(current_user, assignment_id):
    """获取学生针对某个作业的提交详情（包括作业本身的信息）"""
    if current_user.role != 'student':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return jsonify({'code': 404, 'message': '作业不存在'}), 404

    # 检查学生是否选了该作业所属的课程
    if assignment.course not in current_user.enrolled_courses:
        return jsonify({'code': 403, 'message': '您未选修该课程'}), 403

    # 查找学生之前的提交记录
    submission = Submission.query.filter_by(
        student_id=current_user.id,
        assignment_id=assignment.id
    ).first()

    return jsonify({'code': 20000, 'data': {
        # 作业信息
        'assignment': {
            'id': assignment.id,
            'title': assignment.title,
            'content': assignment.content,
            'due_date': assignment.due_date.strftime('%Y-%m-%d %H:%M') if assignment.due_date else 'N/A'
        },
        # 提交信息 (如果存在)
        'submission': {
            'id': submission.id,
            'content': submission.content,
            'submission_date': submission.submission_date.strftime(
                '%Y-%m-%d %H:%M') if submission.submission_date else None,
            'grade': submission.grade,
            'status': submission.status
        } if submission else None
    }})


# --- ↓↓↓ 在这里添加新的作业提交接口 ↓↓↓ ---
@app.route('/student/assignments/<int:assignment_id>/submit', methods=['POST'])
@token_required
def submit_assignment(current_user, assignment_id):
    """学生提交或更新作业"""
    if current_user.role != 'student':
        return jsonify({'code': 403, 'message': '只有学生才能提交作业'}), 403

    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return jsonify({'code': 404, 'message': '作业不存在'}), 404

    # --- ↓↓↓ 核心修改：增加截止日期检查 ↓↓↓ ---
    if assignment.due_date and datetime.datetime.utcnow() > assignment.due_date:
        return jsonify({'code': 400, 'message': '该作业已超过截止日期，无法提交'}), 400

    # 检查学生是否选了该作业所属的课程
    if assignment.course not in current_user.enrolled_courses.all():
        return jsonify({'code': 403, 'message': '您未选修该课程，无法提交作业'}), 403

    data = request.get_json()
    content = data.get('content')
    if content is None:
        return jsonify({'code': 400, 'message': '提交内容不能为空'}), 400

    # 查找是否已有提交记录
    existing_submission = Submission.query.filter_by(
        student_id=current_user.id,
        assignment_id=assignment.id
    ).first()

    if existing_submission:
        # 如果是已批改的作业，理论上不允许再修改
        if existing_submission.status == 'graded':
            return jsonify({'code': 400, 'message': '作业已被批改，无法修改'}), 400

        # 更新现有提交
        existing_submission.content = content
        existing_submission.submission_date = datetime.datetime.utcnow()
        existing_submission.status = 'submitted'  # 确保状态是“已提交”
        message = '作业更新成功'
    else:
        # 创建新的提交记录
        new_submission = Submission(
            content=content,
            student_id=current_user.id,
            assignment_id=assignment.id
        )
        db.session.add(new_submission)
        message = '作业提交成功'

    db.session.commit()
    return jsonify({'code': 20000, 'message': message})


# ======================================================================
# 9. AI 辅助学习 (AI-Powered Learning)
# ======================================================================
# app.py


def fix_json_with_ai(bad_json_string):
    """(辅助函数) 使用 AI 来修复损坏的 JSON 字符串"""
    print("尝试使用 AI 修复 JSON...")
    try:
        fix_prompt = f"""
        以下是一个损坏的、无法被解析的 JSON 字符串。请修复它，确保它是一个完全合法有效的 JSON 格式。
        只返回修复后的纯净 JSON 内容，不要添加任何解释或 markdown 标记。

        损坏的 JSON:
        {bad_json_string}
        """
        client = openai.OpenAI(api_key=app.config['SILICONFLOW_API_KEY'], base_url="https://api.siliconflow.cn/v1")
        completion = client.chat.completions.create(
            model="alibaba/Qwen2-7B-Instruct",  # 使用一个快速、便宜的模型来做修复
            messages=[{"role": "user", "content": fix_prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"AI 修复 JSON 失败: {e}")
        return None  # 返回 None 表示修复失败

# ======================================================================
# 9. AI 辅助学习 (AI-Powered Learning)
# ======================================================================



@app.route('/ai/generate-quiz', methods=['POST'])
@token_required
def generate_quiz(current_user):
    """
    为学生生成新的练习题，并为每道题创建一条练习记录存入数据库。(健壮版+角色支持)
    """
    # [修改] 定义一个包含所有允许角色的列表
    allowed_roles = ['student', 'teacher']

    # [修改] 判断当前用户的角色是否不在允许的列表里
    if current_user.role not in allowed_roles:
        # 如果当前用户的角色既不是 'student' 也不是 'teacher'，则拒绝访问
        return jsonify({'code': 403, 'message': '您没有权限访问此功能'}), 403

    data = request.get_json()
    course_name = data.get('course_name')
    topic = data.get('topic')
    # 接收 role_id 参数
    role_id = data.get('role_id')

    # 默认出3道题
    count = 3

    if not course_name or not topic:
        return jsonify({'code': 400, 'message': '必须提供课程和主题'}), 400

    # 1. 构建 System Prompt (加强版 + 角色植入)
    role_instruction = ""
    if role_id:
        # 假设您的 SQLAlchemy 实例对象名为 db
        role = db.session.get(GradingRole, role_id)
        if role:
            # 把角色风格注入进去，比如“出题要难一点”、“多出代码题”
            role_instruction = f"你的出题风格请参考此角色设定：{role.description}。\n具体要求：{role.prompt_content}"

    system_prompt = f"""
你是一个专业的教辅系统后端API。你的唯一任务是生成练习题数据。
{role_instruction}

【绝对强制输出规则】：
1. 你必须且只能返回 **纯标准 JSON 数组**。
2. **严禁**使用 Markdown 代码块（不要写 ```json ... ```）。
3. **严禁**在 JSON 前后添加任何解释性文字、问候语或总结。
4. 请仔细检查 JSON 语法：
   - 字符串必须用双引号 `"` 包裹。
   - 键值对之间要有逗号 `,`。
   - 数组最后一个元素后不能有逗号。

【JSON 数据结构示例】：
[
  {{
    "type": "选择题",
    "question": "题目内容...",
    "options": {{ "A": "...", "B": "..." }},
    "answer": "A",
    "explanation": "解析..."
  }},
  {{
    "type": "简答题",
    "question": "题目内容...",
    "answer": "参考答案...",
    "explanation": "解析..."
  }}
]
"""

    # 2. 构建 User Prompt
    user_prompt = f"""
课程：{course_name}
主题：{topic}
数量：{count} 道题

请根据主题生成题目。如果角色设定有特殊要求（如难度、题型），请优先满足角色设定。
否则默认生成：2道选择题 + 1道简答题。
确保所有内容（包括选项Key）都是合法的 JSON 字符串。
"""

    try:
        # 调用 AI API (保持你原有的 client 配置)
        client = openai.OpenAI(
            api_key=app.config['SILICONFLOW_API_KEY'],
            base_url="https://api.siliconflow.cn/v1"
        )

        completion = client.chat.completions.create(
            # 建议用 instruction 指令遵循能力更强的模型
            model="alibaba/Qwen2-7B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7  # 稍微降低随机性，保证 JSON 格式稳定
        )
        ai_response_content = completion.choices[0].message.content

        # --- 多层健壮的JSON清理和解析逻辑 (保留你的代码) ---

        # 1. 清理 Markdown 代码块标记
        cleaned_str = ai_response_content.strip()
        if cleaned_str.startswith("```json"):
            cleaned_str = cleaned_str[len("```json"):].strip()
        elif cleaned_str.startswith("```"):  # 有时候 AI 只写 ```
            cleaned_str = cleaned_str[len("```"):].strip()

        if cleaned_str.endswith("```"):
            cleaned_str = cleaned_str[:-3].strip()

        quiz_list_from_ai = None
        try:
            # 2. 第一次尝试直接解析
            quiz_list_from_ai = json.loads(cleaned_str)
        except json.JSONDecodeError:
            # 3. 如果失败，尝试移除所有换行符和回车符后再次解析
            print("直接解析失败，尝试移除换行符后重试...")
            repaired_str = cleaned_str.replace("\n", "").replace("\r", "")
            try:
                quiz_list_from_ai = json.loads(repaired_str)
            except json.JSONDecodeError as e:
                print(f"修复后解析依然失败: {e}")
                # 4. (新增) 终极尝试：有时候 AI 会忘记加闭合的 ]
                if cleaned_str.strip().startswith("[") and not cleaned_str.strip().endswith("]"):
                    try:
                        quiz_list_from_ai = json.loads(cleaned_str + "]")
                        print("通过补全末尾 ] 修复成功")
                    except:
                        raise e
                else:
                    raise e

        if not quiz_list_from_ai:
            raise json.JSONDecodeError("无法从AI响应中解析出JSON", cleaned_str, 0)

        # --- JSON解析成功，开始处理数据库 ---

        new_records = []
        for quiz_data in quiz_list_from_ai:
            # 简单的校验：确保必须有 question 字段
            if 'question' not in quiz_data:
                continue

            record = PracticeRecord(
                student_id=current_user.id,
                quiz_data=quiz_data
            )
            new_records.append(record)

        db.session.add_all(new_records)
        db.session.commit()

        # 构造返回给前端的数据
        response_data = []
        for record in new_records:
            quiz_item = record.quiz_data
            quiz_item['record_id'] = record.id
            response_data.append(quiz_item)

        return jsonify({'code': 20000, 'data': response_data})

    except (openai.APIError, json.JSONDecodeError) as e:
        print(f"AI出题或解析失败: {e}")
        if 'ai_response_content' in locals():
            print(f"原始返回内容: {ai_response_content}")
        return jsonify({'code': 500, 'message': 'AI生成的数据格式有误，请重试'}), 500
    except Exception as e:
        print(f"AI出题时发生未知错误: {e}")
        return jsonify({'code': 500, 'message': 'AI服务发生未知错误'}), 500



@app.route('/ai/practice-history', methods=['GET'])
@token_required
def get_practice_history(current_user):
     # [修改] 定义一个包含所有允许角色的列表
    allowed_roles = ['student', 'teacher']

    # [修改] 判断当前用户的角色是否不在允许的列表里
    if current_user.role not in allowed_roles:
        # 如果当前用户的角色既不是 'student' 也不是 'teacher'，则拒绝访问
        return jsonify({'code': 403, 'message': '您没有权限访问此功能'}), 403

    # 按练习日期降序排序，获取最近的记录
    # 假设一次出题数量不固定，我们通过时间戳来分组
    latest_record = PracticeRecord.query.filter_by(student_id=current_user.id) \
        .order_by(PracticeRecord.practice_date.desc()).first()

    if not latest_record:
        return jsonify({'code': 20000, 'data': []})

    # 获取与最近一条记录时间戳非常接近（比如5秒内）的所有记录
    time_threshold = latest_record.practice_date - datetime.timedelta(seconds=5)
    latest_practice_session = PracticeRecord.query.filter(
        PracticeRecord.student_id == current_user.id,
        PracticeRecord.practice_date >= time_threshold
    ).order_by(PracticeRecord.id).all()

    history_quizzes = []
    for record in latest_practice_session:
        quiz = record.quiz_data
        quiz['user_answer'] = record.user_answer
        quiz['ai_grade'] = record.ai_grade
        quiz['ai_feedback'] = record.ai_feedback
        quiz['record_id'] = record.id
        history_quizzes.append(quiz)

    return jsonify({'code': 20000, 'data': history_quizzes})




# --- ↓↓↓ 新增：保存练习记录 API ↓↓↓ ---
@app.route('/ai/save-practice', methods=['POST'])
@token_required
def save_practice_record(current_user):
    if current_user.role != 'student': return jsonify({'code': 403, 'message': '...'})
    data = request.get_json()
    record = PracticeRecord(
        student_id=current_user.id,
        quiz_question=data.get('question'),
        quiz_type=data.get('type'),
        user_answer=data.get('answer')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'code': 20000, 'message': '练习记录已保存'})


# --- ↓↓↓ 新增：题目收藏/取消收藏 API ↓↓↓ ---
@app.route('/ai/favorite-quiz', methods=['POST'])
@token_required
def favorite_quiz(current_user):
    # [修改] 定义一个包含所有允许角色的列表
    allowed_roles = ['student', 'teacher']

    # [修改] 判断当前用户的角色是否不在允许的列表里
    if current_user.role not in allowed_roles:
        # 如果当前用户的角色既不是 'student' 也不是 'teacher'，则拒绝访问
        return jsonify({'code': 403, 'message': '您没有权限访问此功能'}), 403

    data = request.get_json()
    action = data.get('action', 'add')
    raw_quiz_data = data.get('quiz_data')

    if not raw_quiz_data:
        return jsonify({'code': 400, 'message': '缺少题目数据'}), 400

    # =======================================================
    # 1. 【核心修复】标准化 JSON 字符串
    # sort_keys=True 保证 {"a":1, "b":2} 和 {"b":2, "a":1} 生成的字符串完全一样
    # ensure_ascii=False 保证中文不会变成 \uXXXX，防止编码差异
    # =======================================================
    target_quiz_str = json.dumps(raw_quiz_data, sort_keys=True, ensure_ascii=False)

    # 2. 先把该用户的所有收藏取出来（在内存里比对最稳妥）
    user_favorites = FavoriteQuiz.query.filter_by(student_id=current_user.id).all()

    # 3. 寻找匹配的记录
    target_record = None
    for fav in user_favorites:
        # 获取数据库里的数据
        db_data = fav.quiz_data

        # 如果数据库存的是字符串，先转回字典
        if isinstance(db_data, str):
            try:
                db_data = json.loads(db_data)
            except:
                continue  # 数据损坏，跳过

        # 同样标准化数据库里的数据
        db_data_str = json.dumps(db_data, sort_keys=True, ensure_ascii=False)

        # 精确比对字符串
        if db_data_str == target_quiz_str:
            target_record = fav
            break

    # =======================================================
    # 逻辑处理
    # =======================================================
    if action == 'add':
        if target_record:
            return jsonify({'code': 20000, 'message': '已在收藏夹中'})

        # 存入数据库
        # 注意：建议直接存 raw_quiz_data (字典)，SQLAlchemy 会自动处理 JSON 类型
        new_fav = FavoriteQuiz(student_id=current_user.id, quiz_data=raw_quiz_data)
        db.session.add(new_fav)
        message = '题目收藏成功'

    elif action == 'remove':
        if target_record:
            # 找到记录了，删除！
            db.session.delete(target_record)
            message = '已取消收藏'
        else:
            # 如果依然找不到，尝试一种兜底策略：只比对 question 字段
            # 这是为了防止有些旧数据 JSON 结构对不上
            target_question = raw_quiz_data.get('question', '').strip()
            fallback_record = None
            if target_question:
                for fav in user_favorites:
                    # 取出 DB 里的 question
                    db_q = fav.quiz_data
                    if isinstance(db_q, str): db_q = json.loads(db_q)
                    if db_q.get('question', '').strip() == target_question:
                        fallback_record = fav
                        break

            if fallback_record:
                db.session.delete(fallback_record)
                message = '已取消收藏 (模糊匹配)'
            else:
                # 真的找不到了，就当做已经取消了吧，不然用户会很困惑
                return jsonify({'code': 20000, 'message': '收藏夹中未找到该题目，可能已取消'})

    else:
        return jsonify({'code': 400, 'message': '无效的操作'}), 400

    db.session.commit()
    return jsonify({'code': 20000, 'message': message})


# --- ↑↑↑ 新增结束 ↑↑↑ ---

# --- ↓↓↓ 新增：获取收藏列表 API ↓↓↓ ---
@app.route('/ai/favorites', methods=['GET'])
@token_required
def get_favorite_quizzes(current_user):
    """获取收藏的题目列表（学生和老师均可访问）""" # <-- 建议同时更新注释

    # [修改] 定义一个包含所有允许角色的列表
    allowed_roles = ['student', 'teacher']

    # [修改] 判断当前用户的角色是否不在允许的列表里
    if current_user.role not in allowed_roles:
        # 如果当前用户的角色既不是 'student' 也不是 'teacher'，则拒绝访问
        return jsonify({'code': 403, 'message': '您没有权限访问此功能'}), 403

    # 后续的查询逻辑保持不变
    favorites = FavoriteQuiz.query.filter_by(student_id=current_user.id).order_by(FavoriteQuiz.id.desc()).all()

    # 从记录中提取出题目的 JSON 数据
    quiz_list = [fav.quiz_data for fav in favorites]

    return jsonify({'code': 20000, 'data': {'items': quiz_list}})


# --- ↑↑↑ 新增结束 ↑↑↑ ---


@app.route('/ai/grade-practice/<int:record_id>', methods=['POST'])
@token_required
def ai_grade_practice(current_user, record_id):
    """使用 AI 批改学生提交的练习答案 (已集成AI角色系统)"""

    # 1. 获取基础数据和记录
    record = db.session.get(PracticeRecord, record_id)
    if not record:  # 老师也可以代学生提交和测试，因此不校验 student_id
        return jsonify({'code': 404, 'message': '练习记录不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    user_answer = data.get('user_answer')
    role_id = data.get('role_id')  # [新增] 从请求体中获取 role_id

    # 2. 核心数据校验
    if user_answer is None:
        return jsonify({'code': 400, 'message': '答案内容不能为空'}), 400
    if role_id is None:
        return jsonify({'code': 400, 'message': '必须指定一个AI角色 (role_id)'}), 400

    # [新增] 根据 role_id 查询AI角色
    role = db.session.get(GradingRole, role_id)
    if not role:
        return jsonify({'code': 404, 'message': '指定的AI角色不存在'}), 404

    # 更新学生答案到记录中
    record.user_answer = user_answer

    # 3. [修改] 动态构建 Prompt
    # 系统指令：定义AI的人格和背景，来自我们数据库中的角色内容
    system_prompt = role.prompt_content

    # 用户指令：定义本次 конкрет任务的具体内容和格式要求
    user_prompt = f"""
    请根据以下信息，对学生的回答进行批改。

    # 题目信息:
    {json.dumps(record.quiz_data, ensure_ascii=False, indent=2)}

    # 学生的回答:
    {user_answer}

    # 批改要求:
    1.  **评分 (grade)**: 根据学生答案的正确性、完整性和思路，给出一个0-100的整数分数。
    2.  **评语 (feedback)**: 给出一段具体的评语。如果答案正确，予以表扬；如果答案有误或不完整，请明确指出错误在哪里，并提供正确的思路或代码片段作为提示。不要直接给出完整答案。

    # 输出格式:
    请严格按照以下JSON格式返回，不要包含任何额外的解释或```json标记:
    {{
      "grade": <0-100的整数>,
      "feedback": "<评语文本>"
    }}
    """

    try:
        # 4. 调用大模型 API
        client = openai.OpenAI(
            api_key=app.config['SILICONFLOW_API_KEY'],
            base_url="https://api.siliconflow.cn/v1"
        )
        completion = client.chat.completions.create(
            model="alibaba/Qwen2-7B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},  # [修改] 使用动态的角色内容
                {"role": "user", "content": user_prompt}  # [修改] 使用具体的任务指令
            ],
            response_format={"type": "json_object"}  # [推荐] 使用新版的 JSON mode，让模型强制输出JSON
        )
        ai_response_content = completion.choices[0].message.content

        # 5. 解析和保存结果
        grading_result = json.loads(ai_response_content)

        record.ai_grade = grading_result.get('grade')
        record.ai_feedback = grading_result.get('feedback')

        # 6. [新增] 记录角色调用日志！
        log_entry = RoleCallLog(role_id=role.id, user_id=current_user.id)
        db.session.add(log_entry)

        # 统一提交所有数据库更改
        db.session.commit()

        return jsonify({'code': 20000, 'data': grading_result})

    except (openai.APIError, json.JSONDecodeError) as e:
        db.session.rollback()  # 发生错误时回滚数据库
        print(f"AI 批改或解析失败: {e}")
        if 'ai_response_content' in locals():
            print(f"原始返回内容: {ai_response_content}")
        return jsonify({'code': 500, 'message': 'AI批改服务暂时不可用或返回格式错误'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"AI 批改时发生未知错误: {e}")
        return jsonify({'code': 500, 'message': 'AI 批改服务发生未知错误'}), 500


# --- ↓↓↓ 在这里，补上这个缺失的、用于保存答案的接口 ↓↓↓ ---
@app.route('/ai/practice-record/<int:record_id>', methods=['PUT'])
@token_required
def update_practice_answer(current_user, record_id):
    """保存或更新学生对某道练习题的答案"""
    record = db.session.get(PracticeRecord, record_id)

    # 安全检查
    if not record or record.student_id != current_user.id:
        return jsonify({'code': 404, 'message': '练习记录不存在'}), 404

    data = request.get_json()
    user_answer = data.get('user_answer')

    # 更新数据库中的答案字段
    record.user_answer = user_answer
    db.session.commit()

    return jsonify({'code': 20000, 'message': '答案已保存'})



# --- ↓↓↓ 新增：获取雷达图数据 API ↓↓↓ ---
# app.py -> 替换 get_course_radar_data 函数

@app.route('/analysis/course_radar', methods=['GET'])
@token_required
def get_course_radar_data(current_user):
    """为教师仪表盘提供课程雷达图数据，支持'self'和'all'两种范围"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    # --- ↓↓↓ 核心修改：获取范围参数并决定查询对象 ↓↓↓ ---
    scope = request.args.get('scope', 'self')  # 从URL获取scope参数，默认为'self'

    # 根据范围确定要查询的课程列表
    if scope == 'all':
        # 如果请求查看所有课程
        courses = Course.query.order_by(Course.id).all()
        # 为了对比，我们也需要拿到当前老师的课程ID
        current_teacher_course_ids = {c.id for c in current_user.courses_taught}
    else:  # scope == 'self'
        # 默认只看自己的课程
        courses = current_user.courses_taught
    # --- ↑↑↑ 修改结束 ↑↑↑ ---

    if not courses:
        return jsonify({'code': 20000, 'data': {'indicator': [], 'series_data': []}})

    # --- ↓↓↓ 核心修改：构建指示器时，增加特殊标记 ↓↓↓ ---
    # 如果是查看所有课程，给自己的课程名加上特殊标记
    indicator = []
    for course in courses:
        name = course.name
        if scope == 'all' and course.id in current_teacher_course_ids:
            name = f"{name} (我的)"  # 给自己的课程加上后缀
        indicator.append({'name': name, 'max': 100})
    # --- ↑↑↑ 修改结束 ↑↑↑ ---

    # (后续的计算逻辑与您提供的版本完全一样)
    student_engagement = []
    assignment_coverage = []
    ai_integration = []
    max_students = 0
    max_assignments = 0

    for course in courses:
        student_count = course.students.count()
        assignment_count = course.assignments.count()
        student_engagement.append(student_count)
        assignment_coverage.append(assignment_count)
        ai_score = 5 if any(
            keyword in (course.name + course.description).lower() for keyword in ['ai', 'prompt']) else 0
        ai_integration.append(ai_score + assignment_count)
        if student_count > max_students: max_students = student_count
        if assignment_count > max_assignments: max_assignments = assignment_count

    def normalize(data, max_val, weight):
        if max_val == 0: return [0] * len(data)
        return [min(round((val / max_val) * 100 * weight), 100) for val in data]

    series_data = [
        {'value': normalize(student_engagement, max_students, 1.0), 'name': '学生热度'},
        {'value': normalize(assignment_coverage, max_assignments, 1.2), 'name': '内容丰富度'},
        {'value': normalize(ai_integration, (5 + max_assignments), 1.5), 'name': 'AI结合度'}
    ]

    return jsonify({'code': 20000, 'data': {'indicator': indicator, 'series_data': series_data}})


# --- ↓↓↓ 新增：获取饼图数据 API ↓↓↓ ---
@app.route('/analysis/course_student_pie', methods=['GET'])
@token_required
def get_course_student_pie_data(current_user):
    """为教师仪表盘提供各课程学生人数分布饼图数据"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    # 查询当前教师的所有课程
    courses = current_user.courses_taught

    pie_data = []
    for course in courses:
        student_count = course.students.count()
        # 只有当课程有学生选修时，才加入到饼图中
        if student_count > 0:
            pie_data.append({
                'name': course.name,
                'value': student_count
            })

    return jsonify({'code': 20000, 'data': pie_data})


# --- ↓↓↓ 新增：获取学生详情 API ↓↓↓ ---
@app.route('/students/<int:student_id>/profile', methods=['GET'])
@token_required
def get_student_profile(current_user, student_id):
    """获取单个学生的详细信息、已选课程和提交记录"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '只有教师有权查看学生详情'}), 403

    student = db.session.get(User, student_id)
    if not student or student.role != 'student':
        return jsonify({'code': 404, 'message': '学生不存在'}), 404

    # 获取学生已选课程
    enrolled_courses = [{
        'id': c.id,
        'name': c.name,
        'teacher_name': c.teacher.username
    } for c in student.enrolled_courses]

    # 获取学生所有提交记录
    submissions = [{
        'id': s.id,
        'assignment_title': s.assignment.title,
        'course_name': s.assignment.course.name,
        'submission_date': s.submission_date.strftime('%Y-%m-%d %H:%M'),
        'status': s.status,
        'grade': s.grade
    } for s in student.submissions]

    data = {
        'id': student.id,
        'name': student.username,
        'enrolled_courses': enrolled_courses,
        'submissions': submissions
    }

    return jsonify({'code': 20000, 'data': data})




@app.route('/ai/dashboard/analysis', methods=['GET'])
@token_required
def get_dashboard_analysis(current_user):
    if current_user.role != 'student':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    # ==========================
    # 1. 卡片数据 (Card Data) - 保持原样
    # ==========================
    course_count = current_user.enrolled_courses.count()
    submitted_count = Submission.query.filter_by(student_id=current_user.id).count()

    enrolled_course_ids = [c.id for c in current_user.enrolled_courses.all()]
    if not enrolled_course_ids:
        total_assignments = 0
    else:
        total_assignments = Assignment.query.filter(Assignment.course_id.in_(enrolled_course_ids)).count()
    pending_count = max(0, total_assignments - submitted_count)

    total_practices = PracticeRecord.query.filter_by(student_id=current_user.id).count()
    total_favorites = FavoriteQuiz.query.filter_by(student_id=current_user.id).count()

    # 计算平均分
    all_scores = db.session.query(PracticeRecord.ai_grade).filter(
        PracticeRecord.student_id == current_user.id,
        PracticeRecord.ai_grade != None
    ).all()
    valid_scores = []
    for s in all_scores:
        try:
            val = s[0]
            if isinstance(val, int):
                valid_scores.append(val)
            elif isinstance(val, str):
                nums = re.findall(r"\d+", val)
                if nums: valid_scores.append(int(nums[0]))
        except:
            continue
    avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0

    # ==========================
    # 2. 图表数据 - 核心修改：只用真实数据
    # ==========================
    dates = []

    # 真实数据 A: 每天的 AI 练习数
    daily_ai_practices = []

    # 真实数据 B: 每天的 作业提交数
    daily_submissions = []

    # 兼容你的导入方式
    today = datetime.datetime.now().date()

    for i in range(6, -1, -1):
        target_day = today - datetime.timedelta(days=i)
        dates.append(target_day.strftime('%m-%d'))

        # --- 查询 1: 当天 AI 练习数 ---
        ai_count = PracticeRecord.query.filter(
            PracticeRecord.student_id == current_user.id,
            func.date(PracticeRecord.practice_date) == target_day
        ).count()
        daily_ai_practices.append(ai_count)

        # --- 查询 2: 当天 作业提交数 ---
        sub_count = Submission.query.filter(
            Submission.student_id == current_user.id,
            func.date(Submission.submission_date) == target_day
        ).count()
        daily_submissions.append(sub_count)

        # =======================================================
        # 3. 新增：雷达图数据 (Radar Data) - 基于已有变量计算
        # =======================================================
        # 维度1: 作业完成率
    total_tasks = pending_count + submitted_count
    radar_completion = round((submitted_count / total_tasks * 100), 1) if total_tasks > 0 else 0

    # 维度2: AI 平均分 (复用 avg_score)

    # 维度3: 活跃度 (相对值，假设总操作100次算满分)
    radar_activity = min(100, (submitted_count + total_practices))

    # 维度4: 课程广度 (假设选5门课满分)
    radar_breadth = min(100, (course_count / 5) * 100)

    # 维度5: 收藏活跃度 (假设收藏20个满分)
    radar_fav = min(100, (total_favorites / 20) * 100)

    # 对应前端 RadarChart 的 indicator 顺序
    radar_values = [radar_completion, avg_score, radar_activity, radar_breadth, radar_fav]

    # =======================================================
    # 4. 新增：饼图数据 (Pie Data) - 题目类型分布
    # =======================================================
    all_records = PracticeRecord.query.filter_by(student_id=current_user.id).all()
    type_counts = {}
    for r in all_records:
        try:
            # 解析 quiz_data (可能是字符串或字典)
            q_data = r.quiz_data
            if isinstance(q_data, str):
                q_data = json.loads(q_data)

            # 统计类型 (选择题/简答题)
            q_type = q_data.get('type', '其他')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        except:
            pass

    pie_data = [{"name": k, "value": v} for k, v in type_counts.items()]
    if not pie_data:
        pie_data = [{"name": "暂无数据", "value": 0}]

    # =======================================================
    # 5. 新增：柱状图数据 (Bar Data) - 成绩段分布
    # =======================================================
    score_dist = {
        "不及格": 0,
        "及格": 0,
        "良好": 0,
        "优秀": 0
    }
    # 复用之前算好的 valid_scores 列表
    for score in valid_scores:
        if score < 60:
            score_dist["不及格"] += 1
        elif score < 75:
            score_dist["及格"] += 1
        elif score < 90:
            score_dist["良好"] += 1
        else:
            score_dist["优秀"] += 1

    bar_x = list(score_dist.keys())
    bar_y = list(score_dist.values())

    # =======================================================
    # 6. 最终返回 (整合所有数据)
    # =======================================================
    data = {
        'card_data': {
            'courseCount': course_count,
            'pendingCount': pending_count,
            'submittedCount': submitted_count,
            'total_practices': total_practices,
            'avg_score': avg_score,
            'total_favorites': total_favorites,
            'today_count': daily_ai_practices[-1]
        },
        # 注意：为了配合新的 index.vue，这里将折线图数据放入 'line_data' 键中
        'line_data': {
            'dates': dates,
            'ai_practices': daily_ai_practices,
            'homework_submissions': daily_submissions
        },
        'radar_data': radar_values,
        'pie_data': pie_data,
        'bar_data': {
            'x_axis': bar_x,
            'y_axis': bar_y
        }
    }

    return jsonify({'code': 20000, 'data': data})


# 在 app.py 或单独的脚本中运行
@app.cli.command("init-prompts")
def init_prompts():
    """初始化系统提示词模板"""
    templates = [
        {
            "name": "关键词采分助手",
            "description": "严格按照老师提供的关键词和分数点进行打分，适合简答题。",
            "content": """你是一位公正的阅卷老师。请根据以下[评分标准]对[学生回答]进行打分。

【作业题目】: {question}
【评分标准/得分点】: {criteria}

【学生回答】: {student_answer}

请严格遵守以下规则：
1. 如果学生回答中包含了评分标准里的关键词或意思相近的表述，给予相应分数。
2. 总分不超过100分（或题目满分）。
3. 输出格式必须为JSON，包含 'score' (数字) 和 'reason' (评语)。
"""
        },
        {
            "name": "创意/作文点评助手",
            "description": "关注逻辑、文采和完整性，评分较为人性化。",
            "content": """你是一位资深的语文/英语老师。请评价学生的作文/主观题。

【题目要求】: {question}
【老师要求的重点】: {criteria}

【学生回答】: {student_answer}

请给出评分（0-100）和详细的改进建议。
输出JSON格式: {"score": 0, "reason": "..."}
"""
        }
    ]

    for t in templates:
        exists = PromptTemplate.query.filter_by(name=t['name']).first()
        if not exists:
            pt = PromptTemplate(name=t['name'], description=t['description'], template_content=t['content'],
                                is_system=True)
            db.session.add(pt)

    db.session.commit()
    print("系统提示词初始化完成！")





# 假设你有一个调用大模型的方法 call_llm_api(prompt)

@app.route('/ai/grade-submission/<int:submission_id>', methods=['POST'])
@token_required
def ai_grade_submission(current_user, submission_id):
    # 1. 获取提交记录、作业信息
    submission = Submission.query.get_or_404(submission_id)
    assignment = submission.assignment

    # 2. 获取老师设置的评分标准
    criteria = assignment.grading_criteria or "请根据题目内容，判断回答的准确性。"

    # 3. 选择一个提示词模板 (这里简化为默认使用“关键词采分助手”，实际可以存assignment时指定template_id)
    # 实际项目中，你应该在 Assignment 表里存一个 prompt_template_id
    template = PromptTemplate.query.filter_by(name="关键词采分助手").first()
    if not template:
        return jsonify({'code': 500, 'message': '未找到评分模板'}), 500

    # 4. 【Prompt Engineering 核心】拼接最终提示词
    # 使用 Python 的 format 方法替换占位符
    final_prompt = template.template_content.format(
        question=assignment.content,
        criteria=criteria,
        student_answer=submission.content
    )

    # 5. 调用大模型
    try:
        # 这里模拟调用 LLM，你需要替换成真实的 API 调用 (如 OpenAI, 文心一言等)
        # llm_response_text = call_llm_api(final_prompt)

        # --- 模拟 AI 返回 (假装 AI 根据 criteria 算了分) ---
        # 实际开发中，这里是 LLM 的真实返回
        print(f"发送给AI的提示词:\n{final_prompt}")

        # 假设 AI 返回了 JSON
        ai_result = {
            "score": 85,
            "reason": "学生回答涵盖了主要关键词，但在细节描述上略有欠缺。符合评分标准中'核心概念正确'的要求。"
        }
        # -----------------------------------------------

        # 6. 保存分数和评语
        submission.grade = ai_result['score']
        submission.status = 'graded'
        # 如果 Submission 表里没评语字段，建议加一个 feedback 字段
        # submission.feedback = ai_result['reason']

        db.session.commit()

        return jsonify({'code': 20000, 'message': 'AI评分完成', 'data': ai_result})

    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'message': 'AI服务暂时不可用'}), 500


@app.cli.command("init-roles")
def init_roles():
    roles = [
        {
            "name": "标准助教 (系统默认)",
            "description": "基于作业的标准答案进行客观评分，关注关键词命中率。",
            "content": """你现在是【标准助教】。请根据作业内容进行客观打分。
评分规则：
1. 关键词命中：每命中一个核心关键词得 10 分。
2. 逻辑准确性：满分 100 分。
3. 请指出具体的错误点。
"""
        },
        {
            "name": "苏格拉底 (系统默认)",
            "description": "不直接给出分数，而是通过提问引导学生思考（启发式）。",
            "content": """你现在是【苏格拉底】。你不需要给出一个确切的分数，或者只给一个模糊的等级（优/良/差）。
你的主要任务是：
1. 发现学生逻辑中的漏洞。
2. 用反问句引导学生自己发现错误。
3. 语气要充满智慧且谦逊。
"""
        }
    ]
    for r in roles:
        if not GradingRole.query.filter_by(name=r['name']).first():
            role = GradingRole(name=r['name'], description=r['description'], prompt_content=r['content'],
                               is_system=True)
            db.session.add(role)
    db.session.commit()
    print("系统角色初始化完成")




# 3. 教师创建/更新角色接口
@app.route('/ai/role/save', methods=['POST'])
@token_required
def save_grading_role(current_user):
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '只有教师可以创建评分角色'}), 403

    data = request.get_json()
    role_id = data.get('id')

    if role_id:
        # 更新
        role = GradingRole.query.get(role_id)
        if role.creator_id != current_user.id:
            return jsonify({'code': 403, 'message': '无权修改此角色'}), 403
        role.name = data.get('name')
        role.description = data.get('description')
        role.prompt_content = data.get('prompt_content')
    else:
        # 创建
        role = GradingRole(
            name=data.get('name'),
            description=data.get('description'),
            prompt_content=data.get('prompt_content'),  # 这就是那个单独的文本
            is_system=False,
            creator_id=current_user.id
        )
        db.session.add(role)

    db.session.commit()
    return jsonify({'code': 20000, 'message': '角色保存成功'})


@app.route('/ai/practice/submit', methods=['POST'])
@token_required
def submit_practice_answer(current_user):
    """
    学生提交AI练习答案，系统根据选定的角色进行评分
    """
    data = request.get_json()
    question = data.get('question')  # 题目内容
    user_answer = data.get('answer')  # 学生写的答案
    role_id = data.get('role_id')  # ✅ 关键：学生选择的角色ID

    if not question or not user_answer:
        return jsonify({'code': 400, 'message': '参数不完整'}), 400

    # 1. 确定 AI 的人设（System Prompt）
    system_instruction = ""

    if role_id:
        # 如果学生选了角色，去数据库查这个角色的“独家文本”
        role = GradingRole.query.get(role_id)
        if role:
            system_instruction = role.prompt_content
        else:
            # 容错：没找到就用默认
            system_instruction = "你是一个智能助教，请根据题目和答案进行客观打分。"
    else:
        # 没选角色，用默认兜底
        system_instruction = "你是一个智能助教，请根据题目和答案进行客观打分。"

    # 2. 组装发给大模型的最终 Prompt
    # 这里将角色设定、题目、学生答案拼在一起
    user_prompt = f"""
【题目】：{question}
【学生回答】：{user_answer}

请根据你的角色设定对上述回答进行评分和点评。
要求返回JSON格式：
{{
    "score": 0-100之间的数字,
    "feedback": "你的评语"
}}
"""

    # 3. 调用大模型 (伪代码，请替换为你真实的 LLM 调用逻辑)
    # response = call_llm(system_prompt=system_instruction, user_prompt=user_prompt)

    # --- ↓↓↓ 模拟 AI 返回 (假数据用于测试) ↓↓↓ ---
    print(f"--- 正在使用角色: {role_id} 进行评分 ---")
    print(f"--- 系统提示词(System Prompt): \n{system_instruction}")

    # 这里模拟不同角色会有不同反应
    simulated_score = 85
    simulated_feedback = "回答得不错，但还可以更详细。"

    if "苏格拉底" in system_instruction:
        simulated_feedback = "你的回答很有趣，但你有没有想过，如果情况发生了变化，这个结论还成立吗？"
    elif "严厉" in system_instruction:
        simulated_score = 70
        simulated_feedback = "语法不仅要正确，逻辑也要严密！这里有一个明显的逻辑漏洞。"
    # ---------------------------------------------

    # 4. 保存练习记录
    record = PracticeRecord(
        student_id=current_user.id,
        quiz_data={"question": question},  # 存题目
        user_answer=user_answer,
        ai_grade=simulated_score,
        ai_feedback=simulated_feedback
        # 最好在 PracticeRecord 模型里也加一个 role_id 字段记录当时用了哪个角色
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'code': 20000,
        'data': {
            'score': simulated_score,
            'feedback': simulated_feedback
        }
    })


# ======================================================================
# 1. 将文件同步逻辑封装成一个独立的辅助函数
# ======================================================================
def sync_system_roles_from_files():
    """
    将 ai_roles 文件夹中的文件同步为数据库中的系统角色。
    这个函数可以在应用启动时调用，或者在需要时手动调用。
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        roles_dir = os.path.join(base_dir, 'ai_roles')

        if not os.path.exists(roles_dir):
            print(f"角色目录不存在，跳过同步: {roles_dir}")
            return

        files = os.listdir(roles_dir)
        for filename in files:
            # 过滤掉隐藏文件
            if filename.startswith('.'):
                continue

            file_path = os.path.join(roles_dir, filename)
            if not os.path.isfile(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]

                    if len(lines) < 3:
                        print(f"警告：文件 {filename} 内容格式不正确，至少需要3行。")
                        continue

                    role_name, role_desc = lines[0], lines[1]
                    role_prompt = "\n".join(lines[2:])

                    # 查找或创建系统角色
                    existing_role = GradingRole.query.filter_by(name=role_name, is_system=True).first()

                    if not existing_role:
                        new_role = GradingRole(
                            name=role_name,
                            description=role_desc,
                            prompt_content=role_prompt,
                            is_system=True
                        )
                        db.session.add(new_role)
                        print(f"--- [新增角色] 从文件 '{filename}' 导入: {role_name}")
                    # 如果描述或核心Prompt有变动，则更新
                    elif existing_role.description != role_desc or existing_role.prompt_content != role_prompt:
                        existing_role.description = role_desc
                        existing_role.prompt_content = role_prompt
                        print(f"--- [更新角色] 从文件 '{filename}' 更新: {role_name}")

            except Exception as e:
                print(f"处理文件 {filename} 时发生错误: {e}")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"同步系统角色时发生严重错误: {e}")


# ======================================================================
# 2. 改造API端点，让其职责更单一
# ======================================================================
@app.route('/ai/roles', methods=['GET'])
@token_required
def get_ai_roles(current_user):  # current_user 参数依然保留，因为 token_required 装饰器会传入它
    """
    获取系统中所有的AI角色列表。
    """
    # 步骤一：同步文件中的系统角色到数据库（可选，但推荐保留）
    sync_system_roles_from_files()

    try:
        # 步骤二：从数据库查询所有角色，不进行任何过滤
        # ✅✅✅ 这是关键的修改点 ✅✅✅
        roles_query = GradingRole.query

        # 按照“系统角色优先，然后按ID升序”的顺序排列
        roles = roles_query.order_by(GradingRole.is_system.desc(), GradingRole.id.asc()).all()

        # 步骤三：格式化数据并返回
        data = [{
            'id': r.id,
            'name': r.name,
            'description': r.description
        } for r in roles]

        return jsonify({'code': 20000, 'data': data})

    except Exception as e:
        print(f"查询AI角色时出错: {e}")
        return jsonify({'code': 50000, 'message': '获取角色列表失败'}), 500
# backend/app.py

@app.route('/ai/prompts/list', methods=['GET'])
@token_required
def get_prompts_list(current_user):
    # 查询所有角色，系统内置的排在前面
    roles = GradingRole.query.order_by(GradingRole.is_system.desc(), GradingRole.id.asc()).all()

    return jsonify({
        'code': 20000,
        'data': [r.to_dict() for r in roles]
    })



@app.route('/ai/teacher/roles/stats', methods=['GET'])
@token_required
def get_teacher_roles_stats(current_user):
    """获取当前教师所创建角色的累计调用统计"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '仅限教师访问'}), 403

    # 1. 首先，获取当前教师创建的所有角色的 ID 列表
    teacher_role_ids = [role.id for role in GradingRole.query.filter_by(creator_id=current_user.id).all()]

    # 如果教师没有任何角色，直接返回空数据
    if not teacher_role_ids:
        return jsonify({'code': 20000, 'data': {
            'total_all_time_calls': 0,
            'calls_by_role': {}
        }})

    # 2. 计算这些角色的累计调用总次数
    total_calls = db.session.query(func.count(RoleCallLog.id)).filter(
        RoleCallLog.role_id.in_(teacher_role_ids)
    ).scalar() or 0

    # 3. 按角色分组，计算每个角色的调用次数
    calls_by_role_query = db.session.query(
        RoleCallLog.role_id,
        func.count(RoleCallLog.id).label('call_count')
    ).filter(
        RoleCallLog.role_id.in_(teacher_role_ids)
    ).group_by(RoleCallLog.role_id).all()

    # 将查询结果转换为 {role_id: count} 的字典格式，方便前端使用
    calls_by_role_dict = {role_id: count for role_id, count in calls_by_role_query}

    # 4. 组装并返回最终数据
    stats_data = {
        'total_all_time_calls': total_calls,
        'calls_by_role': calls_by_role_dict
    }

    return jsonify({'code': 20000, 'data': stats_data})

# --- ↑↑↑ 新增结束 ↑↑↑ ---

@app.route('/ai/teacher/roles', methods=['GET'])
@token_required
def get_teacher_roles(current_user):
    """[修正] 获取当前登录教师自己创建的所有角色列表"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '仅限教师访问'}), 403

    # [修正] 核心修改：查询条件从宽泛的OR查询，改为精确的 creator_id 匹配
    # 这确保了教师只能看到自己创建的角色。
    roles = GradingRole.query.filter_by(creator_id=current_user.id).order_by(GradingRole.id.desc()).all()

    return jsonify({'code': 20000, 'data': [role.to_dict() for role in roles]})


@app.route('/ai/teacher/roles', methods=['POST'])
@token_required
def create_teacher_role(current_user):
    """教师创建一个新的 AI 角色 (逻辑无变化)"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '仅限教师创建角色'}), 403

    data = request.get_json()
    if not data or not data.get('name') or not data.get('description'):
        return jsonify({'code': 400, 'message': '角色名称和描述不能为空'}), 400

    new_role = GradingRole(
        name=data['name'],
        description=data['description'],
        prompt_content=data.get('content', ''),
        creator_id=current_user.id,  # 关联到当前教师
        is_system=False
    )
    db.session.add(new_role)
    db.session.commit()
    return jsonify({'code': 20000, 'message': '创建成功', 'data': new_role.to_dict()})


@app.route('/ai/teacher/roles/<int:role_id>', methods=['PUT'])
@token_required
def update_teacher_role(current_user, role_id):
    """[修正] 教师更新一个自己创建的 AI 角色"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '仅限教师编辑'}), 403

    role = db.session.get(GradingRole, role_id)
    if not role:
        return jsonify({'code': 404, 'message': '角色不存在'}), 404

    # [修正] 增加严格的权限校验：确保教师只能编辑自己的角色
    if role.creator_id != current_user.id:
        return jsonify({'code': 403, 'message': '您无权编辑此角色'}), 403

    data = request.get_json()
    role.name = data.get('name', role.name)
    role.description = data.get('description', role.description)
    role.prompt_content = data.get('content', role.prompt_content)

    db.session.commit()
    return jsonify({'code': 20000, 'message': '更新成功', 'data': role.to_dict()})


@app.route('/ai/teacher/roles/<int:role_id>', methods=['DELETE'])
@token_required
def delete_teacher_role(current_user, role_id):
    """[修正] 教师删除一个自己创建的 AI 角色"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '仅限教师删除'}), 403

    role = db.session.get(GradingRole, role_id)
    if not role:
        return jsonify({'code': 404, 'message': '角色不存在'}), 404

    # [修正] 增加严格的权限校验：确保教师只能删除自己的角色
    if role.creator_id != current_user.id:
        return jsonify({'code': 403, 'message': '您无权删除此角色'}), 403

    # is_system 的检查可以保留作为双重保险，但逻辑上 creator_id 存在时 is_system 应为 False
    if role.is_system:
        return jsonify({'code': 400, 'message': '不能删除系统内置角色'}), 400

    db.session.delete(role)
    db.session.commit()
    return jsonify({'code': 20000, 'message': '删除成功'})

# --- ↓↓↓ [新增] 删除单份作业提交的 API 接口 ↓↓↓ ---


@app.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@token_required
def delete_assignment(current_user, assignment_id):
    """删除一个作业及其所有提交记录"""
    # 1. 基础权限校验：必须是教师
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '您没有权限执行此操作'}), 403

    # 2. 查找作业
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return jsonify({'code': 404, 'message': '作业不存在'}), 404

    # 3. [至关重要] 身份校验：确保当前教师是该作业所属课程的授课教师
    if assignment.course.teacher_id != current_user.id:
        return jsonify({'code': 403, 'message': '您只能删除自己课程下的作业'}), 403

    # 4. 执行删除
    # 假设您的 Assignment 和 Submission 模型之间设置了级联删除 (cascade="all, delete-orphan")
    # 那么删除 assignment 会自动删除所有关联的 submission
    db.session.delete(assignment)
    db.session.commit()

    return jsonify({'code': 20000, 'message': '作业及所有提交记录已成功删除'})


@app.route('/ai/teacher/roles/daily-stats', methods=['GET'])
@token_required
def get_teacher_daily_stats(current_user):
    """获取当前教师创建的AI角色在过去7天内每日的调用次数统计"""
    if current_user.role != 'teacher':
        return jsonify({'code': 403, 'message': '仅限教师访问'}), 403

    teacher_roles = GradingRole.query.filter_by(creator_id=current_user.id).all()
    if not teacher_roles:
        return jsonify({'code': 20000, 'data': {'dates': [], 'series': []}})

    teacher_role_map = {role.id: role.name for role in teacher_roles}
    teacher_role_ids = list(teacher_role_map.keys())

    today = datetime.date.today()
    dates_list_objects = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    date_labels = [d.strftime('%m-%d') for d in dates_list_objects]

    start_date = today - datetime.timedelta(days=6)

    query_result = db.session.query(
        func.date(RoleCallLog.created_at).label('call_date'),
        RoleCallLog.role_id,
        func.count(RoleCallLog.id).label('count')
    ).filter(
        RoleCallLog.created_at >= start_date,
        RoleCallLog.role_id.in_(teacher_role_ids)
    ).group_by('call_date', RoleCallLog.role_id).all()

    processed_data = {}
    for call_date_str, role_id, count in query_result:  # [修改] 变量名改为 call_date_str
        # [修改] 直接使用从数据库返回的日期字符串 call_date_str
        # 不再需要 .strftime()

        # 将其转换为字符串以确保一致性 (即使它已经是字符串)
        date_str = str(call_date_str)

        if role_id not in processed_data:
            processed_data[role_id] = {}
        processed_data[role_id][date_str] = count

    series_data = []
    for role_id, role_name in teacher_role_map.items():
        role_series = {
            'name': role_name,
            'type': 'bar',
            'stack': 'total',
            'barWidth': '60%',
            'emphasis': {'focus': 'series'},
            'data': []
        }
        # [修改] 这里遍历的是日期对象列表
        for d in dates_list_objects:
            # 将日期对象格式化为 'YYYY-MM-DD' 字符串以匹配 processed_data 中的键
            date_str = d.strftime('%Y-%m-%d')
            count = processed_data.get(role_id, {}).get(date_str, 0)
            role_series['data'].append(count)

        series_data.append(role_series)

    response_data = {
        'dates': date_labels,
        'series': series_data
    }
    return jsonify({'code': 20000, 'data': response_data})




# ======================================================================
# 7. 主程序入口 (Main Entry)
# ======================================================================

if __name__ == '__main__':
    app.run(debug=True)