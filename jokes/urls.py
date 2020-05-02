from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('player/<int:player_id>', views.player, name='landing'),
    path('session/add', views.add_session, name='add_session'),
    path('player/<int:player_id>/session/<int:session_id>', views.session, name='session'),
    path('player/<int:player_id>/session/<int:session_id>/get_question', views.get_question, name='question'),
    path('player/<int:player_id>/session/<int:session_id>/get_voting', views.get_voting, name='voting'),
]