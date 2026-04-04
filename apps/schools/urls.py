from django.urls import path
from .views import SchoolListCreateView, SchoolDetailView

urlpatterns = [
    path('', SchoolListCreateView.as_view()),
    path('<uuid:pk>/', SchoolDetailView.as_view()),
]