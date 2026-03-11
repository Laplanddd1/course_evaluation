from django.db import models
from users.models import Student
from courses.models import Course

class QuestionnaireTemplate(models.Model):
    """
    问卷模板
    """
    name = models.CharField(max_length=100, verbose_name='模板名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questionnaire_template'
        verbose_name = '问卷模板'
        verbose_name_plural = '问卷模板'

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    问题
    """
    QUESTION_TYPE_CHOICES = (
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('scale', '量表题'),
        ('text', '开放题'),
    )
    template = models.ForeignKey(QuestionnaireTemplate, on_delete=models.CASCADE, related_name='questions')
    content = models.TextField(verbose_name='问题内容')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, verbose_name='题型')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    options = models.JSONField(null=True, blank=True, verbose_name='选项（JSON格式）')
    dimension = models.CharField(max_length=50, blank=True, verbose_name='评价维度') # 新增维度字段

    class Meta:
        db_table = 'question'
        ordering = ['order']
        verbose_name = '问题'
        verbose_name_plural = '问题'

    def __str__(self):
        return f'{self.template.name} - 问题{self.order}'


class EvaluationTask(models.Model):
    """
    评价任务：针对某门课程的一次评价活动
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='evaluation_tasks')
    questionnaire = models.ForeignKey(QuestionnaireTemplate, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='任务名称')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def save(self, *args, **kwargs):
        # 自动关联通用模板
        if not self.questionnaire_id:
            try:
                # 注意：这里需要确保 QuestionnaireTemplate 模型已经加载
                self.questionnaire = QuestionnaireTemplate.objects.get(name='通用课程评价模板')
            except Exception: 
                # 避免在迁移或其他特殊情况下报错
                pass
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'evaluation_task'
        verbose_name = '评价任务'
        verbose_name_plural = '评价任务'

    def __str__(self):
        return f'{self.course.course_name} - {self.name}'


class EvaluationResult(models.Model):
    """
    评价结果：学生对一个评价任务的提交记录
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='evaluation_results')
    task = models.ForeignKey(EvaluationTask, on_delete=models.CASCADE, related_name='results')
    submit_time = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')

    class Meta:
        db_table = 'evaluation_result'
        unique_together = ('student', 'task')  # 同一学生同一任务只能提交一次
        verbose_name = '评价结果'
        verbose_name_plural = '评价结果'

    def __str__(self):
        return f'{self.student.name} - {self.task.name}'


class Answer(models.Model):
    """
    答案：学生对具体问题的回答
    """
    result = models.ForeignKey(EvaluationResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_content = models.JSONField(verbose_name='答案内容')  # 用 JSON 存储，适应多种题型

    class Meta:
        db_table = 'answer'
        verbose_name = '答案'
        verbose_name_plural = '答案'

    def __str__(self):
        return f'{self.result} - {self.question}'


class TeacherVote(models.Model):
    """
    教师投票：学生对最喜欢的教师进行投票
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='teacher_votes')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE, related_name='votes')
    vote_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_vote'
        unique_together = ('student',)  # 每个学生只能投一票（如果需要允许投多票，可以修改这里）
        verbose_name = '教师投票'
        verbose_name_plural = '教师投票'

    def __str__(self):
        return f'{self.student.name} 投票给 {self.teacher.name}'
