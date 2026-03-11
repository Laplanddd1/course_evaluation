from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    自定义用户模型，继承 Django 的 AbstractUser，添加用户类型字段。
    """
    USER_TYPE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name='用户类型')

    class Meta:
        db_table = 'user'  # 指定数据库表名
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'


class Student(models.Model):
    """
    学生扩展信息，与 User 一对一关联。
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True, verbose_name='学号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    # 后续添加班级、专业等字段

    class Meta:
        db_table = 'student'
        verbose_name = '学生'
        verbose_name_plural = '学生'

    def __str__(self):
        return f'{self.name} ({self.student_id})'


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    teacher_id = models.CharField(max_length=20, unique=True, verbose_name='工号')
    name = models.CharField(max_length=50, verbose_name='姓名')

    class Meta:
        db_table = 'teacher'
        verbose_name = '教师'
        verbose_name_plural = '教师'

    def __str__(self):
        return f'{self.name} ({self.teacher_id})'


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # 保留扩展性

    class Meta:
        db_table = 'admin'
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    def __str__(self):
        return f'管理员 {self.user.username}'