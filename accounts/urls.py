from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/',                       views.register,             name='register'),
    path('login/',                          views.login,                name='login'),
    path('me/',                             views.me,                   name='me'),
    path('token/refresh/',                  TokenRefreshView.as_view(), name='token-refresh'),

    path('pending-doctors/',                views.pending_doctors,      name='pending-doctors'),
    path('approve/<int:user_id>/',          views.approve_doctor,       name='approve-doctor'),
    path('reject/<int:user_id>/',           views.reject_doctor,        name='reject-doctor'),
    path('users/',                          views.all_users,            name='all-users'),
    path('users/<int:user_id>/delete/',     views.delete_user,          name='delete-user'),
]