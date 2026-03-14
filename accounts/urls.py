from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/',                  views.register,        name='register'),
    path('login/',                     views.login,           name='login'),
    path('me/',                        views.me,              name='me'),

    # Admin approval
    path('pending-doctors/',           views.pending_doctors, name='pending-doctors'),
    path('approve/<int:user_id>/',     views.approve_doctor,  name='approve-doctor'),
    path('reject/<int:user_id>/',      views.reject_doctor,   name='reject-doctor'),
    path('users/',                     views.all_users,       name='all-users'),
]