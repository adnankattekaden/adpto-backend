import json

from django.contrib.auth import authenticate
from django.db.models import Subquery, OuterRef
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api.generate import generate, generate_roadmap
from utils.permission import CustomizePermission
from utils.permission import JWTUtils
from utils.response import CustomResponse
from utils.views import TokenGenerate
from .models import User, Questions, Answers, Tests, TestTagListLink, TagsList
from .serializers import QuestionSerializer, TestSerializer


#
# f = open('./data/questions.json', encoding="utf8")
# data = json.load(f)
# for key in data:
#     question = key.get('Question')
#     a = key.get('A')
#     b = key.get('B')
#     c = key.get('C')
#     d = key.get('D')
#     correct_answer = key.get('Correct Answer')
#     level = key.get('Difficulty Level')
#     tags = key.get('tag')
#
#     tag = TagsList.objects.filter(title=tags).first()
#     if tag:
#         q = Questions.objects.create(question=question, a=a, b=b, c=c, d=d, correct_answer=correct_answer,
#                                      difficulty_level=level, tags=tag)
#         print(q)
# else:
#     print(tags, level)
#     TagsList.objects.create(title=tags, level=level)


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
        test_id = request.data.get('testId')
        tag_name = request.data.get('tagName')
        is_marked_as_checked = request.data.get('isMarkedAsChecked', False)
        is_already_know = request.data.get('isAlreadyKnow', False)
        if None in (test_id, tag_name):
            return CustomResponse(general_message='All fields are required').get_failure_response()

        tag = TagsList.objects.filter(title=tag_name).first()
        if not tag:
            return CustomResponse(general_message='Invalid Tag').get_failure_response()
        test = Tests.objects.filter(id=test_id).first()
        test_tag_link = TestTagListLink.objects.filter(test=test, tag=tag).first()
        if test_tag_link:
            if is_already_know == "True":
                test_tag_link.is_already_know = True
                test_tag_link.is_marked_as_checked = True
                test_tag_link.save()
                return CustomResponse(general_message='Mark as completed').get_success_response()
            else:
                test_tag_link.is_already_know = is_already_know
                test_tag_link.is_marked_as_checked = is_marked_as_checked
            test_tag_link.save()
        else:
            TestTagListLink.objects.create(test=test, tag=tag, is_already_know=is_already_know,
                                           is_marked_as_checked=is_marked_as_checked)

        return CustomResponse(general_message='Mark as completed').get_success_response()


class CreateTestAPI(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        user = User.objects.filter(id=JWTUtils.fetch_user_id(request)).first()
        subject_name = request.data.get('subjectName')
        test_id = Tests.objects.create(user=user, subject=subject_name)
        return CustomResponse(general_message='Test Created', response={'testId': test_id.id}).get_success_response()

    def delete(self, request, test_id):
        test = Tests.objects.filter(id=test_id).first()
        if test is None:
            return CustomResponse(general_message='Test Doesnot Exist').get_failure_response()

        subject = test.subject
        tests = Tests.objects.filter(subject=subject)
        for test_ in tests:
            test_.delete()
        return CustomResponse(general_message='test deleted').get_success_response()


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
        age_range = request.data.get('ageRange')

        if None in (name, email, phone, password, education, gender, age_range):
            return CustomResponse(general_message='All fields are required').get_failure_response()

        if User.email_exists(email):
            return CustomResponse(general_message='Email already exists').get_failure_response()

        user = User(name=name, email=email, phone=phone, education=education, gender=gender, age_range=age_range)
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


class GenerateRoadmapAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request, test_id):
        test = Tests.objects.filter(id=test_id).first()

        if test is None:
            return CustomResponse(general_message='No Test Exists').get_failure_response()
        answers = Answers.objects.filter(test=test)
        result = generate_roadmap(answers)
        current_level = result.get('proficiencyLevel')
        correct_answers = result.get('correct_answer')
        wrong_answers = result.get('wrong')

        new_tags = set()
        removal_tags = set()
        additions_tags = set()

        if current_level == "Advanced":
            for answer in correct_answers:
                if current_level == answer.get('level'):
                    removal_tags.add(answer.get('tag'))
            for wrong in wrong_answers:
                if wrong.get('level') == "Beginner" or wrong.get('level') == "Intermediate":
                    additions_tags.add(wrong.get('tag'))
        elif current_level == "Intermediate":
            for answer in correct_answers:
                if current_level == answer.get('level'):
                    for answer in correct_answers:
                        if answer.get('level') == "Advanced" or answer.get('level') == "Intermediate":
                            removal_tags.add(answer.get('tag'))
                    for wrong in wrong_answers:
                        if wrong.get('level') == "Beginner":
                            additions_tags.add(wrong.get('tag'))

        elif current_level == "Beginner":
            for answer in correct_answers:
                if current_level == answer.get('level'):
                    removal_tags.add(answer.get('tag'))

        f = open('./data/Roadmaps/Python.json', encoding="utf8")
        roadmap = json.load(f)
        sort_list = []
        for key in roadmap:
            level = key.get('level')
            tag = key.get('tag')
            sort_list.append(tag)
            if current_level == "Advanced":
                if level == "Advanced":
                    new_tags.add(tag)
            elif current_level == "Intermediate":
                if level == "Intermediate" or level == "Advanced":
                    new_tags.add(tag)
            elif current_level == "Beginner":
                new_tags.add(tag)

        for tag in removal_tags:
            new_tags.discard(tag)

        new_tags.update(additions_tags)

        new_data = []
        for key in roadmap:
            for tags in new_tags:
                if tags == key.get('tag'):
                    reference_link = key.get('reference link')
                    description = key.get('description')
                    topic = key.get('Topic')
                    test_tag_link = TestTagListLink.objects.filter(test__id=test_id, tag__title=key.get('tag')).first()
                    if test_tag_link:
                        mark_as_completed = test_tag_link.is_marked_as_checked
                        already_know = test_tag_link.is_already_know
                    else:
                        mark_as_completed = False
                        already_know = False
                    new_data.append(
                        {'tag': tags, 'reference_link': reference_link, 'description': description, 'topic': topic,
                         'mark_as_completed': mark_as_completed, 'alreadyKnow': already_know})

        sorted_json_data = sorted(new_data, key=lambda x: sort_list.index(x["tag"]))
        return CustomResponse(response=sorted_json_data).get_success_response()


class ListAllSubjects(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        user = User.objects.filter(id=JWTUtils.fetch_user_id(request)).first()

        print(user)

        tests = Tests.objects.filter(user=user,
                                     date_time=Subquery(
                                         Tests.objects.filter(user=user, subject=OuterRef('subject'))
                                         .order_by('-date_time')
                                         .values('date_time')[:1]
                                     )
                                     )

        serializer = TestSerializer(tests, many=True)

        print(serializer.data)

        return CustomResponse(response=serializer.data).get_success_response()
