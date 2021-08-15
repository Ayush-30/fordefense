from django.urls import path

from . import views
from .views import *

# from .context_processors import notification_count


urlpatterns = [
    path('', library, name='library'),
    path('navbar/', navbar, name='navbar'),
    path('comp1/', library, name='comp1'),
    path('error/', error, name='error'),


]
