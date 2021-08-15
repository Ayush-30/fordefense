from django.contrib import admin
from .models import QuestionPost, AnswerPost, AnswerLike, QuestionLike, SendNotification

admin.site.register(QuestionPost)
admin.site.register(AnswerPost)
admin.site.register(SendNotification)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)
