import django.contrib.auth.views as dj_views
from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path(
        'logout/',
        dj_views.LogoutView.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'signup/',
        views.SingUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        dj_views.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_reset/',
        dj_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'),
        name='password_reset'),
    path(
        'password_reset/done/',
        dj_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>',
        dj_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='reset_confirm'
    ),
    path(
        'reset/done/',
        dj_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='reset_complete'
    ),
    path(
        'password_change/',
        dj_views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        dj_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
]
