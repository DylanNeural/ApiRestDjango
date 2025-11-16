from django.urls import path
from .views import task_list_create, task_detail, signup, logout_view,me,external_tasks
from django.views.generic import TemplateView
# Auth JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('tasks/', task_list_create, name='task-list-create'),
    path('tasks/<int:pk>/', task_detail, name='task-detail'),
    path(
        "tasks/pagination/",
        TemplateView.as_view(template_name="test.html"),  # ✅ test.html
        name="tasks-pagination",
    ),
    
    # 🔹 API tierce
    path("external-tasks/", external_tasks, name="external-tasks"),
    
    # Auth JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('me/', me, name='me'),
]
