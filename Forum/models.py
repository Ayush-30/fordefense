from django.db import models
from django.db.models import CharField, TextField
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import Profile


class NonBlankCharField(CharField):
    empty_strings_allowed = False


class NonBlankTextField(TextField):
    empty_strings_allowed = False


class QuestionPost(models.Model):
    question_content = NonBlankCharField(max_length=90000, blank=False, default=None)
    question_title = TextField(max_length=10000, default=0)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    question_subject = NonBlankTextField(max_length=500, blank=False, default=None)
    question_author_semester = NonBlankCharField(max_length=150, blank=False, default=None)
    date_posted = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=90000)
    question_answer_count = models.IntegerField(default=0)
    question_view_count = models.IntegerField(default=0)
    question_like = models.ManyToManyField(User, default=None, blank=True, related_name='question_like')

    @property
    def question_id(self):
        return self.id

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.question_content == '':
            raise ValidationError('Empty error message')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.question_content)
        super(QuestionPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.question_content

    def get_absolute_url(self):
        return reverse('viewquestion', kwargs={'pk': self.pk, 'question_id': self.question_id, 'slug':  self.slug})

LIKE_CHOICES = {
    ('Like','Like'),
    ('Unlike', 'Unlike'),
}

class AnswerPost(models.Model):
    answer_id = models.AutoField(primary_key=True)
    question_id = models.TextField(max_length=50000)
    answer_text = models.TextField(max_length=50000)
    date_posted = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_by')
    liked = models.ManyToManyField(User, default=None, blank=True, related_name='liked')

    def get_absolute_url(self):
        return reverse('viewquestion', kwargs={'answer_id': self.answer_id})


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(QuestionPost, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

    def __str__(self):
        return str(self.post)


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(AnswerPost, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

    def __str__(self):
        return str(self.post)


class SendNotification(models.Model):
    user = models.ForeignKey(User, related_name='user',on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='from_user',on_delete=models.CASCADE)
    question_content = models.TextField(max_length=256)
    question_id = models.ForeignKey(QuestionPost, on_delete=models.CASCADE)
    message = models.CharField(max_length=2560)
    sent = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    @receiver(post_save, sender=AnswerPost)
    def create_answer_reply_message(created, sender, instance, *args, **kwargs):
        if created:
            answer = instance.answer_id
            users = AnswerPost.objects.get(answer_id=answer)
            # user = kwargs.get('instance')
            if instance.posted_by != str(users.posted_by):
                from_user = instance.posted_by
                t_id = instance.question_id
                ti = QuestionPost.objects.get(pk=t_id)
                user = ti.posted_by
                title = ti.question_content
                question_id = QuestionPost.objects.get(pk=t_id)
                if str(user) == str(from_user):
                    pass
                else:
                    SendNotification.objects.create(user=user,
                                                    from_user=from_user,
                                                    question_content=title,
                                                    question_id=question_id,
                                                    message="You have an answer to your question.")
            else:
                pass

    @receiver(post_save, sender=AnswerLike)
    def create_like_reply_message(created, sender, instance, *args, **kwargs):
        if created:
            answer = instance.post.posted_by
            user = kwargs.get('instance')
            if str(user) == str(answer.user):
                pass
            else:
                from_user = instance.user
                t_id = instance.post.question_id
                t = instance.post.answer_id
                ti = AnswerPost.objects.get(answer_id=t)
                user = ti.posted_by
                title = ti.answer_text
                question_id = QuestionPost.objects.get(pk=t_id)
                if str(user) == str(from_user):
                    pass
                else:
                    if instance.value == "Like":
                        SendNotification.objects.create(user=user,
                                                        from_user=from_user,
                                                        question_content=title,
                                                        question_id=question_id,
                                                        message="Your Answer was liked!")
                    else:
                        instance = SendNotification.objects.get(user=user,
                                                                from_user=from_user,
                                                                question_content=title,
                                                                question_id=question_id,
                                                                message="Your Answer was liked!")
                        instance.delete()
                        # SendNotification.objects.delete(user=user,
                        #                                 from_user=from_user,
                        #                                 question=title,
                        #                                 question_id=question_id,
                        #                                 message="Your Answer was liked!")

    def __unicode__(self):
        return self.question.question

    class Meta:
        ordering = ['-sent']


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = QuestionPost.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

