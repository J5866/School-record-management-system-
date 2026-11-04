from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Attendance, Examination, Teacher, classRoom, student


class HomeViewTests(TestCase):
    def test_home_page_renders_dashboard_for_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='admin', password='secret123')
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Total students')


class StudentViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(user)

    def test_student_list_alias_renders(self):
        response = self.client.get('/student-list', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/student-list/')

    def test_student_list_displays_student_records(self):
        student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name='Grade 1',
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )

        response = self.client.get(reverse('student_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Records: 1')
        self.assertContains(response, 'S001')
        self.assertContains(response, 'Grade 1')

    def test_student_csv_export_includes_student_class_name(self):
        student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name='Grade 1',
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )

        response = self.client.get(reverse('export_students_csv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn(b'Grade 1', response.content)


class ClassViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(user)

    def test_class_list_shows_add_link_when_no_classes_exist(self):
        response = self.client.get(reverse('class_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('add_class'))
        self.assertContains(response, reverse('export_classes_csv'))
        self.assertContains(response, 'No classes have been added yet.')

    def test_class_csv_export_includes_class_and_counts(self):
        classroom = classRoom.objects.create(
            name='Grade 1',
            description='First grade',
            capacity=30,
        )
        student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name=classroom.name,
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )
        Teacher.objects.create(
            teacher_id='T001',
            first_name='Alex',
            last_name='Smith',
            middle_name='Jordan',
            subject='Math',
            class_name=classroom,
            phone_number='555-0100',
            email='alex@example.com',
            address='School',
        )

        response = self.client.get(reverse('export_classes_csv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="classes.csv"',
        )
        self.assertIn(
            b'Grade 1,First grade,30,1,1,29',
            response.content,
        )

    def test_class_list_alias_redirects_without_trailing_slash(self):
        response = self.client.get('/class-list', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/class-list/')

    def test_edit_class_without_id_redirects_to_class_list(self):
        response = self.client.get('/edit-class', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('class_list'))

    def test_class_list_displays_existing_class(self):
        classroom = classRoom.objects.create(name='Grade 1', capacity=30)
        student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name=classroom.name,
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )

        response = self.client.get(reverse('class_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, classroom.name)
        self.assertContains(response, 'Total Students: 1')
        self.assertContains(response, reverse('class_detail', args=[classroom.id]))

    def test_class_list_search_displays_matching_classes_only(self):
        matching_class = classRoom.objects.create(name='Grade 1', capacity=30)
        classRoom.objects.create(name='Grade 2', capacity=30)

        response = self.client.get(reverse('class_list'), {'q': 'grade 1'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, matching_class.name)
        self.assertNotContains(response, 'Grade 2')
        self.assertContains(response, 'value="grade 1"')

    def test_class_list_search_shows_message_when_no_classes_match(self):
        classRoom.objects.create(name='Grade 1', capacity=30)

        response = self.client.get(reverse('class_list'), {'q': 'Grade 9'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No classes found matching "Grade 9".')

    def test_class_detail_shows_students_assigned_by_class_name(self):
        classroom = classRoom.objects.create(name='Grade 1', capacity=30)
        student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name=classroom.name,
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )

        response = self.client.get(
            reverse('class_detail', args=[classroom.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jamie')


class AttendanceViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(user)
        self.student = student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name='Grade 1',
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )

    def test_attendance_page_renders_for_selected_date(self):
        response = self.client.get(reverse('attendance_list'), {'date': '2026-11-02'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'S001')
        self.assertContains(response, 'Jamie Taylor')
        self.assertContains(response, 'Save Attendance')

    def test_attendance_post_saves_selected_status(self):
        response = self.client.post(
            reverse('attendance_list'),
            {
                'date': '2026-11-02',
                f'attendance_{self.student.id}': 'Absent',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['saved'])
        self.assertEqual(response.context['present_count'], 0)
        self.assertEqual(response.context['absent_count'], 1)
        self.assertEqual(response.context['late_count'], 0)
        self.assertEqual(response.context['total_marked'], 1)
        self.assertEqual(
            Attendance.objects.get(student=self.student, date='2026-11-02').status,
            'Absent',
        )

    def test_attendance_csv_export_contains_saved_records(self):
        Attendance.objects.create(
            student=self.student,
            date='2026-11-02',
            status='Late',
        )

        response = self.client.get(
            reverse('export_attendance_csv'),
            {'date': '2026-11-02'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn(b'2026-11-02,S001,Jamie,Taylor,Late', response.content)


class ExaminationViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(user)
        self.student = student.objects.create(
            student_id='S001',
            first_name='Jamie',
            last_name='Taylor',
            middle_name='Lee',
            date_of_birth='2015-04-01',
            class_name='Grade 1',
            phone_number='555-0101',
            gender='Female',
            address='School Road',
            email='jamie@example.com',
        )

    def test_examination_page_renders_term_choices(self):
        response = self.client.get(reverse('examination_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First Term')
        self.assertContains(response, 'name="test_score"')

    def test_valid_examination_record_is_saved(self):
        response = self.client.post(
            reverse('examination_list'),
            {
                'student': self.student.id,
                'subject': 'Mathematics',
                'term': 'First Term',
                'session': '2026-2027',
                'test_score': '25.50',
                'exam_score': '70',
            },
        )

        self.assertRedirects(response, reverse('examination_list'))
        record = Examination.objects.get()
        self.assertEqual(record.student, self.student)
        self.assertEqual(record.test_score, 25.5)
        self.assertEqual(record.exam_score, 70)

    def test_invalid_total_score_is_reported_without_saving(self):
        response = self.client.post(
            reverse('examination_list'),
            {
                'student': self.student.id,
                'subject': 'Mathematics',
                'term': 'First Term',
                'session': '2026-2027',
                'test_score': '60',
                'exam_score': '50',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'total no more than 100')
        self.assertEqual(Examination.objects.count(), 0)


class TeacherViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(user)

    def test_add_teacher_page_renders(self):
        response = self.client.get(reverse('add_teacher'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Teacher')

    def test_teacher_list_alias_renders(self):
        response = self.client.get('/teacher-list', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/teacher-list/')

    def test_teacher_detail_page_renders(self):
        teacher = Teacher.objects.create(
            teacher_id='T001',
            first_name='Alex',
            last_name='Smith',
            middle_name='Jordan',
            subject='Math',
            phone_number='555-0100',
            email='alex@example.com',
            address='School',
        )

        response = self.client.get(
            reverse('teacher_detail', args=[teacher.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alex Jordan Smith')
        self.assertContains(response, reverse('teacher_list'))

    def test_edit_teacher_page_renders(self):
        teacher = Teacher.objects.create(
            teacher_id='T001',
            first_name='Alex',
            last_name='Smith',
            middle_name='Jordan',
            subject='Math',
            phone_number='555-0100',
            email='alex@example.com',
            address='School',
        )

        response = self.client.get(reverse('edit_teacher', args=[teacher.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Teacher')


class RecordImageUploadTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='secret123',
        )
        self.client.force_login(user)

        media_directory = tempfile.TemporaryDirectory()
        self.addCleanup(media_directory.cleanup)
        media_settings = override_settings(MEDIA_ROOT=media_directory.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

    @staticmethod
    def make_image_upload(name):
        image_data = BytesIO()
        Image.new('RGB', (1, 1), color='blue').save(image_data, format='PNG')
        return SimpleUploadedFile(
            name,
            image_data.getvalue(),
            content_type='image/png',
        )

    def test_student_image_can_be_added_and_replaced(self):
        student_data = {
            'student_id': 'S100',
            'first_name': 'Jamie',
            'last_name': 'Taylor',
            'middle_name': 'Lee',
            'date_of_birth': '2015-04-01',
            'class_name': 'Grade 1',
            'phone_number': '555-0101',
            'gender': 'Female',
            'address': 'School Road',
            'email': 'jamie@example.com',
        }
        response = self.client.post(
            reverse('add_student'),
            {**student_data, 'image': self.make_image_upload('student.png')},
        )

        self.assertRedirects(response, reverse('home'))
        record = student.objects.get(student_id='S100')
        original_image = record.image.name
        self.assertTrue(original_image.startswith('student_images/'))

        response = self.client.post(
            reverse('edit_student', args=[record.student_id]),
            {**student_data, 'image': self.make_image_upload('updated.png')},
        )

        self.assertRedirects(response, reverse('student_list'))
        record.refresh_from_db()
        self.assertTrue(record.image.name.startswith('student_images/'))
        self.assertNotEqual(record.image.name, original_image)

        response = self.client.get(reverse('student_detail', args=[record.student_id]))
        self.assertContains(response, record.image.url)

    def test_teacher_image_can_be_added_and_replaced(self):
        teacher_data = {
            'teacher_id': 'T100',
            'first_name': 'Alex',
            'last_name': 'Smith',
            'middle_name': 'Jordan',
            'subject': 'Math',
            'phone_number': '555-0100',
            'email': 'alex@example.com',
            'address': 'School',
        }
        response = self.client.post(
            reverse('add_teacher'),
            {**teacher_data, 'image': self.make_image_upload('teacher.png')},
        )

        self.assertRedirects(response, reverse('teacher_list'))
        record = Teacher.objects.get(teacher_id='T100')
        original_image = record.image.name
        self.assertTrue(original_image.startswith('teacher_images/'))

        response = self.client.post(
            reverse('edit_teacher', args=[record.id]),
            {**teacher_data, 'image': self.make_image_upload('updated.png')},
        )

        self.assertRedirects(response, reverse('teacher_list'))
        record.refresh_from_db()
        self.assertTrue(record.image.name.startswith('teacher_images/'))
        self.assertNotEqual(record.image.name, original_image)

        response = self.client.get(reverse('teacher_detail', args=[record.id]))
        self.assertContains(response, record.image.url)
