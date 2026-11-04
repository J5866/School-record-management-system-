from django.db import models
from django.db.models.fields import Field

# Create your models here.
class student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    date_of_birth = models.CharField(max_length=50)
    class_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    address= models.CharField(max_length=50)
    email= models.CharField(max_length=50)
    image = models.ImageField(upload_to='student_images/', blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name
class classRoom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    clas_name = models.ForeignKey(
        'classRoom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
class Teacher(models.Model):
    teacher_id = models.CharField(max_length=20,unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    class_name = models.ForeignKey(
        'classRoom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    address = models.TextField(max_length=50)
    image = models.ImageField(upload_to='teacher_images/', blank=True)

            
    def __str__(self):
        return f"{self.first_name}{self.last_name}"
    
    
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'), 
        ('Absent', 'Absent'), 
        ('Late', 'Late'),           
    ]
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
    max_length=10, 
     choices=STATUS_CHOICES,
     default='Present'
     )
    remarks = models.CharField(
        max_length=100, blank=True, null=True)
    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']
        def __str__(self):
            return f"{self.student} - {self.date} - {self.status}"
        
class Examination(models.Model):
    TERM_CHOICES = [
        ('First Term', 'First Term'),
        ('Second Term', 'Second Term'),
        ('Third Term', 'Third Term'),
    ]

    student = models.ForeignKey(student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    session = models.CharField(max_length=20)
    test_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    @property
    def total_score(self):
        return self.test_score + self.exam_score
    
    @property
    def grade(self):
        total = self.total_score
        if total >= 70:
            return 'A'
        elif total >= 60:
            return 'B'
        elif total >= 50:
            return 'C'
        elif total >= 45:
            return 'D'
        else:
            return 'F'

    class Meta:
        ordering = ['student', 'subject']
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.term}"

class Feepayment(models.Model):
    student = models.ForeignKey(
        student, on_delete=models.CASCADE)
    amount_paid =  models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    payment_date =  models.DateField()
    term = models.CharField(max_length=20)
    payment_refeference = models.CharField(
        max_length=50,
        blank=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
class meta:
    ordering = [ '-payment_date']
    
    def __str__(self):
        return f"{self.student} - {self.amount_paid}"
