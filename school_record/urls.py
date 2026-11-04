from django.urls import path
from django.views.generic.base import RedirectView
from . import views
from django.contrib.auth import views as auth_views
from school_record.views import (
    add_student,
    add_teacher,
    edit_teacher,
    home,
    student_list,
    edit_student,
    delete_student,
    search_student,
    student_detail,
    class_list,
    teacher_detail,
    teacher_list,
    class_teacher,
    
)


urlpatterns = [
    path('fee-payments/edit/<int:payment_id>/',views.edit_fee_payment,name='edit_fee_payment'),
    path('fee-payment/', views.fee_payment_list, name='fee_payment_list'),
    path('report-card/', views.student_report_card, name='student_report_card'),
    path('examination/', views.examination_list, name='examination_list'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/export/', views.export_attendance_csv, name='export_attendance_csv'),
    path('export-students/',views.export_students_csv, name='export_students_csv'),
    path('export-classes/', views.export_classes_csv, name='export_classes_csv'),
    path('class-teacher/', views.class_teacher, name='class_teacher'),
    path('class-summary/', views.class_summary, name='class_summary'),
    path('class-detail/<int:class_id>/', views.class_detail, name='class_detail'),
    path('add-class/', views.add_class, name='add_class'),
    path('edit-class/', RedirectView.as_view(pattern_name='class_list')),
    path('edit-class/<int:class_id>/', views.edit_class, name='edit_class'),
    path('', home, name='home'),
    path('dashboard/', home, name='dashboard'),
    path('add_student/', add_student, name='add_student'),
    path('student/', student_list, name='student_list'),
    path('student-list/', student_list),
    path('student_detail/<str:student_id>/', student_detail, name='student_detail'),
    path('edit_student/<str:student_id>/', edit_student, name='edit_student'),
    path('delete_student/<str:student_id>/', delete_student, name='delete_student'),
    path('search_student/', search_student, name='search_student'),
    path('classes/', class_list, name='class_list'),
    path('class-list/', class_list),
    path('teachers/', teacher_list, name='teacher_list'),
    path('teacher-list/', teacher_list),
    path('teachers/<int:id>/', teacher_detail, name='teacher_detail'),
    path('add_teacher/', add_teacher, name='add_teacher'),
    path('edit-teacher/<int:id>/', edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:id>/', views.delete_teacher, name='delete_teacher'),
    path('search_teacher/', views.search_teacher, name='search_teacher'),
    path('login/', auth_views.LoginView.as_view(template_name='school_record/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
]