from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher, Admin

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
    list_display = UserAdmin.list_display + ('user_type',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Admin)