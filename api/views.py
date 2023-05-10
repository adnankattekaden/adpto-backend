import json

from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.response import CustomResponse
from utils.views import TokenGenerate
from .models import User, Questions

from .serializers import QuestionSerializer

class QuestionsAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        medium_questions = Questions.objects.filter(difficulty_level='Medium').order_by('?')[:5]
        beginner_questions = Questions.objects.filter(difficulty_level='Beginner').order_by('?')[:5]
        advanced_questions = Questions.objects.filter(difficulty_level='Advanced').order_by('?')[:5]
        medium = QuestionSerializer(medium_questions,many=True).data
        beginner = QuestionSerializer(beginner_questions,many=True).data
        advanced = QuestionSerializer(advanced_questions,many=True).data
        print(medium,beginner,advanced)
        response = beginner + medium + advanced

        return CustomResponse(response=response).get_success_response()


class SubmitAnswerAPI(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        pass



class RegisterUserAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')

        if None in (name, email, phone, password):
            return CustomResponse(general_message='All fields are required').get_failure_response()

        if User.email_exists(email):
            return CustomResponse(general_message='Email already exists').get_failure_response()

        user = User(name=name, email=email, phone=phone)
        user.set_password(password)
        user.save()
        return CustomResponse(general_message='User registered successfully').get_success_response()


class LoginAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            auth = TokenGenerate().generate(user)
            return CustomResponse(response=auth).get_success_response()
        else:
            return CustomResponse(general_message="login failed").get_failure_response()
