from django.db import models
from django.db.models import CharField, TextField
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from Forum.models import NonBlankCharField


SEMESTER_CHOICES = {
    ('First Semester', 'First Semester'),
    ('Second Semester', 'Second Semester'),
    ('Third Semester', 'Third Semester'),
    ('Fourth Semester', 'Fourth Semester'),
    ('Fifth Semester', 'Fifth Semester'),
    ('Sixth Semester', 'Sixth Semester'),
    ('Seventh Semester', 'Seventh Semester'),
    ('Eighth Semester', 'Eighth Semester'),
}


class Semester(models.Model):
    semester = models.CharField(choices=SEMESTER_CHOICES, default='none', max_length=16)

    def __str__(self):
        return str(self.post)


class Syllabus(models.Model):
    course_code = models.CharField(max_length=7)
    course_name = NonBlankCharField(max_length=50, blank=False, default=None)
    credit_hours = models.CharField(max_length=2)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.post)


class Subject(models.Model):
    subject_name = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    subject_details = models.FileField(upload_to='documents/subject')


class Questions(models.Model):
    semester = models.ForeignKey(Semester, blank=False, on_delete=models.CASCADE)
    subject = models.ForeignKey(Syllabus, blank=False, on_delete=models.CASCADE)
    question = models.FileField(upload_to='documents/questions')



