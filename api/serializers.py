from rest_framework import serializers
from .models import Department, User, Subject, Question, Exam, QuestionAssignment, Choice

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = User
        fields = ['usn', 'name', 'department','semester','role']
        
class SubjectSerializer(serializers.ModelSerializer):
    
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    class Meta:
        model = Subject
        fields = ['id', 'name', 'semester','department' ]

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['label', 'content', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'subject', 'created_by', 'exam', 'question_type', 'choices']
        
    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question
    
    def to_representation(self, instance):
        # Use the original representation
        rep = super().to_representation(instance)
        
        # If the user is not an admin, remove the 'is_correct' attribute from each choice
        if not self.context['request'].user.is_staff:
            for choice in rep['choices']:
                choice.pop('is_correct', None)
        
        return rep


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
        
        
