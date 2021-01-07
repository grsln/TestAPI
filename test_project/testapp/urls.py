from django.urls import path
from . import views

app_name = 'test'

urlpatterns = [
    path("test/<int:pk>/", views.SimpleTestView.as_view(), name="edit_test"),
    path("result/<int:pk>/", views.SimpleTestResView.as_view(), name="result_test"),
    path("test/create/", views.SimpleTestCreateView.as_view(), name="create_test"),
    path('user/create/', views.CustomUserCreate.as_view(), name="create_user"),
]
