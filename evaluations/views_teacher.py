from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import EvaluationTask, EvaluationResult, Answer
from django.db.models import Count
from courses.models import Course, Score
from django.contrib import messages
import json
from decimal import Decimal

@login_required
def course_results(request, course_id):
    # 仅教师和管理员可访问
    if request.user.user_type not in ['teacher', 'admin']:
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    
    # 如果是教师，必须是该课程的授课教师
    if request.user.user_type == 'teacher':
        # 这里需要从 Teacher 模型反查关联的用户
        try:
            teacher = request.user.teacher
            if not course.teachers.filter(teacher_id=teacher.teacher_id).exists():
                 # 实际上应该用 user 对象来判断，或者 teacher 对象本身
                 if not course.teachers.filter(user=request.user).exists():
                     return redirect('dashboard')
        except:
            return redirect('dashboard')

    # 获取该课程的所有评价任务
    tasks = EvaluationTask.objects.filter(course=course)
    
    results_data = []
    
    for task in tasks:
        # 获取该任务的所有评价结果
        eval_results = EvaluationResult.objects.filter(task=task)
        count = eval_results.count()
        
        questions = task.questionnaire.questions.all().order_by('order') if task.questionnaire_id else []
        
        question_stats = []
        for q in questions:
            # 统计每个选项的选择次数
            answers = Answer.objects.filter(question=q, result__in=eval_results)
            
            if q.question_type in ['single', 'scale', 'multiple']:
                # 构建分布数据用于图表
                distribution = {}
                for ans in answers:
                    val = ans.answer_content
                    # 如果是多选，val 可能是列表，需要展开统计
                    if isinstance(val, list):
                        for v in val:
                            distribution[str(v)] = distribution.get(str(v), 0) + 1
                    else:
                        distribution[str(val)] = distribution.get(str(val), 0) + 1
                
                # 转换为 Chart.js 需要的格式
                labels = list(distribution.keys())
                data = list(distribution.values())
                
                question_stats.append({
                    'question': q,
                    'type': 'chart',
                    'chart_id': f'chart_{task.id}_{q.id}',
                    'labels_json': json.dumps(labels),
                    'data_json': json.dumps(data)
                })
            elif q.question_type == 'text':
                # 收集文本反馈
                feedbacks = [a.answer_content for a in answers if a.answer_content]
                question_stats.append({
                    'question': q,
                    'type': 'text',
                    'feedbacks': feedbacks
                })
                
        results_data.append({
            'task': task,
            'count': count,
            'question_stats': question_stats
        })
        
    return render(request, 'course_results.html', {'course': course, 'results_data': results_data})

@login_required
def course_grading(request, course_id):
    """
    教师评分页面
    """
    # 仅教师和管理员可访问
    if request.user.user_type not in ['teacher', 'admin']:
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    
    # 如果是教师，必须是该课程的授课教师
    if request.user.user_type == 'teacher':
        try:
            teacher = request.user.teacher
            if not course.teachers.filter(teacher_id=teacher.teacher_id).exists():
                 if not course.teachers.filter(user=request.user).exists():
                     return redirect('dashboard')
        except:
            return redirect('dashboard')
            
    students = course.students.all().order_by('student_id')
    
    # 获取现有成绩
    scores_map = {}
    for score in Score.objects.filter(course=course):
        scores_map[score.student.student_id] = score
        
    if request.method == 'POST':
        try:
            # 更新权重
            regular_weight = request.POST.get('regular_weight')
            final_weight = request.POST.get('final_weight')
            
            if regular_weight and final_weight:
                # 转换为 Decimal
                course.regular_weight = Decimal(str(regular_weight))
                course.final_weight = Decimal(str(final_weight))
                course.save()
            
            # 更新学生成绩
            for student in students:
                sid = student.student_id
                regular = request.POST.get(f'regular_{sid}')
                final = request.POST.get(f'final_{sid}')
                
                # 如果有输入成绩
                if regular or final:
                    score, created = Score.objects.get_or_create(student=student, course=course)
                    
                    if regular:
                        # 处理可能为空的情况
                        try:
                            score.regular_score = Decimal(str(regular))
                        except:
                            pass
                    if final:
                        try:
                            score.final_score = Decimal(str(final))
                        except:
                            pass
                        
                    score.save() # 触发自动计算总分
            
            messages.success(request, '成绩已更新')
            return redirect('course_grading', course_id=course.id)
            
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    # 准备前端数据
    student_data = []
    for student in students:
        score = scores_map.get(student.student_id)
        student_data.append({
            'student': student,
            'score': score
        })
        
    return render(request, 'course_grading.html', {
        'course': course,
        'student_data': student_data
    })
