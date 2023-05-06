from django.urls import path

from .views import Test, RegisterUserAPI, LoginAPI

urlpatterns = [
    path('', Test.as_view()),
    path('login/', LoginAPI.as_view()),
    path('register/', RegisterUserAPI.as_view()),

]
