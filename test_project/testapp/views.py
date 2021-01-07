from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QuestionSerializer, AnswerSerializer, ResultSerializer, SimpleTestSerializer, \
    CustomUserSerializer, SimpleTestResSerializer
from .models import Question, SimpleTest, SimpleTestResult, Answer


class ResultView(APIView):
    def get(self, request, pk):
        simpletestresult = SimpleTestResult.objects.filter(pk=pk)
        serializer = ResultSerializer(simpletestresult, many=True)
        return Response({"simpletestresult": serializer.data})


class AnswerView(APIView):
    def get(self, request, pk):
        answer = Answer.objects.filter(pk=pk)
        serializer = AnswerSerializer(answer, many=True)
        return Response({"answer": serializer.data})


class QuestionView(APIView):
    def get(self, request, pk):
        question = Question.objects.filter(pk=pk)
        serializer = QuestionSerializer(question, many=True)
        return Response({"question": serializer.data})


class QuestionAnswersView(APIView):
    def get(self, request, pk):
        question = Question.objects.get(pk=pk)
        question_answers = question.answers.all()
        serializer = AnswerSerializer(question_answers, many=True)
        return Response({"question_answers": serializer.data})


class SimpleTestView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        test = SimpleTest.objects.filter(pk=pk)
        serializer = SimpleTestSerializer(test, many=True)
        return Response({"SimpleTest": serializer.data})

    def put(self, request, pk):
        saved_test = get_object_or_404(SimpleTest.objects.all(), pk=pk)
        if not saved_test.status:
            request_test = request.data.get('SimpleTest')
            answers_list = request_test[0]['simpletestresult']
            for answers_item in answers_list:
                test_result_item = saved_test.simpletestresult_set.get(id=answers_item['id'])
                serializer = ResultSerializer(instance=test_result_item, data=answers_item, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    test_result_item.simple_test_question_answered(answer_id=answers_item['answered_id'])
            saved_test.status = True
            saved_test.save()
            test = SimpleTest.objects.get(pk=pk, status=True)
            serializer = SimpleTestResSerializer(test, many=False)
            return Response({"success": "Тест успешно сохранен", "SimpleTest": serializer.data})
        return Response({"error": "Тест был ранее сохранен"})


class SimpleTestResView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        test = SimpleTest.objects.filter(pk=pk, status=True)
        serializer = SimpleTestResSerializer(test, many=True)
        return Response({"SimpleTest": serializer.data})


class SimpleTestCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        test = SimpleTest.objects.create(simple_test_date=timezone.now(), status=False)
        serializer = SimpleTestSerializer(test, many=False)
        return Response({"SimpleTest": serializer.data})


class CustomUserCreate(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
