from rest_framework import serializers

from api.generate import generate
from .models import Questions, Tests, Answers


class QuestionSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(source='tags.title')

    class Meta:
        model = Questions
        fields = ["id", "question", "a", "b", "c", "d", "correct_answer", "difficulty_level", "tags"]


class TestSerializer(serializers.ModelSerializer):
    proficiency = serializers.SerializerMethodField()

    class Meta:
        model = Tests
        fields = ('id', 'subject', 'date_time', 'proficiency')

    def get_proficiency(self, obj):
        answers = Answers.objects.filter(test=obj)

        return generate(answers).get('proficiencyLevel')
