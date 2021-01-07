from rest_framework import serializers
from .models import Answer, Question, SimpleTest, SimpleTestResult, User


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'answer')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleTestResult
        fields = ('id', 'answered_id', 'question')

    def update(self, instance, validated_data):
        instance.answered_id = validated_data.get('answered_id', instance.answered_id)
        instance.save()
        return instance


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'answers')


class QuestionResSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'answers', 'right_answer')


class SimpleTestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    simpletestresult = ResultSerializer(source='simpletestresult_set', many=True)

    class Meta:
        model = SimpleTest
        fields = ('id', 'simple_test_date', 'status', 'questions', 'simpletestresult')
        read_only_fields = ['id', 'simple_test_date', 'status', 'questions']


class SimpleTestResSerializer(serializers.ModelSerializer):
    questions = QuestionResSerializer(many=True, read_only=True)
    simpletestresult = ResultSerializer(source='simpletestresult_set', many=True)

    class Meta:
        model = SimpleTest
        fields = ('id', 'simple_test_date', 'status', 'questions', 'simpletestresult')
        read_only_fields = ['id', 'simple_test_date', 'status', 'questions']


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
