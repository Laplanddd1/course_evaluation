from django.contrib import admin
from .models import QuestionnaireTemplate, Question, EvaluationTask, EvaluationResult, Answer

admin.site.register(QuestionnaireTemplate)
admin.site.register(Question)
admin.site.register(EvaluationTask)
admin.site.register(EvaluationResult)
admin.site.register(Answer)