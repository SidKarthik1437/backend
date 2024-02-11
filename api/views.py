from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser, IsStudentUser
from rest_framework.views import APIView
from django.db.models import Subquery
class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        User = get_user_model()
        
        usn = request.data.get('usn')
        name = request.data.get('name')
        dob = request.data.get('dob')
        role = request.data.get('role')  # Default to STUDENT if role is not provided
        
        if not usn or not name or not dob:
            return Response({'error': 'USN, Name, and DOB are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse dob string to datetime object
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid DOB format, expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if role == User.Role.STUDENT:
                user = User.objects.create_user(usn=usn, name=name, dob=dob, role=role, semester=request.data.get('semester'), department=request.data.get('department'), password=request.data.get('password'))
            else:
                user = User.objects.create_user(usn=usn, name=name, dob=dob, role=role, password=request.data.get('password'))
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        user = UserSerializer(user).data
        return Response({'message': 'User created successfully', "user": user}, status=status.HTTP_201_CREATED)

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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Allow all users to list and retrieve
            permission_classes = [IsAuthenticated]
        else:  # Admin required for other actions
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  # Use filtered queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get_serializer_class(self):
        if self.request.user.is_staff:  # Assuming staff users are admins
            return AdminExamSerializer
        return StudentExamSerializer
    
    def create(self, request, *args, **kwargs):
        # Ensure that only ADMIN users can create exams
        if not request.user.role == User.Role.ADMIN:
            return Response({"detail": "Only ADMIN users can create exams."}, status=status.HTTP_403_FORBIDDEN)
        # Deserialize the request data
        # usn = request.data.get("created_by")
        # try:
        #     user = User.objects.get(usn=usn)
        #     # print(user.id)
        # except User.DoesNotExist:
        #     return Response({"detail": "User with USN {} does not exist.".format(usn)}, status=status.HTTP_404_NOT_FOUND)

        # Deserialize the request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the exam object with the provided data and the retrieved user
        exam = Exam(
            start_time=serializer.validated_data["start_time"],
            end_time=serializer.validated_data["end_time"],
            negativeMarks=serializer.validated_data["negativeMarks"],
            marksPerQuestion=serializer.validated_data["marksPerQuestion"],
            passingMarks=serializer.validated_data["passingMarks"],
            created_by=serializer.validated_data['created_by'],  # Set the created_by field to the retrieved user
            department=serializer.validated_data["department"],
            subject=serializer.validated_data["subject"],
            semester=serializer.validated_data["semester"],
            duration=serializer.validated_data["duration"],
            is_published=serializer.validated_data.get("is_published", False)
        )

        # Save the exam object
        exam.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
            # Subquery to get the exams the student has attempted
            attempted_exams = Result.objects.filter(student=user).values('exam')
            # Filter the exams queryset to exclude attempted exams
            return Exam.objects.exclude(id__in=Subquery(attempted_exams))
        elif user.role == User.Role.ADMIN:
            return Exam.objects.all()
        else:
            return Exam.objects.none()


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
                
                # Check if a question with the same text, subject, and choices exists
                existing_question = Question.objects.filter(
                    text=question_text, subject_id=subject_id
                ).first()

                if existing_question:
                    # Check if choices also match
                    existing_choices = existing_question.choices.all()
                    if all(
                        choice_data in existing_choices
                        for choice_data in choices
                    ):
                        continue  # Skip this question as it's a duplicate

                # If not a duplicate, create a new question and choices
                serializer = self.get_serializer(data=question_data)
                if serializer.is_valid():
                    serializer.save()
                    created_question = serializer.data

                    # Include Choice IDs in the response
                    question_instance = Question.objects.get(pk=created_question['id'])
                    choices = ChoiceSerializer(question_instance.choices.all(), many=True).data
                    created_question['choices'] = choices

                    created_questions.append(created_question)
                else:
                    print(serializer.errors)

            return Response(created_questions, status=status.HTTP_201_CREATED)
        else:
            return super(QuestionViewSet, self).create(request, *args, **kwargs)
    
    # @action(detail=True, methods=['patch'], parser_classes=[MultiPartParser, JSONParser])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            updated_instance = serializer.instance
            # Include Choice IDs in the response
            choices = ChoiceSerializer(updated_instance.choices.all(), many=True).data
            updated_data = serializer.data
            updated_data['choices'] = choices
            return Response(updated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
    
class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = Choice.objects.all()
        serializer = ChoiceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ChoiceSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ChoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ChoiceSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StudentAnswers(APIView):
    def post(self, request):
        data = request.data
        user_responses = data.get('answers', [])
        exam_id = data.get('exam_id', None)

        # print(user_responses)

        if not exam_id:
            return Response({'error': 'Exam ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        student = request.user  # Assuming your authentication is set up properly

        # Evaluate the user responses and calculate the score
        score = 0
        user_scored_answers = {}
        for user_response in user_responses:
            question_id = user_response.get('question_id')
            selected_choice_ids = user_response.get('selected_choices', [])

            exam = Exam.objects.get(pk=exam_id)
            

            # print(selected_choice_ids)
            try:
                question = Question.objects.get(pk=question_id)
            except Question.DoesNotExist:
                return Response({'error': f'Question with ID {question_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            choices = Choice.objects.filter(question=question_id, is_correct=True)
            correct_choices = [c.id for c in choices]
            # print(set(selected_choice_ids) == set(correct_choices))
            print((correct_choices))

            # Use the serializer to create the StudentAnswers instance
            serializer = StudentAnswersSerializer(data={
                'student': student.usn,
                'exam': exam_id,
                'question': question.id,
                'selected_choices': selected_choice_ids,
                'is_correct': set(selected_choice_ids) == set(correct_choices),
            })
            if serializer.is_valid():
                serializer.save()

            # Check if the selected choices are correct for the question
            is_correct = set(selected_choice_ids) == set(correct_choices)

            # Calculate marks for the question based on correctness
            marks_for_question = (
                exam.marksPerQuestion if is_correct else - exam.negativeMarks
            )

            score += marks_for_question
            user_scored_answers[question_id] = {
                'is_correct': is_correct,
                'marks_for_question': marks_for_question,
            }
        
        # Use the serializer to create the Result instance
        result_serializer = ResultSerializer(data={
            'student': student.usn,
            'exam': exam_id,
            'totalMarks': exam.totalMarks,
            'studentMarks': score,
        })
        if result_serializer.is_valid():
            result_serializer.save()

        # Send the evaluation results to the frontend
        response_data = {
            'score': score,
            # 'userScoredAnswers': user_scored_answers,
            'totalMarks': exam.totalQuestions * exam.marksPerQuestion,
            'passingMarks': exam.passingMarks,
        }
        return Response(response_data, status=status.HTTP_200_OK)