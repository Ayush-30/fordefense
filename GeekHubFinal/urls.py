
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
# Functions Import
from user import views as v
from Forum import views as f
from user.form import EmailValidationOnForgotPassword
from Library import views as l
# from library import views as l

from user.views import activate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', v.logout, name='logout'),
    path('', include('user.urls')),
    path('user/<str:username>/', f.UserPostListView, name='user-posts'),
    path('myposts/', f.myposts, name='myposts'),
    # path('library/', l.library, name='library'),
    path('recentsort/', f.rsort, name='rsort'),
    path('recentsort/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    path('changepassword/', v.change_password, name='change_password'),
    path('mostviewedsort/', f.msort, name='msort'),
    path('mostviewedsort/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    path('trendingsort/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    path('trendingsort/', f.tsort, name='tsort'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html', form_class=EmailValidationOnForgotPassword), name='password_reset'),
    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
         name='password_reset_complete'),
    path('forum/', include('Forum.urls')),
    path('newquestion/', f.newquestion, name='newquestion'),
    path('viewquestion/<int:question_id>', f.viewquestion, name='viewquestion'),
    path('forum/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    path('search/', f.search1, name="search"),
    path('search/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    path('like/', f.like_post, name='like_post'),
    path('myposts/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    path('yourpost/search/', f.search1, name="search2"),
    path('notification/', f.notification, name='notification'),
    path('notification/viewquestion/<int:question_id>/', f.viewquestion, name='viewquestion'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),

    path('library/', include('Library.urls')),
    # path('navbar/', l.navbar, name='navbar'),
    # path('comp1/', l.comp1, name='comp1'),
    # path('error/', l.error, name='error'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)