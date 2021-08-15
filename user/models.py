from django.db import models
from PIL import Image
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(auto_now_add=False, auto_now=False, blank=False)
    user_image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    college = models.CharField(max_length=3000)
    sem_choices = (
        ("1st Semester", "1st Semester"),
        ("2nd Semester", "2nd Semester"),
        ("3rd Semester", "3rd Semester"),
        ("4th Semester", "4th Semester"),
        ("5th Semester", "5th Semester"),
        ("6th Semester", "6th Semester"),
        ("7th Semester", "7th Semester"),
        ("8th Semester", "8th Semester"),
    )
    semester = models.CharField(choices=sem_choices, max_length=300)
    contact_number = models.CharField(max_length=10)
    number_of_posts = models.IntegerField(default=0)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.user_image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.user_image.path)