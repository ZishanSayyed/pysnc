from rest_framework.routers import DefaultRouter
from .views import ClassViewSet, StudentSubjectEnrollmentViewSet

router = DefaultRouter()
router.register('enrollments', StudentSubjectEnrollmentViewSet, basename='enrollments')
router.register('', ClassViewSet, basename='classes')

urlpatterns = router.urls
