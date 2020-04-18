from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('landing/<int:player_id>', views.landing, name='landing'),
    path('session/add', views.add_session, name='add_session'),
    path('player/<int:player_id>/session/<int:session_id>', views.session, name='session'),
]