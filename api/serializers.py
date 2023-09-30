from rest_framework import serializers
from .models import Department, User, Subject, Question, Exam, QuestionAssignment, StudentAnswer, Choice, ExamResult

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = User
        fields = ['usn', 'name', 'department','semester']
        
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['label', 'content']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'subject', 'created_by', 'exam', 'question_type', 'choices']
        
    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question

class ExamSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()  # Nested Serializer
    department = DepartmentSerializer()  # Nested Serializer
    class Meta:
        model = Exam
        # fields = ['id', 'subject', 'department', 'start_time', 'end_time', 'semester', 'duration']
        fields = ['id', 'subject', 'start_time', 'end_time', 'department', 'semester', 'duration', 'totalQuestions', 'totalMarks', 'negativeMarks', 'passingMarks', 'created_by', 'marksPerQuestion', 'is_published', 'datetime_published']


# class QuestionAssignmentSerializer(serializers.ModelSerializer):
#     assigned_questions = serializers.PrimaryKeyRelatedField(many=True, queryset=Question.objects.all())
#     class Meta:
#         model = QuestionAssignment
#         fields = '__all__'

class QuestionAssignmentSerializer(serializers.ModelSerializer):
    assigned_questions = QuestionSerializer(many=True)

    class Meta:
        model = QuestionAssignment
        fields = ['id', 'exam', 'assigned_questions', 'student']  # Add more fields if needed
        
        
class StudentAnswerSerializer(serializers.ModelSerializer):
    selected_choices = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset=Choice.objects.all()
)
    
    class Meta:
        model = StudentAnswer
        fields = ['question', 'selected_choices']

class StudentAnswerCreateSerializer(serializers.Serializer):
    exam = serializers.IntegerField(write_only=True)
    answers = StudentAnswerSerializer(many=True)
    
    def create(self, validated_data):
        exam_id = validated_data.get('exam')
        answers_data = validated_data.get('answers')
        
        question_assignment = QuestionAssignment.objects.get(exam_id=exam_id, student=self.context['request'].user)
        
        for answer_data in answers_data:
            StudentAnswer.objects.create(
                question_assignment=question_assignment,
                **answer_data
            )
        return validated_data

class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = ['id', 'student', 'exam', 'total_score', 'total_correct_answers', 'total_attempted']