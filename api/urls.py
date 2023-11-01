from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'departments', DepartmentViewSet)

# router.register(r'question-assignments', QuestionAssignmentViewSet, basename='question-assignment')


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('question-assignments/<int:exam_id>/', QuestionAssignmentViewSet.as_view({'get': 'list'}), name='question-assignment'),
]

urlpatterns += router.urls