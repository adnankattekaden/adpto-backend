import json

from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api.generate import generate, generate_roadmap
from utils.permission import CustomizePermission
from utils.permission import JWTUtils
from utils.response import CustomResponse
from utils.views import TokenGenerate
from .models import User, Questions, Answers, Tests
from .serializers import QuestionSerializer


# f = open('./data/questions.json')
# data = json.load(f)
# for key in data:
#     question_id = key.get('Question ID')
#     question = key.get('Question')
#     a = key.get('A')
#     b = key.get('B')
#     c = key.get('C')
#     d = key.get('D')
#     correct_answer = key.get('Correct Answer')
#     level = key.get('Difficulty Level')
#     tags = key.get('tag')
#
#     Questions.objects.create(question=question, a=a, b=b, c=c, d=d, correct_answer=correct_answer,
#                              difficulty_level=level, tags=tags)


class QuestionsAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        intermediate_questions = Questions.objects.filter(difficulty_level='Intermediate').order_by('?')[:5]
        beginner_questions = Questions.objects.filter(difficulty_level='Beginner').order_by('?')[:5]
        advanced_questions = Questions.objects.filter(difficulty_level='Advanced').order_by('?')[:5]
        intermediate = QuestionSerializer(intermediate_questions, many=True).data
        beginner = QuestionSerializer(beginner_questions, many=True).data
        advanced = QuestionSerializer(advanced_questions, many=True).data
        response = beginner + intermediate + advanced

        return CustomResponse(response=response).get_success_response()


class ResultAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request, test_id):
        test = Tests.objects.filter(id=test_id).first()
        answers = Answers.objects.filter(test=test)
        return CustomResponse(response=generate(answers)).get_success_response()


class SubmitAnswerAPI(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        question_id = request.data.get('questionId')
        user_answer = request.data.get('userAnswer')
        time_taken = request.data.get('timeTaken')
        test_id = request.data.get('testId')

        if None in (question_id, user_answer, time_taken, test_id):
            return CustomResponse(general_message='All fields are required').get_failure_response()

        question = Questions.objects.filter(id=question_id).first()
        test = Tests.objects.filter(id=test_id).first()
        Answers.objects.create(question=question, test=test, answered=user_answer, time_taken=time_taken)
        return CustomResponse(general_message='answer submitted').get_success_response()


class MarkAsChecked(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        answerId = request.data.get('answerId')
        answer = Answers.objects.filter(id=answerId).first()
        answer.status = True
        answer.save()
        return CustomResponse(general_message='Mark as completed').get_success_response()


class CreateTestAPI(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        user = User.objects.filter(id=JWTUtils.fetch_user_id(request)).first()
        subject_name = request.data.get('subjectName')
        test_id = Tests.objects.create(user=user, subject=subject_name)
        return CustomResponse(general_message='Test Created', response={'testId': test_id.id}).get_success_response()


class UserInfo(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        user = User.objects.filter(id=JWTUtils.fetch_user_id(request)).first()

        isTestAttended = True if Tests.objects.filter(user=user).first() else False
        data = {'name': user.name, 'email': user.email, 'isTestAttended': isTestAttended}
        return CustomResponse(response=data).get_success_response()


class RegisterUserAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        education = request.data.get('education')
        gender = request.data.get('gender')

        if None in (name, email, phone, password, education):
            return CustomResponse(general_message='All fields are required').get_failure_response()

        if User.email_exists(email):
            return CustomResponse(general_message='Email already exists').get_failure_response()

        user = User(name=name, email=email, phone=phone, education=education, gender=gender)
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


# class GenerateRoadmapAPI(APIView):
#     authentication_classes = [CustomizePermission]
#
#     def get(self, request, test_id):
#         test = Tests.objects.filter(id=test_id).first()
#         answers = Answers.objects.filter(test=test)
#         result = generate_roadmap(answers)
#         current_level = result.get('proficiencyLevel')
#         correct_answers = result.get('correct_answer')
#
#         new_tags = set()
#         removal_tags = set()
#         if current_level == "Advanced":
#             for answer in correct_answers:
#                 if current_level == answer.get('level'):
#                     removal_tags.add(answer.get('tag'))
#
#         f = open('./data/Roadmaps/Python.json')
#         roadmap = json.load(f)
#         for key in roadmap:
#             level = key.get('level')
#             tag = key.get('tag')
#             if current_level == level:
#                 new_tags.add(tag)
#
#         for tag in removal_tags:
#             new_tags.discard(tag)
#
#         new_data = []
#         for key in roadmap:
#             for tags in new_tags:
#                 if tags == key.get('tag'):
#                     reference_link = key.get('reference_link')
#                     description = key.get('description')
#                     topic = key.get('Topic')
#                     mark_as_completed = False
#                     already_know = False
#                     new_data.append(
#                         {'tag': tags, 'reference_link': reference_link, 'description': description, 'topic': topic,
#                          'mark_as_completed': mark_as_completed, 'alreadyKnow': already_know})
#
#         return CustomResponse(response=new_data).get_success_response()

class GenerateRoadmapAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request, test_id):
        test = Tests.objects.filter(id=test_id).first()
        answers = Answers.objects.filter(test=test)
        result = generate_roadmap(answers)
        current_level = result.get('proficiencyLevel')
        correct_answers = result.get('correct_answer')

        new_tags = set()
        removal_tags = {}
        if current_level == "Advanced":
            for answer in correct_answers:
                if current_level == answer.get('level'):
                    removal_tags[answer.get('tag')] = True

        with open('./data/Roadmaps/Python.json') as f:
            roadmap = json.load(f)

        for key in roadmap:
            level = key.get('level')
            tag = key.get('tag')
            if current_level == level:
                new_tags.add(tag)

        for tag in removal_tags.keys():
            new_tags.discard(tag)

        new_data = []
        for key in roadmap:
            tag = key.get('tag')
            if tag in new_tags:
                reference_link = key.get('reference_link')
                description = key.get('description')
                topic = key.get('Topic')
                mark_as_completed = False
                already_know = False
                new_data.append({
                    'tag': tag,
                    'reference_link': reference_link,
                    'description': description,
                    'topic': topic,
                    'mark_as_completed': mark_as_completed,
                    'alreadyKnow': already_know
                })

        return CustomResponse(response=new_data).get_success_response()
