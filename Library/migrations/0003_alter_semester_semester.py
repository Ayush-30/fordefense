# Generated by Django 3.2.2 on 2021-08-14 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0002_alter_semester_semester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='semester',
            field=models.CharField(choices=[('Second Semester', 'Second Semester'), ('Fourth Semester', 'Fourth Semester'), ('First Semester', 'First Semester'), ('Third Semester', 'Third Semester'), ('Fifth Semester', 'Fifth Semester'), ('Eighth Semester', 'Eighth Semester'), ('Seventh Semester', 'Seventh Semester'), ('Sixth Semester', 'Sixth Semester')], default='none', max_length=16),
        ),
    ]
