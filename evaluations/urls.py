from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('tasks/', views.student_tasks, name='student_tasks'),
    path('evaluate/<int:task_id>/', views.evaluate_task, name='evaluate_task'),
    path('course/<int:course_id>/results/', views.course_results, name='course_results'),
    path('select-courses/', views.select_courses, name='select_courses'),
    path('enroll-course/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('teacher-leaderboard/', views.teacher_leaderboard, name='teacher_leaderboard'),
    path('vote-teacher/', views.vote_teacher, name='vote_teacher'),
    path('export-teacher-votes/', views.export_teacher_votes, name='export_teacher_votes'),
    path('history/', views.historical_evaluations, name='historical_evaluations'),
    path('schedule/', views.student_schedule, name='student_schedule'),
    path('my-grades/', views.my_grades, name='my_grades'),
    path('course/<int:course_id>/grading/', views.course_grading, name='course_grading'),
]