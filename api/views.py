from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, OR, AllowAny
from .permissions import IsAdminUser, IsStudentUser
from rest_framework.decorators import action

class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        User = get_user_model()
        
        usn = request.data.get('usn')
        name = request.data.get('name')
        dob = request.data.get('dob')
        role = request.data.get('role', User.Role.STUDENT)  # Default to STUDENT if role is not provided
        
        if not usn or not name or not dob:
            return Response({'error': 'USN, Name, and DOB are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse dob string to datetime object
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid DOB format, expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if role == User.Role.STUDENT:
                user = User.objects.create_student(usn=usn, name=name, dob=dob, role=role)
            else:
                user = User.objects.create_user(usn=usn, name=name, dob=dob, role=role, password=request.data.get('password'))
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'User created successfully', 'user_id': user.id, "role":user.role, "pass":user.password, "user": user}, status=status.HTTP_201_CREATED)

class CustomLoginView(APIView):
    def post(self, request, *args, **kwargs):
        usn = request.data.get('usn')
        password = request.data.get('password')
        
        if not usn or not password:
            return Response({'error': 'USN and passwordd are required'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()

        try:
            user = User.objects.get(usn=usn)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check password
        if not user.check_password(password):
            print(password)
            return Response({'error': 'Wrong Password'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user).data
        
        res = Response({
            'token': token.key,
            'role': user.role,
            'user': user_serializer  # Include serialized user data in the response
        }, status=status.HTTP_200_OK)
        res.set_cookie('token', token.key, httponly=True)
        
        return res

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.auth.delete()  # Delete the Token
        return Response(status=status.HTTP_200_OK)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only Admin can perform CRUD
    
    def list(self, request, *args, **kwargs):
        # List all subjects
        queryset = Subject.objects.all()
        serializer = SubjectSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        # Retrieve a single subject
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Create a new subject
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        # Update a subject
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        # Delete a subject
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    authentication_classes = [TokenAuthentication]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Using | (OR) operator to allow either students or admin
            self.permission_classes = [IsAuthenticated & (IsStudentUser | IsAdminUser)]
        else:  # For 'create', 'update', 'partial_update', 'destroy'
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return [permission() for permission in self.permission_classes]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Check if the user has permission to publish the exam
        if request.data.get('is_published', False):
            if not self.can_publish_exam(request.user, instance):
                return Response({"detail": "You do not have permission to publish this exam."}, status=status.HTTP_403_FORBIDDEN)
        
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def can_publish_exam(self, user, exam):
        # Implement your permission logic here. For example:
        return user == exam.created_by or user.is_superuser
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDENT:
            # Assuming QuestionAssignment has a ForeignKey to Exam and User
            return Exam.objects.filter(questionassignment__student=user).distinct()
        elif user.role == User.Role.ADMIN:
            return Exam.objects.all()  # or any other filtering logic for admin
        else:
            return Exam.objects.none()  # or any other default behaviour


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]  
    
    def get_queryset(self):
        queryset = Question.objects.all()
        subject_id = self.request.query_params.get('subject', None)
        if subject_id is not None:
            queryset = queryset.filter(subject__id=subject_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            # Process each question in the list
            created_questions = []
            for question_data in request.data:
                question_text = question_data.get('text')
                subject_id = question_data.get('subject')
                choices = question_data.get('choices', [])
                
                # Check if a question with the same text and subject exists
                existing_question = Question.objects.filter(
                    text=question_text, subject_id=subject_id
                ).first()

                if existing_question:
                    # Check if choices also match
                    existing_choices = existing_question.choices.all()
                    if all(choice['content'] in [ec.content for ec in existing_choices] for choice in choices):
                        continue  # Skip this question as it's a duplicate

                # If not a duplicate, create new question and choices
                serializer = self.get_serializer(data=question_data)
                if serializer.is_valid():
                    serializer.save()
                    created_questions.append(serializer.data)

            return Response(created_questions, status=status.HTTP_201_CREATED)
        else:
            return super(QuestionViewSet, self).create(request, *args, **kwargs)

class QuestionAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionAssignmentSerializer
    
    def get_queryset(self):
        # Filter by the logged-in student and the provided exam id
        exam_id = self.kwargs.get('exam_id')
        return QuestionAssignment.objects.filter(student=self.request.user, exam__id=exam_id)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  