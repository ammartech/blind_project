from django.urls import path

from . import views

app_name = 'glossary'

urlpatterns = [
    path('', views.term_list, name='list'),
    path('<int:pk>/', views.term_detail, name='detail'),
    path('new/', views.term_new, name='new'),
]
