from django.urls import path

from .views import RegisterUserAPI, LoginAPI,QuestionsAPI,SubmitAnswerAPI,ResultAPI

urlpatterns = [
    path('login/', LoginAPI.as_view()),
    path('register/', RegisterUserAPI.as_view()),
    path('get-questions/',QuestionsAPI.as_view()),
    path('submit-answer/',SubmitAnswerAPI.as_view()),
    path('results/',ResultAPI.as_view())

]
