from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',     include('apps.accounts.urls')),
    path('api/schools/',  include('apps.schools.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/parents/',  include('apps.parents.urls')),
    path('api/teachers/', include('apps.teachers.urls')),
    path('api/classes/',  include('apps.classes.urls')),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/timetable/", include("apps.timetable.urls")),

]
