from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'
        
    base_role = Role.ADMIN
    
    # Setting the USN as the username field
    USN = models.CharField(max_length=10, unique=True)
    username = None  # Remove the default username field
    USERNAME_FIELD = 'USN'
    REQUIRED_FIELDS = ['email', 'name', 'Department']

    name = models.CharField(max_length=50)
    Department = models.ForeignKey(Department, related_name='department_users', on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField(null=True, blank=True)  # For students' password
    role = models.CharField(max_length=10, choices=Role.choices, default=base_role)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            if self.role == User.Role.STUDENT and self.date_of_birth:
                self.set_password(self.date_of_birth.strftime('%Y%m%d'))  # Setting password as DOB for students
            elif self.role in [User.Role.TEACHER, User.Role.ADMIN] and not self.password:
                raise ValueError("Teachers and Admins must have a password set")
            return super().save(*args, **kwargs)
    
class TeacherManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.TEACHER)

class Teacher(User):
    base_role = User.Role.TEACHER
    teachers = TeacherManager()
    
    class Meta:
        proxy = True
    
class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.STUDENT)

class Student(User):
    base_role = User.Role.STUDENT
    students = StudentManager()
    
    class Meta:
        proxy = True

class StudentProfile(models.Model):
    user = models.OneToOneField(Student, on_delete=models.CASCADE)
