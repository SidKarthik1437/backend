from django.contrib import admin
from .models import *
# Register your models here.
# class ChoiceAdmin(admin.ModelAdmin):
#     readonly_fields = ('id',)

admin.site.register([User, Department, Subject, Question, Exam, QuestionAssignment, Choice, StudentAnswers,Result])