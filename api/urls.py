from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'question-assignments', QuestionAssignmentViewSet, basename='question-assignment')
router.register(r'student_answers', StudentAnswerViewSet, basename='student-answer')
router.register(r'exam_results', ExamResultViewSet, basename='exam-result')

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('create_user/', CreateUserView.as_view(), name='create_user'),
]

urlpatterns += router.urls