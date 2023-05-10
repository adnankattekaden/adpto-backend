import json

from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.response import CustomResponse
from utils.views import TokenGenerate
from .models import User, Questions,Answers
from .serializers import QuestionSerializer
from utils.permission import CustomizePermission

from utils.permission import JWTUtils

class QuestionsAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        intermediate_questions = Questions.objects.filter(difficulty_level='Intermediate').order_by('?')[:5]
        beginner_questions = Questions.objects.filter(difficulty_level='Beginner').order_by('?')[:5]
        advanced_questions = Questions.objects.filter(difficulty_level='Advanced').order_by('?')[:5]
        intermediate = QuestionSerializer(intermediate_questions,many=True).data
        beginner = QuestionSerializer(beginner_questions,many=True).data
        advanced = QuestionSerializer(advanced_questions,many=True).data
        response = beginner + intermediate + advanced

        return CustomResponse(response=response).get_success_response()


class SubmitAnswerAPI(APIView):
    authentication_classes = [CustomizePermission]
    def post(self, request):
        question_id = request.data.get('questionId')
        user_answer = request.data.get('userAnswer')
        time_taken = request.data.get('timeTaken')

        if None in (question_id, user_answer, time_taken):
            return CustomResponse(general_message='All fields are required').get_failure_response()
        
        question = Questions.objects.filter(id=question_id).first()
        user = User.objects.filter(id=JWTUtils.fetch_user_id(request)).first()
        Answers.objects.create(question=question,user=user,answered=user_answer,time_taken=time_taken)
        return CustomResponse(general_message='answer submitted').get_success_response()



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
