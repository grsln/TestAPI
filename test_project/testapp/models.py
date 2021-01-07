import math
from random import randint, random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Max
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return "{}".format(self.email)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='uploads', blank=True)


QUESTION_PER_TEST = 3


class Question(models.Model):
    question = models.CharField('Вопрос', max_length=200)
    image = models.ImageField('Изображение', upload_to='question/', blank=True)
    right_answer = models.IntegerField("ID правильного ответа", default=0)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.question


def random_object():
    count = Question.objects.aggregate(count=Count('id'))['count']
    random_index = randint(0, count - 1)
    return Question.objects.all()[random_index]


def get_random_item(model, max_id=None):
    if max_id is None:
        max_id = model.objects.aggregate(max_id=Max('id'))['max_id']
    min_id = math.ceil(max_id * random())
    return model.objects.filter(id__gte=min_id)[0]


# def random_list():
#     randomlist = []
#     for i in range(3):
#         rnd_object = get_random_item(Question)
#         # rnd_object = random_object()
#         if rnd_object:
#             randomlist.append(rnd_object)
#     return randomlist

def random_list(model, count):
    count_objects = model.objects.aggregate(count=Count('id'))['count']
    object_list = []
    if count >= count_objects:
        object_list = list(model.objects.all())
        random.shuffle(object_list)
    else:
        while len(object_list) < count:
            random_index = randint(0, count_objects - 1)
            random_item = model.objects.all()[random_index]
            if random_item in object_list:
                continue
            else:
                object_list.append(random_item)
    return object_list


class Answer(models.Model):
    answer = models.CharField('Ответ', max_length=200)
    image = models.ImageField('Изображение', upload_to='answer/', blank=True)
    question = models.ForeignKey(
        Question, verbose_name="Вопрос", on_delete=models.CASCADE,
        related_name='answers'
    )

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return '#id {}'.format(self.id)


class SimpleTest(models.Model):
    simple_test_date = models.DateTimeField('Время', auto_now_add=True)
    status = models.BooleanField('Статус', default=False)
    questions = models.ManyToManyField(Question, through='SimpleTestResult')

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def save(self, *args, **kwargs):
        new_test = False
        if not self.pk:
            new_test = True
        super().save(*args, **kwargs)
        if new_test:
            question_list = random_list(Question, QUESTION_PER_TEST)
            for item in question_list:
                if item.answers.all().count() > 0:
                    self.questions.add(item, through_defaults={'answered': False, 'right_answered': False,
                                                               'answered_id': 0})

    def simple_test_close(self):
        self.status = True
        self.save()
        return self

    def __str__(self):
        return '#id {}'.format(self.id)


class SimpleTestResult(models.Model):
    simple_test = models.ForeignKey(SimpleTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    right_answered = models.BooleanField(default=False)
    answered_id = models.IntegerField(default=0)
    answered = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Статус ответа"
        verbose_name_plural = "Статусы ответов "

    def __str__(self):
        return '#id {}'.format(self.id)

    def simple_test_question_answered(self, answer_id):
        self.right_answered = answer_id == self.question.right_answer
        self.answered = True
        self.answered_id = answer_id
        self.save()
        return self
