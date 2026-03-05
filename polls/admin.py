from django.contrib import admin
from .models import Question, Choice

# Register both models
admin.site.register(Question)
admin.site.register(Choice)
