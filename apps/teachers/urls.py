from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, SubjectViewSet, TeacherSchoolAssignmentViewSet

router = DefaultRouter()
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('assignments', TeacherSchoolAssignmentViewSet, basename='teacher-assignments')
router.register('', TeacherViewSet, basename='teachers')

urlpatterns = router.urls
