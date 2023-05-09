from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.response import CustomResponse
from utils.views import TokenGenerate
from .models import User
import json

def get_questions() -> dict:
    questions_file_path = "./data/questions.json"
    with open(questions_file_path, 'r') as f:
        questions_json = json.load(f)
        return questions_json
    

class QuestionsAPI(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        return CustomResponse(response=get_questions()).get_success_response()

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
