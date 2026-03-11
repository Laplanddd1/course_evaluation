from django.db import models
from users.models import Teacher, Student

class Course(models.Model):
    """
    课程信息
    """
    course_code = models.CharField(max_length=20, unique=True, verbose_name='课程代码')
    course_name = models.CharField(max_length=100, verbose_name='课程名称')
    credit = models.FloatField(verbose_name='学分', null=True, blank=True)
    semester = models.CharField(max_length=20, verbose_name='学期', help_text='例如：2025-2026-1')
    teachers = models.ManyToManyField(Teacher, related_name='courses', verbose_name='授课教师')
    students = models.ManyToManyField(Student, related_name='courses', verbose_name='选课学生', blank=True)
    
    WEEK_CHOICES = (
        (1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'), (5, '周五'), (6, '周六'), (7, '周日')
    )
    TIME_SLOT_CHOICES = (
        (1, '第1-2节 (08:00-09:35)'),
        (2, '第3-4节 (09:55-11:30)'),
        (3, '第5-6节 (13:30-15:05)'),
        (4, '第7-8节 (15:25-17:00)'),
        (5, '第9-10节 (18:30-20:05)'),
    )
    week_day = models.IntegerField(choices=WEEK_CHOICES, verbose_name='上课时间(周)', null=True, blank=True)
    time_slot = models.IntegerField(choices=TIME_SLOT_CHOICES, verbose_name='上课时间(节次)', null=True, blank=True)
    location = models.CharField(max_length=50, verbose_name='上课地点', null=True, blank=True)
    
    regular_weight = models.DecimalField(max_digits=3, decimal_places=2, default=0.3, verbose_name='平时分权重')
    final_weight = models.DecimalField(max_digits=3, decimal_places=2, default=0.7, verbose_name='期末分权重')

    class Meta:
        db_table = 'course'
        verbose_name = '课程'
        verbose_name_plural = '课程'

    def __str__(self):
        return f'{self.course_code} {self.course_name}'


class Score(models.Model):
    """
    学生成绩
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores', verbose_name='学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='scores', verbose_name='课程')
    regular_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='平时分')
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='期末分')
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='总评成绩')
    
    class Meta:
        db_table = 'score'
        unique_together = ('student', 'course')
        verbose_name = '成绩'
        verbose_name_plural = '成绩'
        
    def save(self, *args, **kwargs):
        # 自动计算总分
        if self.regular_score is not None and self.final_score is not None:
            # 获取课程权重
            # 注意：Decimal 和 Float 混合运算可能报错，统一转为 Decimal
            from decimal import Decimal
            r_weight = self.course.regular_weight
            f_weight = self.course.final_weight
            
            # 确保分数也是 Decimal 类型
            r_score = Decimal(str(self.regular_score))
            f_score = Decimal(str(self.final_score))
            
            # 计算加权总分
            total = (r_score * r_weight) + (f_score * f_weight)
            self.total_score = round(total, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.name} - {self.course.course_name} : {self.total_score}'