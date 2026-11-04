from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from time import time
from decimal import Decimal, InvalidOperation
from django .utils.dateparse import parse_date
from django .utils import timezone
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .form import studentForm, TeacherForm, ClassRoomForm
from .models import Examination, Feepayment, student, classRoom, Teacher
from .models import Attendance
from .models import student
from .models import Feepayment
from django.contrib import messages
from django.db.models import Sum



@login_required
def student_detail(request, student_id):
    student_obj = get_object_or_404(student, student_id=student_id)
    return render(request, 'school_record/student_detail.html', {'student': student_obj})


@login_required
def home(request):
    total_student = student.objects.count()
    female_students = student.objects.filter(gender='Female').count()
    male_students = student.objects.filter(gender='Male').count()
    total_classes = classRoom.objects.count()
    total_teachers = Teacher.objects.count()

    return render(
        request,
        'school_record/home.html',
        {
            'total_student': total_student,
            'total_classes': total_classes,
            'female_students': female_students,
            'male_students': male_students,
            'total_classes': total_classes,
            'total_teachers': total_teachers,
        }
    )


@login_required
def add_student(request):
    if request.method == 'POST':
        form = studentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = studentForm()

    return render(request, 'school_record/add_student.html', {'form': form})


@login_required
def export_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'First Name', 'Middle Name', 'Last Name', 'Date of Birth', 'Gender', 'Class', 'Phone Number', 'Email', 'Address'
                     ])
    for record in student.objects.all():
        writer.writerow([
            record.student_id,
            record.first_name,
            record.middle_name,
            record.last_name,
            record.date_of_birth,
            record.gender,
            record.class_name,
            record.phone_number,
            record.email,
            record.address
        ])
    return response


@login_required
def export_classes_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="classes.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Class Name',
        'Description',
        'Capacity',
        'Total Students',
        'Total Teachers',
        'Remaining Spaces',
    ])
    for classroom in classRoom.objects.all():
        total_students = student.objects.filter(
            class_name=classroom.name
        ).count()
        total_teachers = Teacher.objects.filter(class_name=classroom).count()
        writer.writerow([
            classroom.name,
            classroom.description,
            classroom.capacity,
            total_students,
            total_teachers,
            max(0, classroom.capacity - total_students),
        ])
    return response


@login_required
def student_list(request):
    students = student.objects.all()
    return render(request, 'school_record/student_list.html', {
        'student': students,
        'query': '',
    })


@login_required
def edit_student(request, student_id):
    student_obj = student.objects.get(student_id=student_id)
    if request.method == 'POST':
        form = studentForm(request.POST, request.FILES, instance=student_obj)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = studentForm(instance=student_obj)

    return render(request, 'school_record/edit_student.html', {'form': form})


@login_required
def delete_student(request, student_id):
    student_obj = student.objects.get(student_id=student_id)

    if request.method == 'POST':
        student_obj.delete()
        return redirect('student_list')

    return render(request, 'school_record/delete_student.html', {'student': student_obj})


@login_required
def search_student(request):
    query = request.GET.get('q', '')
    students = (
        student.objects.filter(student_id__icontains=query)
        | student.objects.filter(first_name__icontains=query)
        | student.objects.filter(last_name__icontains=query)
    )
    return render(request, 'school_record/student_list.html', {
        'student': students,
        'query': query,
    })


@login_required
def class_list(request):
    classes = classRoom.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        classes = classes.filter(name__icontains=query)
    for classroom in classes:
        classroom.total_students = student.objects.filter(
            class_name=classroom
        ).count()
        classroom.total_teachers = Teacher.objects.filter(class_name=classroom).count()
        classroom.remaining_spaces = max (
            0,
            classroom.capacity - classroom.total_students
        )
    return render(request, 'school_record/class_list.html', {
        'classes': classes,
        'query': query,
        'total_students': sum(c.total_students for c in classes),
        'total_teachers': sum(c.total_teachers for c in classes),
    })


@login_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    classes = classRoom.objects.all()
    selected_class = request.GET.get('class_name')
    if selected_class:
        teachers = teachers.filter(class_name__id=selected_class)
    return render(request, 'school_record/teacher_list.html', {
        'teachers': teachers,
        'classes': classes,
        'selected_class': selected_class
    })

@login_required
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()

    return render(request, 'school_record/add_teacher.html', {'form': form})


@login_required
def edit_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)

    return render(
        request,
        'school_record/edit_teacher.html',
        {'form': form, 'teacher': teacher},
    )


@login_required
def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')

    return render(
        request,
        'school_record/delete_teacher.html',
        {'teacher': teacher},
    )
@login_required
def search_teacher(request):
    query = request.GET.get('q', '').strip()
    teachers = Teacher.objects.all()
    if query:
        teachers = teachers.filter(
            Q(teacher_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(subject__icontains=query)
        ).distinct()

    return render(request, 'school_record/teacher_list.html', {
        'teachers': teachers,
        'classes': classRoom.objects.all(),
        'query': query,
    })


@login_required
def teacher_detail(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    return render(request, 'school_record/teacher_detail.html', {
        'teacher': teacher
                                                                 })
@login_required
def class_teacher(request):
    classes = classRoom.objects.all()
    selected_class = request.GET.get('class_name')
    teachers = Teacher.objects.all()

    if selected_class:
        teachers = teachers.filter(class_name__id=selected_class)

    return render(request, 'school_record/class_teacher.html', {
        'classes': classes,
        'teachers': teachers,
        'selected_class': selected_class
        
    })
@login_required
def class_summary(request):
    classes = classRoom.objects.all()
    class_data = []
    for classroom in classes:
            class_data.append({
                'classroom': classroom,
                'total_students': student.objects.filter(
                    class_name=classroom
                ).count(),
                'total_teachers': Teacher.objects.filter(class_name=classroom).count()
            })

    return render(request, 'school_record/class_summary.html', {
        'classes': classes,
        'class_data': class_data
    })
@login_required
def class_detail(request, class_id):
    classroom = get_object_or_404(classRoom, id=class_id)
    students = student.objects.filter(class_name=classroom)
    teachers = Teacher.objects.filter(class_name=classroom)

    return render(request, 'school_record/class_details.html', {
        'classroom': classroom,
        'students': students,
        'teachers': teachers
    })
@login_required
def add_class(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassRoomForm()

    return render(request, 'school_record/add_class.html', {'form': form})

@login_required
def edit_class(request, class_id):
    classroom = classRoom.objects.get(id=class_id)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassRoomForm(instance=classroom)

    return render(request, 'school_record/edit_class.html', {'form': form, 'classroom': classroom})

@login_required
def attendance_list(request):
    selected_date = (
        request.POST.get('date')
        or request.GET.get('date')
        or timezone.localdate().isoformat()
    )
    attendance_date = parse_date(selected_date)
    if attendance_date is None:
        attendance_date = timezone.localdate()
        selected_date = attendance_date.isoformat()

    students = student.objects.all().order_by('first_name', 'last_name')
    saved = False
    if request.method == 'POST':
        valid_statuses = {value for value, _label in Attendance.STATUS_CHOICES}
        for current_student in students:
            status = request.POST.get(
                f'attendance_{current_student.id}',
                'Present',
            )
            if status not in valid_statuses:
                status = 'Present'
            Attendance.objects.update_or_create(
                student=current_student,
                date=attendance_date,
                defaults={'status': status},
            )
        saved = True

    attendance_records = Attendance.objects.filter(date=attendance_date)
    present_count = attendance_records.filter(status='Present').count()
    absent_count = attendance_records.filter(status='Absent').count()
    late_count = attendance_records.filter(status='Late').count()
    attendance_by_student = {
        record.student_id: record
        for record in attendance_records
    }
    student_rows = [
        {
            'student': current_student,
            'attendance': attendance_by_student.get(current_student.id),
        }
        for current_student in students
    ]
    return render(request, 'school_record/attendance_list.html', {
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count':  late_count,
        'total_marked': attendance_records.count(),
        'student_rows': student_rows,
        'selected_date': selected_date,
        'saved': saved
    })


@login_required
def export_attendance_csv(request):
    selected_date = request.GET.get('date') or timezone.localdate().isoformat()
    attendance_date = parse_date(selected_date)
    if attendance_date is None:
        attendance_date = timezone.localdate()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Student ID', 'First Name', 'Last Name', 'Status'])
    records = Attendance.objects.filter(date=attendance_date).select_related(
        'student'
    ).order_by('student__first_name', 'student__last_name')
    for record in records:
        writer.writerow([
            record.date,
            record.student.student_id,
            record.student.first_name,
            record.student.last_name,
            record.status,
        ])
    return response
@login_required
def examination_list(request):
    students = student.objects.all().order_by('first_name', 'last_name')
    errors = []
    if request.method == 'POST':
        student_id = request.POST.get('student')
        subject = request.POST.get('subject', '').strip()
        term = request.POST.get('term', '')
        session = request.POST.get('session', '').strip()
        test_score_input = request.POST.get('test_score', '')
        exam_score_input = request.POST.get('exam_score', '')

        if not all((student_id, subject, term, session, test_score_input, exam_score_input)):
            errors.append('Complete all fields before saving the examination record.')
        if term not in dict(Examination.TERM_CHOICES):
            errors.append('Select a valid examination term.')

        selected_student = None
        if student_id:
            try:
                selected_student = student.objects.get(pk=student_id)
            except (student.DoesNotExist, ValueError, TypeError):
                errors.append('Select a valid student.')

        test_score = exam_score = None
        try:
            test_score = Decimal(test_score_input)
            exam_score = Decimal(exam_score_input)
            if not test_score.is_finite() or not exam_score.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            errors.append('Enter valid numeric scores.')

        if test_score is not None and exam_score is not None:
            if (
                test_score < 0
                or test_score > 100
                or exam_score < 0
                or exam_score > 100
                or test_score + exam_score > 100
            ):
                errors.append('Scores must be between 0 and 100 and total no more than 100.')
            elif (
                test_score.quantize(Decimal('0.01')) != test_score
                or exam_score.quantize(Decimal('0.01')) != exam_score
            ):
                errors.append('Scores can have no more than two decimal places.')

        if not errors and selected_student is not None:
            Examination.objects.create(
                student=selected_student,
                subject=subject,
                term=term,
                session=session,
                test_score=test_score,
                exam_score=exam_score,
            )
        else:
            messages.error(request, 'Invalid scores. Each score must be between 0 and 100, and the total cannot exceed 100.')
            messages.success(request, 'Examination record saved successfully!')
            return redirect('examination_list')

    return render(request, 'school_record/examination_list.html', {
        'examinations': Examination.objects.select_related('student').all(),
        'students': students,
        'term_choices': Examination.TERM_CHOICES,
        'errors': errors,
    })
    
@login_required
def student_report_card(request):
    students = student.objects.all().order_by('first_name', 'last_name')
    selected_student_id = request.GET.get('student')
    selected_term = request.GET.get('term')
    selected_session = request.GET.get('session')
    selected_student = None
    examination = Examination.objects.none()

    if selected_student_id:
        try:
            selected_student = students.filter(pk=selected_student_id).first()
        except (ValueError, TypeError):
            selected_student = None

    total_score = Decimal('0')
    subject_count = 0
    average_score = Decimal('0')
    present_days = 0
    absent_days = 0
    late_days = 0
    total_days = 0
    attendance_percentage = 0
    class_position = None
    peformance_remark = 'No examination results available yet.'

    if selected_student:
        examination = Examination.objects.filter(student=selected_student)
        if selected_term:
            examination = examination.filter(term=selected_term)
        if selected_session:
            examination = examination.filter(session=selected_session)

        examination_records = list(examination)
        subject_count = len(examination_records)
        total_score = sum(
            (record.total_score for record in examination_records),
            Decimal('0'),
        )
        if subject_count:
            average_score = total_score / subject_count
            if average_score >= 70:
                peformance_remark = 'Excellent performance. Keep it up!'
            elif average_score >= 60:
                peformance_remark = 'Very good performance. You can do better!'
            elif average_score >= 50:
                peformance_remark = 'Good performance. Keep improving!'
            elif average_score >= 40:
                peformance_remark = 'Fair performance. More effort is needed!'
            else:
                peformance_remark = 'Needs improvement. More dedication is required!'

            class_averages = []
            classmates = students.filter(class_name=selected_student.class_name)
            for classmate in classmates:
                classmate_examinations = Examination.objects.filter(student=classmate)
                if selected_term:
                    classmate_examinations = classmate_examinations.filter(
                        term=selected_term
                    )
                if selected_session:
                    classmate_examinations = classmate_examinations.filter(
                        session=selected_session
                    )
                scores = list(classmate_examinations)
                if scores:
                    classmate_average = sum(
                        (record.total_score for record in scores),
                        Decimal('0'),
                    ) / len(scores)
                    class_averages.append((classmate.id, classmate_average))

            class_averages.sort(key=lambda item: item[1], reverse=True)
            class_position = next(
                (
                    index
                    for index, (classmate_id, _average) in enumerate(
                        class_averages,
                        start=1,
                    )
                    if classmate_id == selected_student.id
                ),
                None,
            )

        attendance_records = Attendance.objects.filter(student=selected_student)
        present_days = attendance_records.filter(status='Present').count()
        absent_days = attendance_records.filter(status='Absent').count()
        late_days = attendance_records.filter(status='Late').count()
        total_days = attendance_records.count()
        if total_days:
            attendance_percentage = present_days / total_days * 100

    return render(
        request,
        'school_record/student_report_card.html',
        {
            'peformance_remark': peformance_remark,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'total_days': total_days,
            'attendance_percentage': attendance_percentage,
            'students': students,
            'selected_term': selected_term,
            'selected_session': selected_session,
            'selected_student': selected_student,
            'examination': examination,
            'examination_records': examination,
            'total_score': total_score,
            'subject_count': subject_count,
            'average_score': average_score,
            'class_position': class_position,
            'term_choices': Examination.TERM_CHOICES,
        },
    )
        
@login_required
def fee_payment_list(request):
    students = student.objects.all().order_by('first_name', 'last_name')
    if request.method == 'POST':
        student_id = request.POST.get('student')
        amount_paid = request.POST.get('amount_paid')
        payment_date = request.POST.get('payment_date')
        term = request.POST.get('term')
        session = request.POST.get('session')
        payment_reference = request.POST.get('payment_reference')
        description = request.POST.get('description')

        try:
            amount = Decimal(amount_paid)
            selected_student = student.objects.get(pk=student_id)
            parsed_payment_date = parse_date(payment_date)

            if (
                not amount.is_finite()
                or amount <= 0
                or parsed_payment_date is None
                or not term
                or not session
            ):
                raise ValueError

            Feepayment.objects.create(
                student=selected_student,
                amount_paid=amount,
                payment_date=parsed_payment_date,
                term=term,
                session=session,
                payment_refeference=payment_reference or '',
                description=description or '',
            )
            messages.success(request, 'Fee payment recorded successfully!')
        except (InvalidOperation, TypeError, ValueError, student.DoesNotExist):
            messages.error(request, 'Invalid payment information.')

    payments = Feepayment.objects.select_related('student').all()
    total_payments = sum(payment.amount_paid for payment in payments
                         )
    payments_count = payments.count()
    student_payments = students.annotate(
        total_paid=Sum('feepayment__amount_paid')
    )
    return render(
        request,
        'school_record/fee_payment_list.html',
        {
            'student_payments': student_payments,
            'payments': payments,
            'total_payments': total_payments,
            'payments_count': payments_count,
            'students': students,
            'terms_choice': Examination.TERM_CHOICES,
        },)
    
@login_required
def edit_fee_payment(request, payment_id):
    payment = get_object_or_404(Feepayment, id=payment_id)
    if request.method == 'POST':
        students = student.objects.all().order_by('first_name', 'last_name')
        if request.method == 'POST':
            payment.student = student.objects.get(id=request.POST.get('student')
                                                  )
            payment.amount_paid =request.POST.get('amount_paid')
            payment.payment_date =request.POST.get('payment_date')
            payment.term =request.POST.get('term')
            payment.session =request.POST.get('session')
            payment.payment_refeference =request.POST.get('payment_reference')
            payment.description =request.POST.get('description')
            payment.save()
            messages.success(
                request,
                'payment records updated successfully'
            )
    return redirect(
        'fee_payment_list'
    )
    return render(
        request,
        'school_record/edit_fee_payment.html',
        {
            'payment': payment,
            'students':students,
            'terms_choice': Examination.TERM_CHOICES,
        }     
    )
    
@login_required
def delete_fee_payment(reguest,payment_id):
    payment = get_object_or_404 