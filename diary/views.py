from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Grade, Student, Subject
from datetime import datetime


class TeacherDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "diary/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        combos = (
            Grade.objects.filter(teacher=self.request.user)
            .values("subject__id", "subject__name", "student__student_class")
            .distinct()
        )
        context["combos"] = combos
        return context


class SubjectClassDetailView(LoginRequiredMixin, TemplateView):
    template_name = "diary/subject_class.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs.get("subject_id")
        student_class = self.kwargs.get("student_class")
        teacher = self.request.user

        subject_obj = get_object_or_404(Subject, id=subject_id)
        students = list(
            Student.objects.filter(student_class=student_class).order_by(
                "last_name", "first_name"
            )
        )
        grades_qs = Grade.objects.filter(
            teacher=teacher, subject=subject_obj, student__student_class=student_class
        )
        dates = list(
            grades_qs.values_list("date", flat=True).distinct().order_by("date")
        )

        grade_map = {}
        for grade in grades_qs:
            key = (grade.student.id, grade.date)
            grade_map[key] = grade

        rows = []
        for student in students:
            row = {"student": student, "grades": [], "grade_pairs": [], "average": None}
            sum_grades = 0
            count_grades = 0
            grade_list = []
            for date in dates:
                key = (student.id, date)
                g = grade_map.get(key)
                grade_list.append(g)
                if g:
                    sum_grades += g.value
                    count_grades += 1
            row["grades"] = grade_list
            row["grade_pairs"] = list(zip(dates, grade_list))
            row["average"] = (
                round(sum_grades / count_grades, 2) if count_grades else "-"
            )
            rows.append(row)

        context["subject"] = subject_obj
        context["student_class"] = student_class
        context["dates"] = dates
        context["rows"] = rows
        return context


class GradeEditView(LoginRequiredMixin, UpdateView):
    model = Grade
    fields = ["value", "comment"]
    template_name = "diary/grade_edit.html"

    def get_success_url(self):
        subject_id = self.object.subject.id
        student_class = self.object.student.student_class
        return reverse_lazy(
            "subject_class_detail",
            kwargs={"subject_id": subject_id, "student_class": student_class},
        )


class GradeCreateCellView(LoginRequiredMixin, CreateView):
    model = Grade
    fields = ["value", "comment"]
    template_name = "diary/grade_create.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["student"] = self.kwargs.get("student_id")
        initial["date"] = self.kwargs.get("grade_date")
        return initial

    def form_valid(self, form):
        subject_id = self.kwargs.get("subject_id")
        student_id = self.kwargs.get("student_id")
        grade_date = self.kwargs.get("grade_date")
        form.instance.teacher = self.request.user
        form.instance.subject = get_object_or_404(Subject, id=subject_id)
        form.instance.student = get_object_or_404(Student, id=student_id)
        form.instance.date = grade_date  # Устанавливаем дату из URL
        return super().form_valid(form)

    def get_success_url(self):
        subject_id = self.kwargs.get("subject_id")
        student_class = self.kwargs.get("student_class")
        return reverse_lazy(
            "subject_class_detail",
            kwargs={"subject_id": subject_id, "student_class": student_class},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs.get("subject_id")
        student_class = self.kwargs.get("student_class")
        context["subject"] = get_object_or_404(Subject, id=subject_id)
        context["student_class"] = student_class
        return context


class GradeCreateGenericView(LoginRequiredMixin, CreateView):
    model = Grade
    fields = ["student", "date", "value", "comment"]
    template_name = "diary/grade_create.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        student_class = self.kwargs.get("student_class")
        form.fields["student"].queryset = Student.objects.filter(
            student_class=student_class
        ).order_by("last_name", "first_name")
        form.fields["date"].widget.attrs.update({"type": "date"})
        return form

    def form_valid(self, form):
        subject_id = self.kwargs.get("subject_id")
        form.instance.teacher = self.request.user
        form.instance.subject = get_object_or_404(Subject, id=subject_id)
        return super().form_valid(form)

    def get_success_url(self):
        subject_id = self.kwargs.get("subject_id")
        student_class = self.kwargs.get("student_class")
        return reverse_lazy(
            "subject_class_detail",
            kwargs={"subject_id": subject_id, "student_class": student_class},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs.get("subject_id")
        student_class = self.kwargs.get("student_class")
        context["subject"] = get_object_or_404(Subject, id=subject_id)
        context["student_class"] = student_class
        return context
