from django.core.management.base import BaseCommand
from users.models import User, Student, Teacher
from courses.models import Course, Score
from evaluations.models import QuestionnaireTemplate, Question, EvaluationTask, EvaluationResult, Answer, TeacherVote
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Starting data population...')
        
        # 1. Create Users
        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created admin user (password: admin123)')
            
        # Teachers
        teachers_data = [
            ('teacher1', 'T001', '老师一'),
            ('teacher2', 'T002', '老师二'),
            ('teacher3', 'T003', '老师三'),
            ('teacher4', 'T004', '老师四'),
            ('teacher5', 'T005', '老师五'),
        ]
        teachers = []
        for username, t_id, t_name in teachers_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='123456', user_type='teacher')
                teacher = Teacher.objects.create(user=user, teacher_id=t_id, name=t_name)
                teachers.append(teacher)
                self.stdout.write(f'Created {username} ({t_name}, password: 123456)')
            else:
                teacher = User.objects.get(username=username).teacher
                # Update name if needed
                if teacher.name != t_name:
                    teacher.name = t_name
                    teacher.save()
                teachers.append(teacher)

        # Students
        students = []
        for i in range(1, 11):
            username = f'student{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='123456', user_type='student')
                student = Student.objects.create(user=user, student_id=f'S202500{i}', name=f'学生{i}')
                students.append(student)
                self.stdout.write(f'Created {username} (password: 123456)')
            else:
                students.append(User.objects.get(username=username).student)
                
        # 2. Create Courses
        course_names = ['高等数学', '大学英语', '计算机导论', 'Python程序设计', '数据结构', '操作系统']
        locations = ['教A-101', '教A-202', '教B-303', '实C-105', '实D-206']
        courses = []
        for i, name in enumerate(course_names):
            code = f'CS{100+i}'
            course, created = Course.objects.get_or_create(
                course_code=code,
                defaults={'course_name': name, 'semester': '2025-2026-1'}
            )
            
            # Update semester if it exists but is old format
            if course.semester != '2025-2026-1':
                course.semester = '2025-2026-1'
                course.save()
            
            # Update schedule info if missing
            if not course.week_day:
                course.week_day = random.randint(1, 5)
                course.time_slot = random.randint(1, 5)
                course.location = random.choice(locations)
                course.save()
                
            # Assign random teachers
            if course.teachers.count() == 0:
                course.teachers.add(*random.sample(teachers, k=random.randint(1, 2)))
            courses.append(course)
            self.stdout.write(f'Created/Updated course {name} with schedule')

        # 3. Enroll Students
        for student in students:
            # Enroll in 3-5 random courses
            if student.courses.count() == 0:
                selected_courses = random.sample(courses, k=random.randint(3, 5))
                for c in selected_courses:
                    student.courses.add(c)
            
            # Generate scores for enrolled courses
            for course in student.courses.all():
                if not Score.objects.filter(student=student, course=course).exists():
                    Score.objects.create(
                        student=student,
                        course=course,
                        regular_score=random.randint(70, 95),
                        final_score=random.randint(60, 95)
                    )
        self.stdout.write('Enrolled students in courses and generated scores')

        # 4. Create Questionnaire
        template, _ = QuestionnaireTemplate.objects.get_or_create(
            name='通用课程评价模板',
            defaults={'description': '适用于大多数理论课程的通用评价问卷'}
        )
        
        # Clear existing questions to update structure if needed (optional, here we check count)
        if template.questions.count() < 5:
            template.questions.all().delete()
            
            # 维度1：教学态度 (20%)
            Question.objects.create(template=template, content='老师上课是否准时，备课是否充分？', question_type='scale', order=1, dimension='教学态度')
            Question.objects.create(template=template, content='老师对待学生是否耐心，能否及时解答疑问？', question_type='scale', order=2, dimension='教学态度')
            
            # 维度2：教学内容 (30%)
            Question.objects.create(template=template, content='课程内容是否充实，重点难点是否突出？', question_type='scale', order=3, dimension='教学内容')
            Question.objects.create(template=template, content='教学进度安排是否合理？', question_type='scale', order=4, dimension='教学内容')
            
            # 维度3：教学方法 (30%)
            Question.objects.create(template=template, content='老师的讲解是否生动有趣，易于理解？', question_type='scale', order=5, dimension='教学方法')
            Question.objects.create(template=template, content='是否善于运用多媒体等辅助教学手段？', question_type='scale', order=6, dimension='教学方法')
            
            # 维度4：教学效果 (20%)
            Question.objects.create(template=template, content='通过本课程的学习，你是否掌握了相关知识和技能？', question_type='scale', order=7, dimension='教学效果')
            
            # 开放题
            Question.objects.create(template=template, content='你对这门课程或老师有什么建议？', question_type='text', order=8, dimension='建议与意见')
            
        self.stdout.write('Created/Updated questionnaire template with structured questions')

        # 5. Create Evaluation Tasks
        now = timezone.now()
        for course in courses:
            EvaluationTask.objects.get_or_create(
                course=course,
                questionnaire=template,
                name=f'{course.course_name}期末评价',
                defaults={
                    'start_time': now - timedelta(days=7),
                    'end_time': now + timedelta(days=7),
                    'is_active': True
                }
            )
        self.stdout.write('Created evaluation tasks')
        
        # 6. Generate Votes
        for student in students:
            if not TeacherVote.objects.filter(student=student).exists():
                # Randomly vote for a teacher
                chosen_teacher = random.choice(teachers)
                TeacherVote.objects.create(student=student, teacher=chosen_teacher)
        self.stdout.write('Generated random teacher votes')

        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))
