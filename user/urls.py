from django.conf.urls import url
from django.urls import path

from . import views
from .views import activate

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.loginpage, name='login'),
    path('', views.base, name='open_page'),
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.editprofile, name='editprofile'),
    # path('editprofile/profile',  views.profile, name='profile'),
    path('activate/<slug:uidb64>/<slug:token>/',
         views.activate, name='activate')
]
