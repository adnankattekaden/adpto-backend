from rest_framework import serializers

from .models import Questions


class QuestionSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(source='tags.title')

    class Meta:
        model = Questions
        fields = ["id", "question", "a", "b", "c", "d", "correct_answer", "difficulty_level", "tags"]
