from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('subjects/', views.subjects, name='subjects'),
    path('subjects/new/', views.subjects_new, name='subjects_new'),
    path('subjects/edit/<int:id>/', views.subjects_edit, name='subjects_edit'),
    path('subjects/delete/<int:id>/', views.subjects_delete, name='subjects_delete'),

    path('sessions/', views.sessions, name='sessions'),
    path('sessions/new/', views.sessions_new, name='sessions_new'),
    path('sessions/edit/<int:id>/', views.sessions_edit, name='sessions_edit'),
    path('sessions/delete/<int:id>/', views.sessions_delete, name='sessions_delete'),
]

