from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from users.models import Teacher
from courses.models import Course, Score
from .models import TeacherVote, EvaluationResult, EvaluationTask
import csv
import json

@login_required
def select_courses(request):
    """
    学生选课页面
    """
    if request.user.user_type != 'student':
        return redirect('dashboard')
        
    student = request.user.student
    
    # 获取学期筛选参数
    semester_query = request.GET.get('semester')
    
    # 获取所有课程
    all_courses = Course.objects.all().prefetch_related('teachers')
    
    # 筛选学期
    if semester_query:
        all_courses = all_courses.filter(semester=semester_query)
        
    # 获取所有可用的学期供筛选
    semesters = Course.objects.values_list('semester', flat=True).distinct().order_by('-semester')
    
    # 区分已选和未选
    enrolled_ids = student.courses.values_list('id', flat=True)
    
    available_courses = []
    enrolled_courses_list = []
    
    for course in all_courses:
        if course.id in enrolled_ids:
            enrolled_courses_list.append(course)
        else:
            available_courses.append(course)
            
    return render(request, 'select_courses.html', {
        'available_courses': available_courses,
        'enrolled_courses': enrolled_courses_list,
        'semesters': semesters,
        'current_semester': semester_query
    })

@login_required
def enroll_course(request, course_id):
    """
    处理选课请求
    """
    if request.user.user_type != 'student':
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student
    
    # 添加关联
    if course not in student.courses.all():
        student.courses.add(course)
        messages.success(request, f'成功选修课程：{course.course_name}')
    
    return redirect('select_courses')

@login_required
def teacher_leaderboard(request):
    """
    教师排行榜
    """
    # 获取所有教师及其得票数
    teachers = Teacher.objects.annotate(vote_count=Count('votes')).order_by('-vote_count')
    
    # Chart.js 数据准备
    labels = [t.name for t in teachers]
    data = [t.vote_count for t in teachers]
    
    # 检查当前用户是否已投票（仅限学生）
    has_voted = False
    if request.user.user_type == 'student':
        try:
            student = request.user.student
            has_voted = TeacherVote.objects.filter(student=student).exists()
        except:
            pass
        
    return render(request, 'teacher_leaderboard.html', {
        'teachers': teachers,
        'labels_json': json.dumps(labels),
        'data_json': json.dumps(data),
        'has_voted': has_voted,
        'user_type': request.user.user_type
    })

@login_required
def vote_teacher(request):
    """
    处理投票请求
    """
    if request.user.user_type != 'student':
        return redirect('teacher_leaderboard')
        
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        if not teacher_id:
            return redirect('teacher_leaderboard')
            
        try:
            student = request.user.student
            
            # 检查是否已投票
            if TeacherVote.objects.filter(student=student).exists():
                return redirect('teacher_leaderboard')
            
            # 使用 pk 查询更安全
            teacher = get_object_or_404(Teacher, pk=teacher_id)
            TeacherVote.objects.create(student=student, teacher=teacher)
            messages.success(request, f'成功投票给：{teacher.name} 老师')
        except Exception as e:
            print(f"Vote error: {e}")
            pass
        
    return redirect('teacher_leaderboard')

@login_required
def export_teacher_votes(request):
    """
    导出教师得票数据
    """
    if request.user.user_type not in ['teacher', 'admin']:
        return redirect('dashboard')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teacher_votes.csv"'
    response.write('\ufeff'.encode('utf8')) # BOM for Excel
    
    writer = csv.writer(response)
    writer.writerow(['工号', '姓名', '得票数'])
    
    teachers = Teacher.objects.annotate(vote_count=Count('votes')).order_by('-vote_count')
    for teacher in teachers:
        writer.writerow([teacher.teacher_id, teacher.name, teacher.vote_count])
        
    return response

@login_required
def historical_evaluations(request):
    """
    学生查看历史评价记录
    """
    if request.user.user_type != 'student':
        return redirect('dashboard')
        
    student = request.user.student
    
    # 获取该学生提交的所有评价结果
    results = EvaluationResult.objects.filter(student=student).select_related('task', 'task__course').order_by('-submit_time')
    
    return render(request, 'historical_evaluations.html', {
        'results': results
    })

@login_required
def student_schedule(request):
    """
    学生课表可视化
    """
    if request.user.user_type != 'student':
        return redirect('dashboard')
        
    student = request.user.student
    courses = student.courses.all()
    
    # 初始化课表数据结构
    # schedule[time_slot][week_day] = course
    # 行是节次，列是星期
    schedule = {}
    for slot in range(1, 6):
        schedule[slot] = {}
        for day in range(1, 8):
            schedule[slot][day] = None
            
    # 填充课表
    for course in courses:
        if course.week_day and course.time_slot:
            schedule[course.time_slot][course.week_day] = course
            
    # 元数据
    week_days = [
        (1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'), (5, '周五'), (6, '周六'), (7, '周日')
    ]
    time_slots = [
        (1, '第1-2节 (08:00-09:35)'),
        (2, '第3-4节 (09:55-11:30)'),
        (3, '第5-6节 (13:30-15:05)'),
        (4, '第7-8节 (15:25-17:00)'),
        (5, '第9-10节 (18:30-20:05)'),
    ]
    
    # 转换为列表格式方便模板遍历
    schedule_rows = []
    for slot_num, slot_name in time_slots:
        row = {'slot_name': slot_name, 'courses': []}
        for day_num, day_name in week_days:
            course = schedule.get(slot_num, {}).get(day_num)
            row['courses'].append(course)
        schedule_rows.append(row)
    
    return render(request, 'student_schedule.html', {
        'schedule_rows': schedule_rows,
        'week_days': week_days,
    })

@login_required
def my_grades(request):
    """
    学生查看成绩
    """
    if request.user.user_type != 'student':
        return redirect('dashboard')
        
    student = request.user.student
    
    # 获取学期筛选参数
    semester_query = request.GET.get('semester')
    
    # 获取所有已选课程
    courses = student.courses.all()
    
    # 筛选学期
    if semester_query:
        courses = courses.filter(semester=semester_query)
        
    # 获取所有可用的学期供筛选
    semesters = student.courses.values_list('semester', flat=True).distinct().order_by('-semester')
    
    # 获取成绩记录
    scores = Score.objects.filter(student=student, course__in=courses).select_related('course')
    
    grade_data = []
    
    for course in courses:
        score = scores.filter(course=course).first()
        grade_data.append({
            'course': course,
            'score': score
        })
        
    # 导出功能
    if request.GET.get('export') == 'true':
        response = HttpResponse(content_type='text/csv')
        filename = f"my_grades_{semester_query if semester_query else 'all'}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write('\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        writer.writerow(['课程代码', '课程名称', '学期', '学分', '平时成绩', '期末成绩', '总评成绩', '绩点'])
        
        for item in grade_data:
            course = item['course']
            score = item['score']
            
            total_score = score.total_score if score else ''
            gp = 0.0
            if total_score:
                if total_score >= 90: gp = 4.0
                elif total_score >= 85: gp = 3.7
                elif total_score >= 82: gp = 3.3
                elif total_score >= 78: gp = 3.0
                elif total_score >= 75: gp = 2.7
                elif total_score >= 72: gp = 2.3
                elif total_score >= 68: gp = 2.0
                elif total_score >= 64: gp = 1.5
                elif total_score >= 60: gp = 1.0
                else: gp = 0.0
            
            writer.writerow([
                course.course_code,
                course.course_name,
                course.semester,
                course.credit or '',
                score.regular_score if score else '',
                score.final_score if score else '',
                total_score,
                gp if total_score else ''
            ])
        return response
        
    return render(request, 'my_grades.html', {
        'grade_data': grade_data,
        'semesters': semesters,
        'current_semester': semester_query
    })
