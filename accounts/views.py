from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm, ProfileEditForm, ChangePasswordForm


class AppLoginView(LoginView):
    """صفحة تسجيل الدخول"""
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        """عند نجاح تسجيل الدخول"""
        user = form.get_user()
        messages.success(self.request, f'مرحباً بك، {user.get_display_name()}! 👋')
        return super().form_valid(form)


class AppLogoutView(LogoutView):
    """تسجيل الخروج"""
    next_page = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'تم تسجيل الخروج بنجاح.')
        return super().dispatch(request, *args, **kwargs)


def register(request):
    """صفحة التسجيل"""
    if request.user.is_authenticated:
        return redirect('service:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'تم إنشاء حسابك بنجاح! 🎉 يمكنك إكمال ملفك الشخصي لاحقاً.'
            )
            return redirect('service:dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """صفحة عرض الملف الشخصي"""
    user = request.user
    context = {
        'profile_user': user,
        'completion': user.profile_completion_percentage(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """صفحة تعديل الملف الشخصي"""
    user = request.user

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث ملفك الشخصي بنجاح! ✅')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=user)

    context = {
        'form': form,
        'completion': user.profile_completion_percentage(),
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def change_password_view(request):
    """صفحة تغيير كلمة المرور"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح! ✅')
            return redirect('accounts:profile')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
