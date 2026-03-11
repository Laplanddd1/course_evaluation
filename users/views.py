from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'student':
        # 尝试获取学生对象，如果不存在可能需要处理
        try:
            student = user.student
        except:
            student = None
        return render(request, 'student_dashboard.html', {'student': student})
    elif user.user_type == 'teacher':
        try:
            teacher = user.teacher
            courses = teacher.courses.all()
        except:
            teacher = None
            courses = []
        return render(request, 'teacher_dashboard.html', {'teacher': teacher, 'courses': courses})
    else:  # admin
        return render(request, 'admin_dashboard.html', {'user': user})

@login_required
def profile_settings(request):
    """
    用户个人设置（目前主要是修改密码）
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 重要！否则修改密码后会被登出
            messages.success(request, '密码修改成功！')
            return redirect('dashboard')
        else:
            messages.error(request, '请修正下面的错误。')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profile_settings.html', {'form': form})