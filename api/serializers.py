import json

from rest_framework import serializers

from api.generate import generate, generate_roadmap
from .models import Questions, Tests, Answers, TestTagListLink


class QuestionSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(source='tags.title')

    class Meta:
        model = Questions
        fields = ["id", "question", "a", "b", "c", "d", "correct_answer", "difficulty_level", "tags"]


class TestSerializer(serializers.ModelSerializer):
    proficiency = serializers.SerializerMethodField()
    percentage_of_completed = serializers.SerializerMethodField()

    class Meta:
        model = Tests
        fields = ('id', 'subject', 'date_time', 'proficiency', 'percentage_of_completed')

    def get_proficiency(self, obj):
        answers = Answers.objects.filter(test=obj)

        return generate(answers).get('proficiencyLevel')

    def get_percentage_of_completed(self, obj):

        answers = Answers.objects.filter(test=obj)
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
                    test_tag_link = TestTagListLink.objects.filter(test__id=obj.id, tag__title=key.get('tag')).first()
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
        tags_count = 0
        mark_as_completed_count = 0
        for i in sorted_json_data:

            if i.get('mark_as_completed') == True:
                mark_as_completed_count += 1
            tags_count += 1

        return (mark_as_completed_count / tags_count) * 100
