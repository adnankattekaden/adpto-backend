from django.urls import path

from .views import RegisterUserAPI, LoginAPI, QuestionsAPI, SubmitAnswerAPI, ResultAPI, MarkAsChecked, CreateTestAPI, \
    UserInfo, GenerateRoadmapAPI

urlpatterns = [
    path('login/', LoginAPI.as_view()),
    path('register/', RegisterUserAPI.as_view()),
    path('get-questions/', QuestionsAPI.as_view()),
    path('create-test/', CreateTestAPI.as_view()),
    path('submit-answer/', SubmitAnswerAPI.as_view()),
    path('results/<str:test_id>/', ResultAPI.as_view()),
    path('mark-as-checked/', MarkAsChecked.as_view()),
    path('delete-test/<str:test_id>/', CreateTestAPI.as_view()),

    path('info/', UserInfo.as_view()),
    path('generate-roadmap/<str:test_id>/', GenerateRoadmapAPI.as_view()),

]
