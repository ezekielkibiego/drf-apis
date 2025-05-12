from django.db import models

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),  
    )
    
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    location = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
class Course (models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_weeks = models.IntegerField()
    
    def __str__(self):
        return self.name
    
class Enrollment(models.Model): 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
    
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)
    date_assigned = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.course}: {self.grade}"
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    
    def __str__(self):
        return f"{self.student} - {self.course}: {self.status}"

class Feedback(models.Model):   
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.student} for {self.course}"
class Instructor(models.Model):     
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
class CourseInstructor(models.Model):       
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.instructor} teaches {self.course}"

class Assignment(models.Model): 
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    
    def __str__(self):
        return self.title
    
class Submission(models.Model): 
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/')
    
    def __str__(self):
        return f"{self.student} submitted {self.assignment}"
