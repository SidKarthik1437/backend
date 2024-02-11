from djongo import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
import jsonfield
from django.contrib.auth.models import Group
import random
from django.db import models, transaction
from django.utils import timezone

class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class CustomUserManager(BaseUserManager):
    def create_user(self, usn, password=None, role=None, **extra_fields):
        if not usn:
            raise ValueError("The USN must be set")
        # if not extra_fields.get('department'):
        #     raise ValueError("The Department must be set")
        
        if not role:
            role = User.Role.STUDENT
        
        if role == User.Role.STUDENT:
            # If role is STUDENT, set password as dob
            dob = extra_fields.get('dob')
            if not dob:
                raise ValueError("DOB must be set for students")
            password = dob.strftime('%Y%m%d')

        user = self.model(usn=usn, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        try:
            if role == User.Role.ADMIN:
                group = Group.objects.get(name='Admin')
            elif role == User.Role.STUDENT:
                group = Group.objects.get(name='Student')
            else:
                raise ValueError("Invalid role")
        except Group.DoesNotExist:
            # Handle the case where the group does not exist
            raise ValueError(f"{role} group does not exist. Please create it in the admin panel.")
            
        user.groups.add(group)
        
        return user

    def create_superuser(self, usn, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(usn, password, role=User.Role.ADMIN, **extra_fields)
    
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STUDENT = 'STUDENT', 'Student'
        
    base_role = Role.ADMIN

    usn = models.CharField(max_length=10, unique=True, primary_key=True )
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, default=None)
    role = models.CharField(max_length=10, choices=Role.choices, default=base_role)
    dob = models.DateField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    
    username = None
    first_name = None   
    last_name = None
    email = None
    
    USERNAME_FIELD = 'usn'
    REQUIRED_FIELDS = ['name', 'dob']
    objects = CustomUserManager()

    
    def __str__(self):
        return self.usn
    
    def save(self, *args, **kwargs):
            if self.role == User.Role.STUDENT and not self.dob:
                raise ValidationError("DOB is required for students.")
            if not self.usn:
                raise ValidationError("The USN must be set")
            if not self.name:
                raise ValidationError("The name must be set")
            # if not self.department:
            #     raise ValidationError("The department must be set")

            super().save(*args, **kwargs)


class Subject(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    semester = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, default=None)
    
    def __str__(self):
        return self.id
    
    
class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE = 'SINGLE', 'Single'
        MULTIPLE = 'MULTIPLE', 'Multiple'
    
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, null=True, blank=True)
    question_type = models.CharField(max_length=10, choices=QuestionType.choices, default=QuestionType.SINGLE)

    def __str__(self):
        return self.text


from django.db import models

class Choice(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    label = models.CharField(max_length=1)  # A, B, C, D
    content = models.TextField()
    image = models.ImageField(upload_to='choices/', null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('question', 'label')
    
    def __str__(self):
        return f"{self.id} - {self.question.text} - {self.label}"

    
class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    semester = models.IntegerField(null=True)
    duration = models.DurationField(null=True)
    totalQuestions = models.IntegerField(null=True, blank=True)
    totalMarks = models.IntegerField(null=True, blank=False)
    negativeMarks = models.IntegerField(null=True, blank=True)
    passingMarks = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    marksPerQuestion = models.IntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    datetime_published = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Check if is_published is set to True and if this is the first time publishing
        if self.is_published == True :
            print("assigning questions!")
            with transaction.atomic():  # Ensure atomicity for the whole operation
                self.datetime_published = timezone.now()  # Set the time when the exam is published
                super().save(*args, **kwargs)  # Save the Exam object before creating assignments
                
                # Find the students who are eligible for this exam
                students = User.objects.filter(department=self.department, role=User.Role.STUDENT, semester=self.semester)
                print(students)
                # Get the questions associated with this exam
                questions = self.question_set.all()
                print(questions)
                if questions.count() == 0:
                    return
                # Determine the number of questions to assign to each student
                num_questions_per_student = self.totalQuestions  # Adjust as necessary
                
                for student in students:
                    # Randomly select a subset of questions for this student
                    selected_questions = random.sample(list(questions), min(num_questions_per_student, len(questions)))
                    
                   # Check if a QuestionAssignment already exists for this student and exam
                    assignment, created = QuestionAssignment.objects.get_or_create(exam=self, student=student)

                    # If it exists, clear the existing assigned_questions and set the new ones
                    if not created:
                        assignment.assigned_questions.clear()

                    # Set the new assigned_questions
                    assignment.assigned_questions.set(selected_questions)
                    
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}_{self.subject}_{self.department}_{self.semester}"

    
    
class QuestionAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    assigned_questions = models.ManyToManyField(Question, related_name='question_assignments')
    
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.exam) +" || "+ (self.student.usn)
    
class StudentResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, related_name='selected_choices', blank=True)  # For multiple choice questions
    is_correct = models.BooleanField(default=False)

    # marksPerQuestion = models.IntegerField(null=True, blank=True)
    # negativeMarks = models.IntegerField(null=True, blank=True)


    def __str__(self):
        return f"{self.student.usn} - {self.question_assignment} - {self.question}"

    def save(self, *args, **kwargs):
        # Ensure that either selected_choice or selected_choices is set, but not both.
        super().save(*args, **kwargs)
    
class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    totalMarks = models.IntegerField(null=True, blank=False)
    studentMarks = models.IntegerField(null=True, blank=False)

    def __str__(self) -> str:
        return f"Result of {self.student.usn} for Exam {self.exam}"