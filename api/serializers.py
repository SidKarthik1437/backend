from rest_framework import serializers
from .models import *

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = User
        fields = ['usn', 'name', 'department','semester','role', 'dob']
        
class SubjectSerializer(serializers.ModelSerializer):
    
    # department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    class Meta:
        model = Subject
        fields = ['id', 'name', 'semester','department' ]

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'label', 'content', 'is_correct', 'image']
        
    def create(self, validated_data):
        label = validated_data.get('label')
        if label is None:
            # Handle the case where 'label' is not provided in the data
            raise serializers.ValidationError("Label is required for a choice.")

        choices_data = validated_data.pop('choices')
        choice = Choice.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=choice, **choice_data)
        return choice
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url if instance.image else None
        representation['id'] = instance.id
        return representation

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'subject', 'created_by', 'image', 'exam', 'question_type', 'choices']
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question
    
    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', [])

        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create choices
        for choice_data in choices_data:
            label = choice_data.get('label')
            choice, created = Choice.objects.update_or_create(
                question=instance, label=label, 
                defaults=choice_data
            )

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url if instance.image else None
        # If the user is not an admin, remove the 'is_correct' attribute from each choice
        if not self.context['request'].user.is_staff:
            for choice in representation['choices']:
                choice.pop('is_correct', None)
        return representation
    


class AdminExamSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Exam
        fields = ['id', 'subject', 'start_time', 'end_time', 'department', 'semester', 'duration', 'totalQuestions', 'totalMarks', 'negativeMarks', 'passingMarks', 'created_by', 'marksPerQuestion', 'is_published', 'datetime_published', 'status']

class StudentExamSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = Exam
        fields = ['id', 'subject', 'start_time', 'end_time', 'department', 'semester', 'duration', 'is_published', 'datetime_published']

class ExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSession
        fields = '__all__'


class QuestionAssignmentSerializer(serializers.ModelSerializer):
    assigned_questions = QuestionSerializer(many=True)

    class Meta:
        model = QuestionAssignment
        fields = ['id', 'exam', 'assigned_questions', 'student']  # Add more fields if needed
        
        
class StudentAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswers
        fields = ['id', 'exam', 'student', 'question', 'selected_choices', 'is_correct']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'exam', 'student', 'studentMarks', 'totalMarks']