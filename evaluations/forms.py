from django import forms
from .models import Question

class EvaluationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # 从关键字参数中取出 questions 列表
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for q in questions:
            field_name = f'q_{q.id}'
            if q.question_type == 'scale':
                self.fields[field_name] = forms.ChoiceField(
                    label=q.content,
                    choices=[(1, '1分'), (2, '2分'), (3, '3分'), (4, '4分'), (5, '5分')],
                    widget=forms.RadioSelect,
                    required=True
                )
            elif q.question_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=q.content,
                    widget=forms.Textarea(attrs={'rows': 3}),
                    required=False  # 开放题可以不必须
                )
            elif q.question_type == 'single':
                # 单选题，选项从 q.options 中获取，假设 options 是列表 ['A','B','C']
                options = q.options if q.options else []
                choices = [(opt, opt) for opt in options]
                self.fields[field_name] = forms.ChoiceField(
                    label=q.content,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True
                )
            elif q.question_type == 'multiple':
                options = q.options if q.options else []
                choices = [(opt, opt) for opt in options]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=q.content,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple,
                    required=False
                )