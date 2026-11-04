from django import forms
from .models import classRoom, student, Teacher


class studentForm(forms.ModelForm):
    class Meta:
        model = student
        fields = [
            'student_id',
            'first_name',
            'last_name',
            'middle_name',
            'date_of_birth',
            'class_name',
            'phone_number',
            'gender',
            'address',
            'email',
            'image',
        ]


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'teacher_id',
            'first_name',
            'last_name',
            'middle_name',
            'subject',
            'class_name',
            'phone_number',
            'email',
            'address',
            'image',
        ]
class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = classRoom
        fields = [
            'name',
            'description',
            'capacity',
        ]