from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    TeacherDashboardView,
    SubjectClassDetailView,
    GradeEditView,
    GradeCreateCellView,
    GradeCreateGenericView,
)

urlpatterns = [
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path("dashboard/", TeacherDashboardView.as_view(), name="teacher-dashboard"),
    path(
        "subject/<int:subject_id>/<str:student_class>/",
        SubjectClassDetailView.as_view(),
        name="subject_class_detail",
    ),
    path("grade/edit/<int:pk>/", GradeEditView.as_view(), name="grade_edit"),
    path(
        "subject/<int:subject_id>/<str:student_class>/grade/add/<int:student_id>/<str:grade_date>/",
        GradeCreateCellView.as_view(),
        name="grade_create_cell",
    ),
    path(
        "subject/<int:subject_id>/<str:student_class>/grade/add/",
        GradeCreateGenericView.as_view(),
        name="grade_create_generic",
    ),
]


