from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # تسجيل الدخول والخروج
    path('login/', views.AppLoginView.as_view(), name='login'),
    path('logout/', views.AppLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # الملف الشخصي
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/password/', views.change_password_view, name='change_password'),
]
