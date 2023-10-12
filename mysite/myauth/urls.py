from django.urls import path

from .views import (
    SignIn,
    SignOut,
    SignUp,
    ProfileUser,
    AvatarUpdateView,
)

app_name = 'myauth'

urlpatterns = [
    path("sign-in/", SignIn.as_view()),
    path("sign-up/", SignUp.as_view()),
    path("sign-out/", SignOut.as_view()),
    path("profile/", ProfileUser.as_view()),
    path("profile/avatar/", AvatarUpdateView.as_view()),
    path("profile/password/", ProfileUser.as_view()),
]
