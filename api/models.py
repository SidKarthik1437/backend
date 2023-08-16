from djongo import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
import jsonfield

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
        
        if role == User.Role.STUDENT:
            # If role is STUDENT, set password as dob
            dob = extra_fields.get('dob')
            if dob:
                password = dob.strftime('%Y%m%d')  # Format dob as YYYYMMDD

        user = self.model(usn=usn, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, usn, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(usn, password, **extra_fields)
    
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STUDENT = 'STUDENT', 'Student'
        
    base_role = Role.ADMIN

    usn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, default=None)
    role = models.CharField(max_length=10, choices=Role.choices, default=base_role)
    dob = models.DateField(null=True, blank=True)
    
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
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, default=None)
    
    def __str__(self):
        return self.name
    
class Question(models.Model):

    class QuestionType(models.TextChoices):
        SINGLE ='SINGLE', 'Single'
        MULTIPLE= 'MULTIPLE', 'Multiple' 
    

    text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE
    )
    choices = jsonfield.JSONField()

    def __str__(self):
        return self.text[:50]

    
class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    semester = models.IntegerField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False)

    def __str__(self):
        return f"{self.id}_{self.subject}_{self.department}_{self.semester}"
    
class QuestionAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    assigned_questions = models.ManyToManyField(Question, related_name='question_assignments')
    
    Student = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id
    
class StudentAnswer(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    QuestionAssignment = models.ForeignKey(QuestionAssignment, on_delete=models.CASCADE)
    answers = jsonfield.JSONField(null=True, blank=True)
    # ... other fields related to student's answer

    def __str__(self):
        return f"Answer: {self.student_exam} - {self.question}"
