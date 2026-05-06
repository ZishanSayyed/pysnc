from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamSubjectViewSet, StudentResultViewSet

router = DefaultRouter()
router.register(r"exams", ExamViewSet, basename="exams")
router.register(r"exam-subjects", ExamSubjectViewSet, basename="exam-subjects")
router.register(r"results", StudentResultViewSet, basename="results")

urlpatterns = [
    path("", include(router.urls)),
]
