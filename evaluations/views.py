from django.shortcuts import get_object_or_404, redirect, render
from .models import EvaluationTask, EvaluationResult, Answer
from .forms import EvaluationForm
from .views_teacher import course_results, course_grading
from .views_student import select_courses, enroll_course, teacher_leaderboard, vote_teacher, export_teacher_votes, historical_evaluations, student_schedule, my_grades
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

@login_required
def student_tasks(request):
    if request.user.user_type != 'student':
        return redirect('dashboard')
    
    student = request.user.student
    
    # 获取该学生所选课程的所有评价任务
    # 1. 找到学生选的课
    enrolled_courses = student.courses.all()
    
    # 2. 找到这些课的评价任务，且当前时间在任务起止时间内，且任务是激活状态
    now = timezone.now()
    tasks = EvaluationTask.objects.filter(
        course__in=enrolled_courses,
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    )
    
    # 3. 标记哪些任务已经完成
    # 获取该学生已提交的所有 EvaluationResult 的 task_id 列表
    completed_task_ids = EvaluationResult.objects.filter(student=student).values_list('task_id', flat=True)
    
    # 构建包含状态的任务列表
    task_list = []
    for task in tasks:
        is_completed = task.id in completed_task_ids
        task_list.append({
            'task': task,
            'is_completed': is_completed
        })
        
    return render(request, 'student_tasks.html', {'task_list': task_list})

@login_required
def evaluate_task(request, task_id):
    # 仅学生可访问
    if request.user.user_type != 'student':
        return redirect('dashboard')

    task = get_object_or_404(EvaluationTask, id=task_id, is_active=True)
    student = request.user.student

    # 检查是否已经提交过
    if EvaluationResult.objects.filter(student=student, task=task).exists():
        return redirect('student_tasks')

    # 获取该任务关联的问卷的所有问题，按 order 排序
    questions = task.questionnaire.questions.all().order_by('order')

    if request.method == 'POST':
        form = EvaluationForm(request.POST, questions=questions)
        if form.is_valid():
            # 创建评价结果记录
            result = EvaluationResult.objects.create(
                student=student,
                task=task,
                is_anonymous=request.POST.get('anonymous') == 'on'  # 复选框勾选时值为 'on'
            )
            # 保存每个问题的答案
            for q in questions:
                field_name = f'q_{q.id}'
                value = form.cleaned_data[field_name]
                # 对于多选题，value 是一个列表，需要转换为可 JSON 序列化的格式
                if q.question_type == 'multiple':
                    value = list(value)  # 将 QuerySet 转换为列表
                Answer.objects.create(
                    result=result,
                    question=q,
                    answer_content=value
                )
            messages.success(request, '评价提交成功！')
            return redirect('student_tasks')
    else:
        form = EvaluationForm(questions=questions)

    return render(request, 'evaluate.html', {'form': form, 'task': task})