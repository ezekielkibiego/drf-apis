from django.urls import path, include
from .views import index
from .views import StudentViewSet, CourseViewSet, EnrollmentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)), 
]