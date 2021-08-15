from django.urls import path

from . import views
from .views import *

# from .context_processors import notification_count


urlpatterns = [
    path('', views.forum, name='forum'),
    path('viewquestion/<int:question_id>/', viewquestion, name='viewquestion'),
    path('newquestion/', views.newquestion, name='newquestion'),
    path('newquestion/viewquestion/<int:question_id>/', views.newquestion, name='newquestion'),
    path('search/viewquestion/<int:question_id>/', views.viewquestion, name='viewquestion'),
    # path('like/', views.like_post, name='like_post'),
    path('like/<int:answer_id>', views.like_post, name='like_post'),
    path('likeqns/<int:question_id>', views.like_question, name='like_question'),
    path('notification/', views.notification, name='notification'),
    path('notification/viewquestion/<int:question_id>/', views.viewquestion, name='viewquestion'),
    # path('notification_count/', notification_count, name='notification_count'),
    path('update/viewquestion/<int:question_id>/', views.questionupdate, name='questionupdate'),
    path('myposts/viewquestion/<int:answer_id>/', views.answerdelete, name='answerdelete'),
    path('profile/<int:question_id>/', views.user_profile_display, name='user_profile_display'),
    # path('test/<int:question_id>/', views.test, name='test'),
    # path('test2/', views.monkey, name='test2'),
    # path('displayquestion/<int:question_id>/', displayquestion, name='displayquestion'),
    # path('form/', views.test_form, name="form"),

]
