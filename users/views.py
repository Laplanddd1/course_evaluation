from django import forms
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import SiteSetting, User, Student


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=150)
    student_id = forms.CharField(label='学号', max_length=20)
    name = forms.CharField(label='姓名', max_length=50)
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id'].strip()
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('学号已存在')
        return student_id

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', '两次输入的密码不一致')
        return cleaned_data

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


def register(request):
    if not SiteSetting.get_solo().registration_enabled:
        messages.error(request, '管理员已关闭注册')
        return redirect('login')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                user_type='student',
            )
            Student.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                name=form.cleaned_data['name'],
            )
            login(request, user)
            messages.success(request, '注册成功，已自动登录')
            return redirect('dashboard')
        messages.error(request, '请修正下面的错误')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
