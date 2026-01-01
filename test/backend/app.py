import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Course, Assignment, Submission, Prompt,AnalysisReport
from flask_migrate import Migrate
import openai
import json
import requests
import json
import time


app = Flask(__name__)
app.config.from_object(Config)

# 初始化
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)


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


# ======================================================================
# 4. 课程管理 (Course Management)
# ======================================================================

@app.route('/courses', methods=['GET'])
@token_required
def get_courses(current_user):
    """获取课程列表（分页）"""
    page, limit = request.args.get('page', 1, type=int), request.args.get('limit', 20, type=int)
    query = Course.query.filter_by(teacher_id=current_user.id) if current_user.role == 'teacher' else Course.query
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return jsonify({'code': 20000, 'data': {
        'total': pagination.total,
        'items': [{'id': c.id, 'name': c.name, 'teacher_name': c.teacher.username, 'student_count': c.students.count(),
                   'description': c.description} for c in pagination.items]
    }})


@app.route('/courses/list', methods=['GET'])
@token_required
def get_course_list(current_user):
    """获取教师的课程下拉列表"""
    if current_user.role != 'teacher': return jsonify({'code': 403, 'message': '权限不足'}), 403
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return jsonify({'code': 20000, 'data': {'items': [{'id': c.id, 'name': c.name} for c in courses]}})


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




# ======================================================================
# 6. 开发辅助 (Development Helper)
# ======================================================================

@app.cli.command("seed")
def seed():
    """清空并填充数据库测试数据"""
    print("正在清空数据库...")
    db.drop_all()
    db.create_all()
    print("正在创建测试数据...")
    teacher_li = User(username='teacher_li', role='teacher');
    teacher_li.set_password('123456')
    teacher_wang = User(username='teacher_wang', role='teacher');
    teacher_wang.set_password('123456')
    student_zhang = User(username='student_zhang', role='student');
    student_zhang.set_password('123456')
    student_zhao = User(username='student_zhao', role='student');
    student_zhao.set_password('123456')
    db.session.add_all([teacher_li, teacher_wang, student_zhang, student_zhao]);
    db.session.commit()
    course_prompt = Course(name='提示词工程入门', teacher=teacher_li)
    course_python = Course(name='Python编程基础', teacher=teacher_wang)
    db.session.add_all([course_prompt, course_python]);
    db.session.commit()
    course_prompt.students.append(student_zhang)
    course_python.students.append(student_zhao)
    assignment1 = Assignment(title='第一周作业', course=course_prompt,
                             due_date=datetime.datetime.utcnow() + datetime.timedelta(days=7))
    assignment2 = Assignment(title='Python基础练习', course=course_python,
                             due_date=datetime.datetime.utcnow() + datetime.timedelta(days=5))
    db.session.add_all([assignment1, assignment2]);
    db.session.commit()
    prompt1 = Prompt(title='分析性提示词模板', content='请分析...', teacher=teacher_li)
    db.session.add(prompt1);
    db.session.commit()
    submission1 = Submission(content='这是张三对第一周作业的回答', student=student_zhang, assignment=assignment1,
                             status='submitted')
    db.session.add(submission1);
    db.session.commit()
    print("测试数据创建完成！")



@app.route('/students', methods=['GET'])
@token_required
def get_students(current_user):
    """获取学生列表，支持按课程ID筛选和分页"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    course_id = request.args.get('course_id', type=int)

    query = User.query.filter_by(role='student')

    # 如果传入了 course_id，则只查询该课程下的学生
    if course_id:
        course = db.session.get(Course, course_id)
        if course:
            # 安全检查：确保教师只能查询自己课程下的学生
            if current_user.role == 'teacher' and course.teacher_id != current_user.id:
                return jsonify({'code': 403, 'message': '无权访问该课程的学生列表'}), 403
            query = course.students

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    students = pagination.items
    total = pagination.total

    items = []
    for student in students:
        items.append({
            'id': student.id,
            'name': student.username,
            'enrolled_course_count': student.enrolled_courses.count(), # 已选课程数
            'submission_count': len(student.submissions) # 已提交作业数
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
        analysis_data_str += (
            f"- 作业:{sub.assignment.title}, 课程:{sub.assignment.course.name}, "
            f"提交于:{sub.submission_date.strftime('%Y-%m-%d')}, 成绩:{sub.grade if sub.grade is not None else '未批改'}\n"
        )

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
# 7. 主程序入口 (Main Entry)
# ======================================================================

if __name__ == '__main__':
    app.run(debug=True)