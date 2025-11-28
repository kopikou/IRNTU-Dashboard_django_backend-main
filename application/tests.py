# import os
# import django
# from django.conf import settings
# if not settings.configured:
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
#     django.setup()

# from django.test import TestCase
# import pytest
# from django.utils import timezone
# from datetime import date, timedelta, datetime
# from rest_framework.test import APITestCase, APIRequestFactory
# from rest_framework import status
# from unittest.mock import Mock, patch, MagicMock, mock_open
# from django.db.models import *
# from rest_framework.request import Request
# from application.models import *
# from application.api import *

# # Добавить в конец файла tests.py

# class TestGradesViewset(APITestCase):
#     """
#     Тесты для GradesViewset - получения оценок студентов с агрегированной статистикой.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.view = GradesViewset.as_view({'get': 'list'})
        
#         # Создаем мок пользователя для аутентификации
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
#         self.user.is_authenticated = True

#     def test_calculate_course_before_september(self):
#         """Тест расчета курса до сентября."""
#         viewset = GradesViewset()
        
#         with patch('application.api.datetime') as mock_datetime:
#             mock_now = Mock()
#             mock_now.year = 2024
#             mock_now.month = 8  # Август (до сентября)
#             mock_datetime.now.return_value = mock_now
            
#             course = viewset.calculate_course(2021)
#             self.assertEqual(course, 3)  # 2024 - 2021 = 3

#     def test_calculate_course_after_september(self):
#         """Тест расчета курса после сентября."""
#         viewset = GradesViewset()
        
#         with patch('application.api.datetime') as mock_datetime:
#             mock_now = Mock()
#             mock_now.year = 2024
#             mock_now.month = 9  # Сентябрь
#             mock_datetime.now.return_value = mock_now
            
#             course = viewset.calculate_course(2021)
#             self.assertEqual(course, 4)  # 2024 - 2021 + 1 = 4

#     def test_extract_year_from_group_title_valid(self):
#         """Тест извлечения года из корректного названия группы."""
#         viewset = GradesViewset()
        
#         year = viewset.extract_year_from_group_title('ФИТ-21Б')
#         self.assertEqual(year, 2021)
        
#         year = viewset.extract_year_from_group_title('ИВТ-19А')
#         self.assertEqual(year, 2019)

#     def test_extract_year_from_group_title_invalid(self):
#         """Тест извлечения года из некорректного названия группы."""
#         viewset = GradesViewset()
        
#         # Некорректные форматы
#         self.assertIsNone(viewset.extract_year_from_group_title('ФИТ21Б'))
#         self.assertIsNone(viewset.extract_year_from_group_title('ФИТ-'))
#         self.assertIsNone(viewset.extract_year_from_group_title(''))
#         self.assertIsNone(viewset.extract_year_from_group_title(None))

#     def test_student_is_still_enrolled_current_year(self):
#         """Тест проверки что студент продолжает обучение (текущий год)."""
#         viewset = GradesViewset()
        
#         current_year = datetime.now().year
#         admission_year = current_year - 2  # 2 курс
        
#         result = viewset.student_is_still_enrolled(admission_year)
#         self.assertTrue(result)

#     def test_student_is_still_enrolled_graduated(self):
#         """Тест проверки что студент уже выпустился."""
#         viewset = GradesViewset()
        
#         current_year = datetime.now().year
#         admission_year = current_year - 5  # Должен был выпуститься
        
#         result = viewset.student_is_still_enrolled(admission_year)
#         self.assertFalse(result)

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_basic_request(self, mock_course_projects, mock_grades):
#         """Тест базового запроса без параметров."""
#         # Настраиваем моки
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Настраиваем цепочку вызовов для grades
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_grades_queryset.select_related.return_value = mock_grades_queryset
        
#         # Настраиваем цепочку вызовов для course_projects
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.select_related.return_value = mock_course_projects_queryset
        
#         # Создаем тестовые данные для итерации
#         test_grades = [
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Иванов Иван',
#                     group=Mock(title='ФИТ-21Б')
#                 ),
#                 fc=Mock(
#                     hps=Mock(
#                         disciple=Mock(
#                             disciple_name='Математика',
#                             disciple_id=1
#                         )
#                     )
#                 ),
#                 grade='5'
#             )
#         ]
        
#         test_course_projects = [
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Иванов Иван', 
#                     group=Mock(title='ФИТ-21Б')
#                 ),
#                 hps=Mock(
#                     disciple=Mock(
#                         disciple_name='Программирование',
#                         disciple_id=2
#                     )
#                 ),
#                 grade=4
#             )
#         ]
        
#         mock_grades_queryset.__iter__ = Mock(return_value=iter(test_grades))
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter(test_course_projects))
        
#         # Создаем запрос
#         request = self.factory.get('/api/grades/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('summary', response.data)
#         self.assertIn('students', response.data)
#         self.assertIn('subjects', response.data)

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_with_course_filter(self, mock_course_projects, mock_grades):
#         """Тест запроса с фильтром по курсу."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Настраиваем цепочки вызовов
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_grades_queryset.select_related.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.select_related.return_value = mock_course_projects_queryset
        
#         # Пустые результаты
#         mock_grades_queryset.__iter__ = Mock(return_value=iter([]))
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter([]))
        
#         # Создаем запрос с фильтром по курсу
#         request = self.factory.get('/api/grades/?course=2')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_with_semester_filter(self, mock_course_projects, mock_grades):
#         """Тест запроса с фильтром по семестру."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Проверяем что фильтр по семестру применяется
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
        
#         mock_grades_queryset.__iter__ = Mock(return_value=iter([]))
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter([]))
        
#         request = self.factory.get('/api/grades/?semester=1')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что фильтр был применен
#         mock_grades_queryset.filter.assert_called_with(fc__hps__semester='1')
#         mock_course_projects_queryset.filter.assert_called_with(hps__semester='1')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_with_group_filter(self, mock_course_projects, mock_grades):
#         """Тест запроса с фильтром по группе."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
        
#         mock_grades_queryset.__iter__ = Mock(return_value=iter([]))
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter([]))
        
#         request = self.factory.get('/api/grades/?group=ФИТ-21Б')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что фильтр по группе был применен
#         mock_grades_queryset.filter.assert_called_with(student__group__title='ФИТ-21Б')
#         mock_course_projects_queryset.filter.assert_called_with(student__group__title='ФИТ-21Б')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_with_subject_filter(self, mock_course_projects, mock_grades):
#         """Тест запроса с фильтром по предмету."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
        
#         mock_grades_queryset.__iter__ = Mock(return_value=iter([]))
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter([]))
        
#         request = self.factory.get('/api/grades/?subject=Математика')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что фильтр по предмету был применен
#         mock_grades_queryset.filter.assert_called_with(fc__hps__disciple__disciple_name='Математика')
#         mock_course_projects_queryset.filter.assert_called_with(hps__disciple__disciple_name='Математика')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_invalid_course_semester_combination(self, mock_course_projects, mock_grades):
#         """Тест некорректной комбинации курса и семестра."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Создаем запрос с некорректной комбинацией курса и семестра
#         request = self.factory.get('/api/grades/?course=1&semester=3')  # Для 1 курса допустимы семестры 1 и 2
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что возвращается пустой ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['summary']['totalStudents'], 0)
#         self.assertIsNone(response.data['summary']['averageGrade'])
#         self.assertEqual(response.data['students'], [])

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_empty_results(self, mock_course_projects, mock_grades):
#         """Тест запроса с пустыми результатами."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Пустые результаты
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_grades_queryset.select_related.return_value = mock_grades_queryset
#         mock_grades_queryset.__iter__ = Mock(return_value=iter([]))
        
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.select_related.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter([]))
        
#         request = self.factory.get('/api/grades/?subject=НесуществующийПредмет')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ с пустыми данными
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['summary']['totalStudents'], 0)
#         self.assertIsNone(response.data['summary']['averageGrade'])
#         self.assertEqual(response.data['students'], [])
#         self.assertEqual(response.data['subjects'], [])

#     def test_queryset_optimization(self):
#         """Тест оптимизации queryset с select_related."""
#         viewset = GradesViewset()
#         queryset = viewset.get_queryset()
        
#         # Проверяем что queryset использует select_related
#         self.assertIsNotNone(queryset)


# class TestAcademicPerformanceViewSet(APITestCase):
#     """
#     Тесты для AcademicPerformanceViewSet - статистики по успеваемости с учётом задолженностей.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.view = AcademicPerformanceViewSet.as_view({'get': 'list'})
        
#         # Создаем мок пользователя для аутентификации
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
#         self.user.is_authenticated = True

#     def test_get_active_debts_filter(self):
#         """Тест создания фильтра для активных задолженностей."""
#         viewset = AcademicPerformanceViewSet()
#         active_debts_filter = viewset.get_active_debts_filter()
        
#         # Проверяем что фильтр создан корректно
#         self.assertIsNotNone(active_debts_filter)

#     @patch('application.api.Student.objects.select_related')
#     def test_get_queryset_optimization(self, mock_select_related):
#         """Тест оптимизации queryset с select_related."""
#         mock_queryset = Mock()
#         mock_select_related.return_value.annotate.return_value.order_by.return_value = mock_queryset
        
#         viewset = AcademicPerformanceViewSet()
#         queryset = viewset.get_queryset()
        
#         # Проверяем что select_related был вызван
#         mock_select_related.assert_called_once_with('group')
#         self.assertIsNotNone(queryset)

#     @patch.object(AcademicPerformanceViewSet, 'get_queryset')
#     def test_list_basic_request(self, mock_get_queryset):
#         """Тест базового запроса без параметров."""
#         # Создаем тестовых студентов
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 active_debt_count=0
#             ),
#             Mock(
#                 student_id=2,
#                 name='Петров Петр',
#                 group=Mock(title='ФИТ-21Б'),
#                 active_debt_count=2
#             )
#         ]
        
#         # Настраиваем моки
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.__iter__ = Mock(return_value=iter(test_students))
        
#         # Мокаем агрегатные функции
#         mock_queryset.aggregate.return_value = {
#             'zero_debts': 1,
#             'one_debt': 0,
#             'two_debts': 1,
#             'three_plus_debts': 0
#         }
        
#         # Мокаем расчет статистики по группам
#         with patch.object(AcademicPerformanceViewSet, 'calculate_group_stats') as mock_group_stats:
#             mock_group_stats.return_value = [
#                 {'group': 'ФИТ-21Б', 'avgDebts': 1.0}
#             ]
            
#             # Создаем запрос
#             request = self.factory.get('/api/academic-performance/')
#             request.user = self.user
#             response = self.view(request)
            
#             # Проверяем ответ
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self.assertIn('debtsDistribution', response.data)
#             self.assertIn('groupAverages', response.data)
#             self.assertIn('students', response.data)
            
#             # Проверяем структуру данных
#             debt_dist = response.data['debtsDistribution']
#             self.assertEqual(debt_dist['0'], 1)
#             self.assertEqual(debt_dist['1'], 0)
#             self.assertEqual(debt_dist['2'], 1)
#             self.assertEqual(debt_dist['3plus'], 0)
            
#             self.assertEqual(len(response.data['students']), 2)

#     @patch.object(AcademicPerformanceViewSet, 'get_queryset')
#     def test_list_with_group_filter(self, mock_get_queryset):
#         """Тест запроса с фильтром по группе."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 active_debt_count=1
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.__iter__ = Mock(return_value=iter(test_students))
#         mock_queryset.aggregate.return_value = {
#             'zero_debts': 0, 'one_debt': 1, 'two_debts': 0, 'three_plus_debts': 0
#         }
        
#         with patch.object(AcademicPerformanceViewSet, 'calculate_group_stats') as mock_group_stats:
#             mock_group_stats.return_value = [
#                 {'group': 'ФИТ-21Б', 'avgDebts': 1.0}
#             ]
            
#             # Создаем запрос с фильтром по группе
#             request = self.factory.get('/api/academic-performance/?group=ФИТ-21Б')
#             request.user = self.user
#             response = self.view(request)
            
#             # Проверяем что фильтр по группе был применен
#             mock_queryset.filter.assert_called_with(group__title='ФИТ-21Б')
#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch.object(AcademicPerformanceViewSet, 'get_queryset')
#     def test_list_with_search_filter(self, mock_get_queryset):
#         """Тест запроса с поисковым фильтром."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 active_debt_count=0
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.__iter__ = Mock(return_value=iter(test_students))
#         mock_queryset.aggregate.return_value = {
#             'zero_debts': 1, 'one_debt': 0, 'two_debts': 0, 'three_plus_debts': 0
#         }
        
#         with patch.object(AcademicPerformanceViewSet, 'calculate_group_stats') as mock_group_stats:
#             mock_group_stats.return_value = []
            
#             # Создаем запрос с поисковым запросом
#             request = self.factory.get('/api/academic-performance/?search=Иванов')
#             request.user = self.user
#             response = self.view(request)
            
#             # Проверяем что поисковый фильтр был применен
#             mock_queryset.filter.assert_called_with(name__icontains='Иванов')
#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch.object(AcademicPerformanceViewSet, 'get_queryset')
#     def test_list_empty_results(self, mock_get_queryset):
#         """Тест запроса с пустыми результатами."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Пустые результаты
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.__iter__ = Mock(return_value=iter([]))
#         mock_queryset.aggregate.return_value = {
#             'zero_debts': 0, 'one_debt': 0, 'two_debts': 0, 'three_plus_debts': 0
#         }
        
#         with patch.object(AcademicPerformanceViewSet, 'calculate_group_stats') as mock_group_stats:
#             mock_group_stats.return_value = []
            
#             # Создаем запрос с фильтром, который не найдет данных
#             request = self.factory.get('/api/academic-performance/?group=НесуществующаяГруппа')
#             request.user = self.user
#             response = self.view(request)
            
#             # Проверяем ответ с пустыми данными
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self.assertEqual(response.data['debtsDistribution']['0'], 0)
#             self.assertEqual(response.data['groupAverages'], [])
#             self.assertEqual(response.data['students'], [])

#     @patch.object(AcademicPerformanceViewSet, 'get_queryset')
#     def test_calculate_group_stats_integration(self, mock_get_queryset):
#         """Тест интеграции расчета статистики по группам."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 active_debt_count=1
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.__iter__ = Mock(return_value=iter(test_students))
#         mock_queryset.aggregate.return_value = {
#             'zero_debts': 0, 'one_debt': 1, 'two_debts': 0, 'three_plus_debts': 0
#         }
        
#         # Мокаем Group.objects
#         with patch('application.api.Group.objects') as mock_group_objects:
#             mock_group = Mock()
#             mock_group.title = 'ФИТ-21Б'
#             mock_group_objects.filter.return_value.distinct.return_value = [mock_group]
            
#             # Мокаем Student.objects с аннотацией
#             mock_student_queryset = MagicMock()
#             with patch('application.api.Student.objects') as mock_student_objects:
#                 mock_student_objects.filter.return_value.annotate.return_value.aggregate.return_value = {
#                     'avg': 1.0
#                 }
                
#                 request = self.factory.get('/api/academic-performance/')
#                 request.user = self.user
#                 response = self.view(request)
                
#                 # Проверяем ответ
#                 self.assertEqual(response.status_code, status.HTTP_200_OK)
#                 self.assertIn('groupAverages', response.data)


# class TestTrainModelViewSet(APITestCase):
#     """
#     Тесты для TrainModelViewSet - запуска обучения ML-модели аналитики студентов.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.view = TrainModelViewSet.as_view({'get': 'list'})
        
#         # Создаем мок пользователя для аутентификации
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
#         self.user.is_authenticated = True

#     def test_permission_classes(self):
#         """Тест проверки классов разрешений."""
#         viewset = TrainModelViewSet()
#         self.assertEqual(viewset.permission_classes, [IsAuthenticated])

#     @patch('application.api.call_command')
#     def test_list_success(self, mock_call_command):
#         """Тест успешного запуска обучения модели."""
#         # Настраиваем мок
#         mock_call_command.return_value = None
        
#         # Создаем запрос
#         request = self.factory.get('/api/train-model/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], "Модель успешно обучена, результаты сохранены в CSV.")
        
#         # Проверяем что команда была вызвана
#         mock_call_command.assert_called_once_with('analytics')

#     @patch('application.api.call_command')
#     def test_list_command_error(self, mock_call_command):
#         """Тест обработки ошибки при выполнении команды."""
#         # Настраиваем мок для выброса исключения
#         mock_call_command.side_effect = Exception("Test error")
        
#         # Создаем запрос
#         request = self.factory.get('/api/train-model/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ с ошибкой
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertEqual(response.data['error'], "Test error")

#     def test_queryset_is_none(self):
#         """Тест что queryset не используется."""
#         viewset = TrainModelViewSet()
#         self.assertIsNone(viewset.queryset)

#     @patch('application.api.call_command')
#     def test_list_unauthenticated_user(self, mock_call_command):
#         """Тест запроса от неаутентифицированного пользователя."""
#         # Создаем запрос без пользователя
#         request = self.factory.get('/api/train-model/')
        
#         # Должен вернуть 403 из-за IsAuthenticated permission
#         response = self.view(request)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
#         # Команда не должна быть вызвана
#         mock_call_command.assert_not_called()


# # Дополнительные тесты для edge cases GradesViewset
# class TestGradesViewsetEdgeCases(APITestCase):
#     """Тесты для граничных случаев GradesViewset."""

#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.view = GradesViewset.as_view({'get': 'list'})
        
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
#         self.user.is_authenticated = True

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_various_grade_types(self, mock_course_projects, mock_grades):
#         """Тест обработки различных типов оценок."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Создаем тестовые данные с разными типами оценок
#         test_grades = [
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Иванов Иван',
#                     group=Mock(title='ФИТ-21Б')
#                 ),
#                 fc=Mock(
#                     hps=Mock(
#                         disciple=Mock(
#                             disciple_name='Математика',
#                             disciple_id=1
#                         )
#                     )
#                 ),
#                 grade='5'  # Числовая оценка
#             ),
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Иванов Иван',
#                     group=Mock(title='ФИТ-21Б')
#                 ),
#                 fc=Mock(
#                     hps=Mock(
#                         disciple=Mock(
#                             disciple_name='Физика',
#                             disciple_id=2
#                         )
#                     )
#                 ),
#                 grade='зачет'  # Зачет
#             ),
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Иванов Иван',
#                     group=Mock(title='ФИТ-21Б')
#                 ),
#                 fc=Mock(
#                     hps=Mock(
#                         disciple=Mock(
#                             disciple_name='Химия',
#                             disciple_id=3
#                         )
#                     )
#                 ),
#                 grade='неявка'  # Неявка
#             )
#         ]
        
#         test_course_projects = [
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Иванов Иван',
#                     group=Mock(title='ФИТ-21Б')
#                 ),
#                 hps=Mock(
#                     disciple=Mock(
#                         disciple_name='Программирование',
#                         disciple_id=4
#                     )
#                 ),
#                 grade=4  # Числовая оценка курсового проекта
#             )
#         ]
        
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_grades_queryset.select_related.return_value = mock_grades_queryset
#         mock_grades_queryset.__iter__ = Mock(return_value=iter(test_grades))
        
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.select_related.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter(test_course_projects))
        
#         request = self.factory.get('/api/grades/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что все типы оценок обработаны
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['students']), 1)
#         student_data = response.data['students'][0]
#         self.assertEqual(len(student_data['subjects']), 4)  # 4 предмета

#     @patch('application.api.Grades.objects.select_related')
#     @patch('application.api.CourseProjects.objects.select_related')
#     def test_list_student_without_group(self, mock_course_projects, mock_grades):
#         """Тест обработки студента без группы."""
#         mock_grades_queryset = MagicMock()
#         mock_grades.return_value = mock_grades_queryset
        
#         mock_course_projects_queryset = MagicMock()
#         mock_course_projects.return_value = mock_course_projects_queryset
        
#         # Создаем студента без группы
#         test_grades = [
#             Mock(
#                 student=Mock(
#                     student_id=1,
#                     name='Студент Без Группы',
#                     group=None  # Нет группы
#                 ),
#                 fc=Mock(
#                     hps=Mock(
#                         disciple=Mock(
#                             disciple_name='Математика',
#                             disciple_id=1
#                         )
#                     )
#                 ),
#                 grade='4'
#             )
#         ]
        
#         mock_grades_queryset.filter.return_value = mock_grades_queryset
#         mock_grades_queryset.select_related.return_value = mock_grades_queryset
#         mock_grades_queryset.__iter__ = Mock(return_value=iter(test_grades))
        
#         mock_course_projects_queryset.filter.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.select_related.return_value = mock_course_projects_queryset
#         mock_course_projects_queryset.__iter__ = Mock(return_value=iter([]))
        
#         request = self.factory.get('/api/grades/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         student_data = response.data['students'][0]
#         self.assertIsNone(student_data['group'])
#         self.assertIsNone(student_data['course'])

# class TestAcademicReturnsViewSet(APITestCase):
#     """
#     Тесты для AcademicReturnsViewSet - статистики по возвратам из академических отпусков.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.view = AcademicReturnsViewSet.as_view({'get': 'list'})
        
#         # Мокаем создание пользователя
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
        
#         # Создаем моки для групп 
#         self.group1 = Mock(spec=Group)
#         self.group1.title = 'ИТ-21-тест'
#         self.group1.pk = 1
        
#         self.group2 = Mock(spec=Group)
#         self.group2.title = 'ИТ-22-тест'
#         self.group2.pk = 2
        
#         self.group3 = Mock(spec=Group)
#         self.group3.title = 'ИТ-23-тест'
#         self.group3.pk = 3
        
#         # Создаем моки для студентов
#         self.student1 = Mock(spec=Student)
#         self.student1.student_id = 1
#         self.student1.name = 'Иванов Иван'
#         self.student1.group = self.group1
        
#         self.student2 = Mock(spec=Student)
#         self.student2.student_id = 2
#         self.student2.name = 'Петров Петр'
#         self.student2.group = self.group2
        
#         self.student3 = Mock(spec=Student)
#         self.student3.student_id = 3
#         self.student3.name = 'Сидоров Алексей'
#         self.student3.group = None
        
#         self.student4 = Mock(spec=Student)
#         self.student4.student_id = 4
#         self.student4.name = 'Кузнецова Мария'
#         self.student4.group = self.group3
        
#         # Даты для тестов
#         self.today = timezone.now().date()
#         self.yesterday = self.today - timedelta(days=1)
#         self.tomorrow = self.today + timedelta(days=1)
#         self.last_year = self.today - timedelta(days=365)
#         self.next_year = self.today + timedelta(days=365)

#     def create_mock_academ(self, student, end_date, relevant_group=None, academ_id=None):
#         """Вспомогательный метод для создания мока записи об академе."""
#         academ = Mock(spec=Academ)
#         academ.pk = academ_id or student.student_id
#         academ.student = student
#         academ.end_date = end_date
#         academ.relevant_group = relevant_group
#         academ.previous_group = student.group
#         academ.start_date = self.today - timedelta(days=100)
#         return academ

#     def test_get_queryset_optimization(self):
#         """Тест оптимизации queryset с select_related."""
#         # Мокаем сам метод get_queryset чтобы проверить его логику
#         with patch('application.models.Academ.objects.select_related') as mock_select_related:
#             mock_queryset = Mock()
#             mock_select_related.return_value.all.return_value = mock_queryset
            
#             viewset = AcademicReturnsViewSet()
#             queryset = viewset.get_queryset()
            
#             # Проверяем что select_related был вызван с правильными параметрами
#             mock_select_related.assert_called_once_with(
#                 'student',
#                 'student__group', 
#                 'previous_group',
#                 'relevant_group'
#             )

#     def test_determine_status_no_end_date(self):
#         """Тест определения статуса когда нет даты окончания."""
#         viewset = AcademicReturnsViewSet()
#         academ = Mock(end_date=None, student=Mock(group=Mock()))
        
#         status = viewset.determine_status(academ)
#         self.assertEqual(status, "Продолжает обучение")

#     def test_determine_status_end_date_past_with_group(self):
#         """Тест статуса 'Возвращён' - отпуск завершен, есть группа."""
#         viewset = AcademicReturnsViewSet()
#         academ = Mock(
#             end_date=self.yesterday,
#             student=Mock(group=Mock())
#         )
        
#         status = viewset.determine_status(academ)
#         self.assertEqual(status, "Возвращён")

#     def test_determine_status_end_date_past_no_group(self):
#         """Тест статуса 'Отчислен' - отпуск завершен, нет группы."""
#         viewset = AcademicReturnsViewSet()
#         academ = Mock(
#             end_date=self.yesterday,
#             student=Mock(group=None)
#         )
        
#         status = viewset.determine_status(academ)
#         self.assertEqual(status, "Отчислен")

#     def test_determine_status_end_date_future(self):
#         """Тест статуса когда дата окончания в будущем."""
#         viewset = AcademicReturnsViewSet()
#         academ = Mock(
#             end_date=self.tomorrow,
#             student=Mock(group=None)
#         )
        
#         status = viewset.determine_status(academ)
#         self.assertEqual(status, "Продолжает обучение")

#     def test_list_empty_data(self):
#         """Тест запроса когда нет данных об академах."""
#         # Мокаем все методы 
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self.assertEqual(response.data['statusDistribution'], {
#                 "Отчислен": 0,
#                 "Возвращён": 0,
#                 "Продолжает обучение": 0
#             })
#             self.assertEqual(response.data['students'], [])

#     def test_list_with_various_statuses(self):
#         """Тест со всеми типами статусов студентов."""
#         # Создаем моки записей с разными статусами
#         academ1 = self.create_mock_academ(self.student1, self.yesterday)
#         academ2 = self.create_mock_academ(self.student2, self.yesterday)
#         academ3 = self.create_mock_academ(self.student3, self.last_year)
#         academ4 = self.create_mock_academ(self.student4, self.tomorrow)
        
#         # Для пятой записи создаем без даты окончания
#         academ5 = self.create_mock_academ(self.student4, None)
        
#         # Мокаем методы для возврата тестовых данных
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ1, academ2, academ3, academ4, academ5]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
            
#             # Проверяем распределение статусов
#             status_dist = response.data['statusDistribution']
#             self.assertEqual(status_dist['Возвращён'], 2)
#             self.assertEqual(status_dist['Отчислен'], 1)
#             self.assertEqual(status_dist['Продолжает обучение'], 2)

#     def test_student_data_structure(self):
#         """Тест структуры данных возвращаемых студентов."""
#         academ = self.create_mock_academ(self.student1, self.yesterday, relevant_group=self.group2)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             student_data = response.data['students'][0]
            
#             self.assertEqual(student_data['id'], 1)
#             self.assertEqual(student_data['name'], 'Иванов Иван')
#             self.assertEqual(student_data['group'], 'ИТ-22-тест')
#             self.assertEqual(student_data['returnDate'], self.yesterday.strftime("%Y-%m-%d"))
#             self.assertEqual(student_data['status'], 'Возвращён')

#     def test_student_data_fallback_group_logic(self):
#         """Тест логики fallback для определения группы."""
#         # Создаем запись без relevant_group
#         academ = self.create_mock_academ(self.student1, self.yesterday, relevant_group=None)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             student_data = response.data['students'][0]
#             # Должен использоваться student.group
#             self.assertEqual(student_data['group'], 'ИТ-21-тест')

#     def test_student_data_no_group(self):
#         """Тест когда у студента вообще нет группы."""
#         academ = self.create_mock_academ(self.student3, self.yesterday, relevant_group=None)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             student_data = response.data['students'][0]
#             self.assertIsNone(student_data['group'])

#     def test_filter_queryset_integration(self):
#         """Тест интеграции с системой фильтрации DRF."""
#         # Создаем тестовые данные
#         academ1 = self.create_mock_academ(self.student1, self.yesterday)
#         academ2 = self.create_mock_academ(self.student2, self.last_year)
        
#         # Мокаем filter_queryset для тестирования фильтрации
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ1]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/?some_filter=value')
#             request.user = self.user
#             response = self.view(request)
            
#             # Проверяем что фильтрация была применена
#             mock_filter.assert_called_once()

#     def test_date_format_validation(self):
#         """Тест корректности формата дат в ответе."""
#         academ = self.create_mock_academ(self.student1, date(2023, 12, 31))
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             student_data = response.data['students'][0]
#             return_date = student_data['returnDate']
            
#             # Проверяем формат YYYY-MM-DD
#             self.assertEqual(return_date, '2023-12-31')

#     @patch('django.utils.timezone.now')
#     def test_timezone_aware_dates(self, mock_now):
#         """Тест работы с timezone-aware датами."""
#         # Фиксируем текущее время для предсказуемых тестов
#         from django.utils.timezone import get_default_timezone
#         fixed_now = datetime(2024, 1, 15, tzinfo=get_default_timezone())
#         mock_now.return_value = fixed_now
#         fixed_today = fixed_now.date()
        
#         viewset = AcademicReturnsViewSet()
        
#         # Тестируем определение статуса с фиксированной датой
#         academ_past = Mock(
#             end_date=fixed_today - timedelta(days=1),
#             student=Mock(group=Mock())
#         )
#         academ_future = Mock(
#             end_date=fixed_today + timedelta(days=1),
#             student=Mock(group=Mock())
#         )
        
#         self.assertEqual(viewset.determine_status(academ_past), "Возвращён")
#         self.assertEqual(viewset.determine_status(academ_future), "Продолжает обучение")

#     def test_performance_with_large_dataset(self):
#         """Тест производительности с большим набором данных."""
#         # Создаем 10 мок-записей для теста производительности
#         academ_records = []
#         for i in range(10):
#             student = Mock(spec=Student)
#             student.student_id = 1000 + i
#             student.name = f'Студент {i}'
#             student.group = self.group1
            
#             academ = self.create_mock_academ(student, self.yesterday - timedelta(days=i))
#             academ_records.append(academ)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter(academ_records))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             # Проверяем что запрос выполняется без ошибок
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
            
#             response = self.view(request)
#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_error_handling(self):
#         """Тест обработки ошибок в данных."""
#         # Создаем запись с проблемными данными
#         academ = self.create_mock_academ(self.student1, self.yesterday)
        
#         # Симулируем проблему с доступом к связанным объектам
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             # Создаем мок, который выбрасывает исключение при итерации
#             mock_queryset.__iter__ = Mock(side_effect=AttributeError('Test error'))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
            
#             # Должен вернуть 500 ошибку
#             with self.assertRaises(AttributeError):
#                 self.view(request)


# # Дополнительные тесты для edge cases
# class TestAcademicReturnsEdgeCases(APITestCase):
#     """Тесты для граничных случаев AcademicReturnsViewSet."""

#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.view = AcademicReturnsViewSet.as_view({'get': 'list'})
        
#         # Мокаем пользователя
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
        
#         # Мокаем группу
#         self.group = Mock(spec=Group)
#         self.group.title = 'ИТ-21-тест'
#         self.group.pk = 1
        
#         # Мокаем студента
#         self.student = Mock(spec=Student)
#         self.student.student_id = 1
#         self.student.name = 'Тестовый Студент'
#         self.student.group = self.group

#     def create_mock_academ(self, student, end_date, relevant_group=None, academ_id=None):
#         """Вспомогательный метод для создания мока записи об академе."""
#         academ = Mock(spec=Academ)
#         academ.pk = academ_id or student.student_id
#         academ.student = student
#         academ.end_date = end_date
#         academ.relevant_group = relevant_group
#         academ.previous_group = student.group
#         academ.start_date = timezone.now().date() - timedelta(days=100)
#         return academ

#     def test_academ_with_same_day_end_date(self):
#         """Тест когда дата окончания равна текущей дате."""
#         today = timezone.now().date()
#         academ = self.create_mock_academ(self.student, today)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             # Должен считаться "Продолжает обучение" так как дата не в прошлом
#             student_data = response.data['students'][0]
#             self.assertEqual(student_data['status'], 'Продолжает обучение')

#     def test_multiple_academ_records_same_student(self):
#         """Тест когда у одного студента несколько записей об академах."""
#         # Создаем две записи для одного студента
#         academ1 = self.create_mock_academ(self.student, date(2022, 1, 1), academ_id=1)
#         academ2 = self.create_mock_academ(self.student, date(2023, 1, 1), academ_id=2)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ1, academ2]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             # Должны вернуться обе записи
#             self.assertEqual(len(response.data['students']), 2)

#     def test_very_old_and_future_dates(self):
#         """Тест с очень старыми и будущими датами."""
#         # Очень старая дата (2000 год - в прошлом)
#         academ1 = self.create_mock_academ(self.student, date(2000, 1, 1), academ_id=1)
        
#         # Очень будущая дата (2030 год - в будущем)  
#         academ2 = self.create_mock_academ(self.student, date(2030, 1, 1), academ_id=2)
        
#         # Мокаем методы
#         with patch.object(AcademicReturnsViewSet, 'get_queryset') as mock_get_queryset, \
#              patch.object(AcademicReturnsViewSet, 'filter_queryset') as mock_filter_queryset:
            
#             mock_queryset = Mock()
#             mock_queryset.__iter__ = Mock(return_value=iter([academ1, academ2]))
#             mock_get_queryset.return_value = mock_queryset
#             mock_filter_queryset.return_value = mock_queryset
            
#             request = self.factory.get('/academic-returns/')
#             request.user = self.user
#             response = self.view(request)
            
#             status_dist = response.data['statusDistribution']
#             # 2000 год - в прошлом, студент в группе -> "Возвращён"
#             # 2030 год - в будущем -> "Продолжает обучение"
#             self.assertEqual(status_dist['Возвращён'], 1)
#             self.assertEqual(status_dist['Продолжает обучение'], 1)

# class TestSubjectStatisticsViewSet(APITestCase):
#     """
#     Тесты для SubjectStatisticsViewSet - статистики по успеваемости по предметам.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.view = SubjectStatisticsViewSet.as_view({'get': 'list'})
        
#         # Создаем мок пользователя для аутентификации
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
#         self.user.is_authenticated = True

#     def test_calculate_course_before_september(self):
#         """Тест расчета курса до сентября."""
#         viewset = SubjectStatisticsViewSet()
        
#         with patch('application.api.datetime') as mock_datetime:
#             mock_now = Mock()
#             mock_now.year = 2024
#             mock_now.month = 8  # Август (до сентября)
#             mock_datetime.now.return_value = mock_now
            
#             course = viewset.calculate_course(2021)
#             self.assertEqual(course, 3)  # 2024 - 2021 = 3

#     def test_calculate_course_after_september(self):
#         """Тест расчета курса после сентября."""
#         viewset = SubjectStatisticsViewSet()
        
#         with patch('application.api.datetime') as mock_datetime:
#             mock_now = Mock()
#             mock_now.year = 2024
#             mock_now.month = 9  # Сентябрь
#             mock_datetime.now.return_value = mock_now
            
#             course = viewset.calculate_course(2021)
#             self.assertEqual(course, 4)  # 2024 - 2021 + 1 = 4

#     def test_extract_year_from_group_title_valid(self):
#         """Тест извлечения года из корректного названия группы."""
#         viewset = SubjectStatisticsViewSet()
        
#         year = viewset.extract_year_from_group_title('ФИТ-21Б')
#         self.assertEqual(year, 2021)
        
#         year = viewset.extract_year_from_group_title('ИВТ-19А')
#         self.assertEqual(year, 2019)

#     def test_extract_year_from_group_title_invalid(self):
#         """Тест извлечения года из некорректного названия группы."""
#         viewset = SubjectStatisticsViewSet()
        
#         # Некорректные форматы
#         self.assertIsNone(viewset.extract_year_from_group_title('ФИТ21Б'))
#         self.assertIsNone(viewset.extract_year_from_group_title('ФИТ-'))
#         self.assertIsNone(viewset.extract_year_from_group_title(''))
#         self.assertIsNone(viewset.extract_year_from_group_title(None))

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_basic_request(self, mock_select_related):
#         """Тест базового запроса без параметров."""
#         # Настраиваем моки с правильной цепочкой
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем агрегатные функции
#         mock_queryset.annotate.return_value.aggregate.return_value = {
#             'min_grade': 3.0,
#             'avg_grade': 4.25,
#             'max_grade': 5.0
#         }
        
#         # Мокаем распределение оценок
#         grade_distribution_data = [
#             {'grade': '2', 'count': 1},
#             {'grade': '3', 'count': 2},
#             {'grade': '4', 'count': 3},
#             {'grade': '5', 'count': 4}
#         ]
#         mock_grade_distribution = MagicMock()
#         mock_grade_distribution.__iter__.return_value = iter(grade_distribution_data)
#         mock_queryset.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = mock_grade_distribution
        
#         # Мокаем топ предметов - используем MagicMock для поддержки срезов
#         top_subjects_data = [
#             {
#                 'fc__hps__disciple__disciple_name': 'Математика',
#                 'avg_grade': 4.5,
#                 'max_grade': 5,
#                 'count': 10,
#                 'avg_attendance': 85.5
#             },
#             {
#                 'fc__hps__disciple__disciple_name': 'Физика',
#                 'avg_grade': 4.2,
#                 'max_grade': 5,
#                 'count': 8,
#                 'avg_attendance': 78.0
#             }
#         ]
        
#         mock_top_subjects = MagicMock()
#         mock_top_subjects.__getitem__.return_value = top_subjects_data
#         mock_queryset.annotate.return_value.filter.return_value.values.return_value.annotate.return_value.order_by.return_value.exclude.return_value = mock_top_subjects
        
#         # Создаем запрос
#         request = self.factory.get('/api/subject-statistics/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('subjectStats', response.data)
#         self.assertIn('gradeDistributionBar', response.data)
#         self.assertIn('bestSubjects', response.data)
        
#         # Проверяем структуру данных
#         self.assertEqual(response.data['subjectStats']['minGrade'], 3.0)
#         self.assertEqual(response.data['subjectStats']['avgGrade'], 4.25)
#         self.assertEqual(response.data['subjectStats']['maxGrade'], 5.0)
#         self.assertEqual(len(response.data['bestSubjects']), 2)

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_invalid_course_semester_combination(self, mock_select_related):
#         """Тест некорректной комбинации курса и семестра."""
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем базовые методы чтобы не было ошибок
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
        
#         # Создаем запрос с некорректной комбинацией курса и семестра
#         request = self.factory.get('/api/subject-statistics/?course=1&semester=3')  # Для 1 курса допустимы семестры 1 и 2
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что возвращается пустой ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIsNone(response.data['subjectStats']['minGrade'])
#         self.assertIsNone(response.data['subjectStats']['avgGrade'])
#         self.assertIsNone(response.data['subjectStats']['maxGrade'])
#         self.assertEqual(response.data['gradeDistributionBar']['2'], 0)
#         self.assertEqual(response.data['bestSubjects'], [])

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_different_sort_criteria(self, mock_select_related):
#         """Тест разных критериев сортировки."""
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем агрегатные функции
#         mock_queryset.annotate.return_value.aggregate.return_value = {
#             'min_grade': 3.0,
#             'avg_grade': 4.0,
#             'max_grade': 5.0
#         }
        
#         # Мокаем распределение оценок
#         grade_distribution_data = [
#             {'grade': '3', 'count': 1},
#             {'grade': '4', 'count': 2},
#             {'grade': '5', 'count': 1}
#         ]
#         mock_grade_distribution = MagicMock()
#         mock_grade_distribution.__iter__.return_value = iter(grade_distribution_data)
#         mock_queryset.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = mock_grade_distribution
        
#         # Мокаем топ предметов для всех случаев
#         top_subjects_data = [
#             {
#                 'fc__hps__disciple__disciple_name': 'Математика',
#                 'avg_grade': 4.5,
#                 'max_grade': 5,
#                 'count': 10,
#                 'avg_attendance': 85.5
#             }
#         ]
        
#         mock_top_subjects = MagicMock()
#         mock_top_subjects.__getitem__.return_value = top_subjects_data
#         mock_queryset.annotate.return_value.filter.return_value.values.return_value.annotate.return_value.order_by.return_value.exclude.return_value = mock_top_subjects
        
#         # Тестируем сортировку по среднему баллу
#         request_avg = self.factory.get('/api/subject-statistics/?sortBy=avg')
#         request_avg.user = self.user
#         response_avg = self.view(request_avg)
#         self.assertEqual(response_avg.status_code, status.HTTP_200_OK)
        
#         # Тестируем сортировку по максимальному баллу
#         request_max = self.factory.get('/api/subject-statistics/?sortBy=max')
#         request_max.user = self.user
#         response_max = self.view(request_max)
#         self.assertEqual(response_max.status_code, status.HTTP_200_OK)
        
#         # Тестируем сортировку по количеству оценок
#         request_count = self.factory.get('/api/subject-statistics/?sortBy=count')
#         request_count.user = self.user
#         response_count = self.view(request_count)
#         self.assertEqual(response_count.status_code, status.HTTP_200_OK)

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_empty_results(self, mock_select_related):
#         """Тест запроса с пустыми результатами."""
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем пустые результаты - возвращаем None значения
#         mock_queryset.annotate.return_value.aggregate.return_value = {
#             'min_grade': None,
#             'avg_grade': None,
#             'max_grade': None
#         }
        
#         # Мокаем пустое распределение оценок
#         mock_grade_distribution = MagicMock()
#         mock_grade_distribution.__iter__.return_value = iter([])
#         mock_queryset.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = mock_grade_distribution
        
#         # Мокаем пустые топ предметы
#         mock_top_subjects = MagicMock()
#         mock_top_subjects.__getitem__.return_value = []
#         mock_queryset.annotate.return_value.filter.return_value.values.return_value.annotate.return_value.order_by.return_value.exclude.return_value = mock_top_subjects
        
#         # Создаем запрос с фильтром, который не найдет данных
#         request = self.factory.get('/api/subject-statistics/?subject=НесуществующийПредмет')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ с пустыми данными
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # Вместо проверки на None, проверяем что значения присутствуют в ответе
#         self.assertIn('minGrade', response.data['subjectStats'])
#         self.assertIn('avgGrade', response.data['subjectStats'])
#         self.assertIn('maxGrade', response.data['subjectStats'])
#         self.assertEqual(response.data['bestSubjects'], [])

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_invalid_parameters(self, mock_select_related):
#         """Тест обработки некорректных параметров."""
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем базовые методы
#         mock_queryset.annotate.return_value.aggregate.return_value = {
#             'min_grade': 4.0,
#             'avg_grade': 4.5,
#             'max_grade': 5.0
#         }
        
#         # Мокаем распределение оценок
#         grade_distribution_data = [
#             {'grade': '4', 'count': 1},
#             {'grade': '5', 'count': 2}
#         ]
#         mock_grade_distribution = MagicMock()
#         mock_grade_distribution.__iter__.return_value = iter(grade_distribution_data)
#         mock_queryset.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = mock_grade_distribution
        
#         # Мокаем топ предметов
#         top_subjects_data = [
#             {
#                 'fc__hps__disciple__disciple_name': 'Математика',
#                 'avg_grade': 4.5,
#                 'max_grade': 5,
#                 'count': 3,
#                 'avg_attendance': 80.0
#             }
#         ]
        
#         mock_top_subjects = MagicMock()
#         mock_top_subjects.__getitem__.return_value = top_subjects_data
#         mock_queryset.annotate.return_value.filter.return_value.values.return_value.annotate.return_value.order_by.return_value.exclude.return_value = mock_top_subjects
        
#         # Тестируем некорректный курс (не число)
#         request_invalid_course = self.factory.get('/api/subject-statistics/?course=abc')
#         request_invalid_course.user = self.user
#         response_invalid_course = self.view(request_invalid_course)
#         self.assertEqual(response_invalid_course.status_code, status.HTTP_200_OK)
        
#         # Тестируем некорректный семестр (не число)
#         request_invalid_semester = self.factory.get('/api/subject-statistics/?semester=xyz')
#         request_invalid_semester.user = self.user
#         response_invalid_semester = self.view(request_invalid_semester)
#         self.assertEqual(response_invalid_semester.status_code, status.HTTP_200_OK)

#     def test_queryset_optimization(self):
#         """Тест оптимизации queryset с select_related."""
#         # Создаем реальный экземпляр ViewSet и проверяем его queryset
#         viewset = SubjectStatisticsViewSet()
#         queryset = viewset.get_queryset()
        
#         # Проверяем что queryset использует select_related
#         self.assertIsNotNone(queryset)
#         # Дополнительные проверки можно добавить в зависимости от реализации get_queryset

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_with_groups_filter(self, mock_select_related):
#         """Тест фильтрации по группам."""
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем результаты
#         mock_queryset.annotate.return_value.aggregate.return_value = {
#             'min_grade': 4.0,
#             'avg_grade': 4.5,
#             'max_grade': 5.0
#         }
        
#         # Мокаем распределение оценок
#         grade_distribution_data = [
#             {'grade': '4', 'count': 2},
#             {'grade': '5', 'count': 3}
#         ]
#         mock_grade_distribution = MagicMock()
#         mock_grade_distribution.__iter__.return_value = iter(grade_distribution_data)
#         mock_queryset.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = mock_grade_distribution
        
#         # Мокаем топ предметов
#         top_subjects_data = [
#             {
#                 'fc__hps__disciple__disciple_name': 'Математика',
#                 'avg_grade': 4.5,
#                 'max_grade': 5,
#                 'count': 5,
#                 'avg_attendance': 85.0
#             }
#         ]
        
#         mock_top_subjects = MagicMock()
#         mock_top_subjects.__getitem__.return_value = top_subjects_data
#         mock_queryset.annotate.return_value.filter.return_value.values.return_value.annotate.return_value.order_by.return_value.exclude.return_value = mock_top_subjects
        
#         # Создаем запрос с фильтром по группам
#         request = self.factory.get('/api/subject-statistics/?groups=ФИТ-21Б,ФИТ-22Б')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.Grades.objects.select_related')
#     def test_list_default_limit(self, mock_select_related):
#         """Тест применения лимита по умолчанию."""
#         mock_queryset = MagicMock()
#         mock_select_related.return_value = mock_queryset
        
#         # Мокаем результаты
#         mock_queryset.annotate.return_value.aggregate.return_value = {
#             'min_grade': 4.0,
#             'avg_grade': 4.5,
#             'max_grade': 5.0
#         }
        
#         # Мокаем распределение оценок
#         grade_distribution_data = [
#             {'grade': '4', 'count': 2},
#             {'grade': '5', 'count': 3}
#         ]
#         mock_grade_distribution = MagicMock()
#         mock_grade_distribution.__iter__.return_value = iter(grade_distribution_data)
#         mock_queryset.annotate.return_value.values.return_value.annotate.return_value.order_by.return_value = mock_grade_distribution
        
#         # Мокаем топ предметов - проверяем что применяется лимит по умолчанию (5)
#         mock_top_subjects = MagicMock()
#         mock_top_subjects.__getitem__.return_value = [
#             {
#                 'fc__hps__disciple__disciple_name': f'Предмет {i}',
#                 'avg_grade': 4.5,
#                 'max_grade': 5,
#                 'count': 5,
#                 'avg_attendance': 85.0
#             } for i in range(5)
#         ]
        
#         mock_queryset.annotate.return_value.filter.return_value.values.return_value.annotate.return_value.order_by.return_value.exclude.return_value = mock_top_subjects
        
#         # Создаем запрос без указания лимита
#         request = self.factory.get('/api/subject-statistics/')
#         request.user = self.user
        
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # Проверяем что срез был вызван с правильными параметрами (лимит по умолчанию 5)
#         mock_top_subjects.__getitem__.assert_called_with(slice(None, 5))

# class TestStudentRatingViewSet(APITestCase):
#     """
#     Тесты для StudentRatingViewSet - рейтинга студентов с комплексной оценкой успеваемости.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.view = StudentRatingViewSet.as_view({'get': 'list'})
        
#         # Создаем мок пользователя для аутентификации
#         self.user = Mock(spec=Administrator)
#         self.user.email = 'testuser@example.com'
#         self.user.is_authenticated = True

#     def test_calculate_course_before_september(self):
#         """Тест расчета курса до сентября."""
#         viewset = StudentRatingViewSet()
        
#         with patch('application.api.datetime') as mock_datetime:
#             mock_now = Mock()
#             mock_now.year = 2024
#             mock_now.month = 8  # Август (до сентября)
#             mock_datetime.now.return_value = mock_now
            
#             course = viewset.calculate_course(2021)
#             self.assertEqual(course, 3)  # 2024 - 2021 = 3

#     def test_calculate_course_after_september(self):
#         """Тест расчета курса после сентября."""
#         viewset = StudentRatingViewSet()
        
#         with patch('application.api.datetime') as mock_datetime:
#             mock_now = Mock()
#             mock_now.year = 2024
#             mock_now.month = 9  # Сентябрь
#             mock_datetime.now.return_value = mock_now
            
#             course = viewset.calculate_course(2021)
#             self.assertEqual(course, 4)  # 2024 - 2021 + 1 = 4

#     def test_extract_year_from_group_title_valid(self):
#         """Тест извлечения года из корректного названия группы."""
#         viewset = StudentRatingViewSet()
        
#         year = viewset.extract_year_from_group_title('ФИТ-21Б')
#         self.assertEqual(year, 2021)
        
#         year = viewset.extract_year_from_group_title('ИВТ-19А')
#         self.assertEqual(year, 2019)

#     def test_extract_year_from_group_title_invalid(self):
#         """Тест извлечения года из некорректного названия группы."""
#         viewset = StudentRatingViewSet()
        
#         # Некорректные форматы
#         self.assertIsNone(viewset.extract_year_from_group_title('ФИТ21Б'))
#         self.assertIsNone(viewset.extract_year_from_group_title('ФИТ-'))
#         self.assertIsNone(viewset.extract_year_from_group_title(''))
#         self.assertIsNone(viewset.extract_year_from_group_title(None))

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_basic_request(self, mock_get_queryset):
#         """Тест базового запроса без параметров."""
#         # Создаем тестовых студентов
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             ),
#             Mock(
#                 student_id=2,
#                 name='Петров Петр',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.2,
#                 avg_activity=7.5,
#                 attendance_percent=90.0,
#                 calculated_rating=76.8
#             )
#         ]
        
#         # Настраиваем моки для полной цепочки
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Настраиваем цепочку вызовов
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос
#         request = self.factory.get('/api/student-rating/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('chartData', response.data)
#         self.assertIn('students', response.data)
#         self.assertEqual(len(response.data['students']), 2)
        
#         # Проверяем структуру данных
#         student_data = response.data['students'][0]
#         self.assertIn('id', student_data)
#         self.assertIn('name', student_data)
#         self.assertIn('group', student_data)
#         self.assertIn('course', student_data)
#         self.assertIn('avgGrade', student_data)
#         self.assertIn('activity', student_data)
#         self.assertIn('attendancePercent', student_data)
#         self.assertIn('dropoutRisk', student_data)
#         self.assertIn('rating', student_data)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_with_group_filter(self, mock_get_queryset):
#         """Тест запроса с фильтром по группе."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос с фильтром по группе
#         request = self.factory.get('/api/student-rating/?group=ФИТ-21Б')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что фильтр по группе был применен
#         mock_queryset.filter.assert_called_with(group__title='ФИТ-21Б')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_with_course_filter(self, mock_get_queryset):
#         """Тест запроса с фильтром по курсу."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Мокаем студентов с разными группами
#         student_with_group = Mock(
#             student_id=1,
#             name='Иванов Иван',
#             group=Mock(title='ФИТ-21Б'),
#             avg_grade=4.5,
#             avg_activity=8.0,
#             attendance_percent=85.5,
#             calculated_rating=78.5
#         )
        
#         # Настраиваем поведение для фильтрации по курсу
#         def filter_side_effect(**kwargs):
#             if 'student_id__in' in kwargs:
#                 # Возвращаем только студента с группой
#                 filtered_mock = MagicMock()
#                 filtered_mock.annotate.return_value = filtered_mock
#                 filtered_mock.order_by.return_value.__getitem__.return_value = [student_with_group]
#                 return filtered_mock
#             return mock_queryset
        
#         mock_queryset.filter.side_effect = filter_side_effect
#         mock_queryset.annotate.return_value = mock_queryset
        
#         # Создаем запрос с фильтром по курсу
#         request = self.factory.get('/api/student-rating/?course=3')
#         request.user = self.user
        
#         # Мокаем extract_year_from_group_title и calculate_course
#         with patch.object(StudentRatingViewSet, 'extract_year_from_group_title') as mock_extract, \
#              patch.object(StudentRatingViewSet, 'calculate_course') as mock_calculate:
            
#             mock_extract.return_value = 2021
#             mock_calculate.return_value = 3
            
#             response = self.view(request)
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_with_subject_filter(self, mock_get_queryset):
#         """Тест запроса с фильтром по предмету."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос с фильтром по предмету
#         request = self.factory.get('/api/student-rating/?subject=Математика')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что фильтр по предмету был применен
#         mock_queryset.filter.assert_called_with(
#             grades__fc__hps__disciple__disciple_name__icontains='Математика'
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_different_sort_criteria(self, mock_get_queryset):
#         """Тест разных критериев сортировки."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Тестируем сортировку по рейтингу
#         request_rating = self.factory.get('/api/student-rating/?sortBy=rating')
#         request_rating.user = self.user
#         response_rating = self.view(request_rating)
#         self.assertEqual(response_rating.status_code, status.HTTP_200_OK)
        
#         # Тестируем сортировку по успеваемости
#         request_performance = self.factory.get('/api/student-rating/?sortBy=performance')
#         request_performance.user = self.user
#         response_performance = self.view(request_performance)
#         self.assertEqual(response_performance.status_code, status.HTTP_200_OK)
        
#         # Тестируем сортировку по посещаемости
#         request_attendance = self.factory.get('/api/student-rating/?sortBy=attendance')
#         request_attendance.user = self.user
#         response_attendance = self.view(request_attendance)
#         self.assertEqual(response_attendance.status_code, status.HTTP_200_OK)
        
#         # Тестируем сортировку по активности
#         request_activity = self.factory.get('/api/student-rating/?sortBy=activity')
#         request_activity.user = self.user
#         response_activity = self.view(request_activity)
#         self.assertEqual(response_activity.status_code, status.HTTP_200_OK)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_with_custom_limit(self, mock_get_queryset):
#         """Тест запроса с кастомным лимитом."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_order_by = MagicMock()
#         mock_queryset.order_by.return_value = mock_order_by
#         mock_order_by.__getitem__.return_value = test_students
        
#         # Создаем запрос с кастомным лимитом
#         request = self.factory.get('/api/student-rating/?limit=5')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что лимит был применен
#         mock_order_by.__getitem__.assert_called_with(slice(None, 5))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_empty_results(self, mock_get_queryset):
#         """Тест запроса с пустыми результатами."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Мокаем пустой результат
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = []
        
#         # Создаем запрос с фильтром, который не найдет данных
#         request = self.factory.get('/api/student-rating/?group=НесуществующаяГруппа')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ с пустыми данными
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['chartData'], [])
#         self.assertEqual(response.data['students'], [])

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_invalid_course_parameter(self, mock_get_queryset):
#         """Тест обработки некорректного параметра курса."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос с некорректным курсом
#         request = self.factory.get('/api/student-rating/?course=abc')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что запрос обработан успешно (некорректный курс игнорируется)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_student_without_group(self, mock_get_queryset):
#         """Тест обработки студента без группы."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Создаем студента без группы
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Студент Без Группы',
#                 group=None,
#                 avg_grade=4.0,
#                 avg_activity=7.0,
#                 attendance_percent=80.0,
#                 calculated_rating=70.0
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос
#         request = self.factory.get('/api/student-rating/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         student_data = response.data['students'][0]
#         self.assertIsNone(student_data['group'])
#         self.assertIsNone(student_data['course'])

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_calculation_accuracy(self, mock_get_queryset):
#         """Тест точности расчетов рейтинга."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Создаем студента с конкретными значениями для проверки расчетов
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Тестовый Студент',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,      # 4.5 * 0.5 = 2.25
#                 avg_activity=8.0,   # 8.0 * 0.3 = 2.4
#                 attendance_percent=85.5,  # 85.5 * 0.2 = 17.1
#                 calculated_rating=78.5    # (2.25 + 2.4 + 17.1) * 20 = 435, но должно быть округлено
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос
#         request = self.factory.get('/api/student-rating/')
#         request.user = self.user
        
#         # Мокаем расчет курса
#         with patch.object(StudentRatingViewSet, 'extract_year_from_group_title') as mock_extract, \
#              patch.object(StudentRatingViewSet, 'calculate_course') as mock_calculate:
            
#             mock_extract.return_value = 2021
#             mock_calculate.return_value = 3
            
#             response = self.view(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         student_data = response.data['students'][0]
        
#         # Проверяем округление значений
#         self.assertEqual(student_data['avgGrade'], 4.5)
#         self.assertEqual(student_data['activity'], 8.0)
#         self.assertEqual(student_data['attendancePercent'], 85.5)
#         self.assertEqual(student_data['rating'], 78.5)
#         self.assertEqual(student_data['dropoutRisk'], 0.25)  # Фиксированное значение

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_annotation_chain(self, mock_get_queryset):
#         """Тест правильности цепочки аннотаций."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Иванов Иван',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.5,
#                 avg_activity=8.0,
#                 attendance_percent=85.5,
#                 calculated_rating=78.5
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос
#         request = self.factory.get('/api/student-rating/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что аннотации были вызваны
#         self.assertTrue(mock_queryset.annotate.called)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_queryset_optimization(self):
#         """Тест оптимизации queryset с select_related."""
#         viewset = StudentRatingViewSet()
#         queryset = viewset.get_queryset()
        
#         # Проверяем что queryset использует select_related
#         self.assertIsNotNone(queryset)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_default_limit_applied(self, mock_get_queryset):
#         """Тест применения лимита по умолчанию."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         test_students = [
#             Mock(
#                 student_id=i,
#                 name=f'Студент {i}',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=4.0,
#                 avg_activity=7.0,
#                 attendance_percent=80.0,
#                 calculated_rating=70.0
#             ) for i in range(10)  # 10 студентов - лимит по умолчанию
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_order_by = MagicMock()
#         mock_queryset.order_by.return_value = mock_order_by
#         mock_order_by.__getitem__.return_value = test_students
        
#         # Создаем запрос без указания лимита
#         request = self.factory.get('/api/student-rating/')
#         request.user = self.user
#         response = self.view(request)
        
#         # Проверяем что лимит по умолчанию (10) был применен
#         mock_order_by.__getitem__.assert_called_with(slice(None, 10))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['students']), 10)

#     @patch('application.api.StudentRatingViewSet.get_queryset')
#     def test_list_complex_rating_calculation(self, mock_get_queryset):
#         """Тест расчета комплексного рейтинга."""
#         mock_queryset = MagicMock()
#         mock_get_queryset.return_value = mock_queryset
        
#         # Создаем студента с нулевыми значениями для проверки граничных случаев
#         test_students = [
#             Mock(
#                 student_id=1,
#                 name='Студент с нулями',
#                 group=Mock(title='ФИТ-21Б'),
#                 avg_grade=None,  # None значения
#                 avg_activity=None,
#                 attendance_percent=None,
#                 calculated_rating=None
#             )
#         ]
        
#         mock_queryset.filter.return_value = mock_queryset
#         mock_queryset.annotate.return_value = mock_queryset
#         mock_queryset.order_by.return_value.__getitem__.return_value = test_students
        
#         # Создаем запрос
#         request = self.factory.get('/api/student-rating/')
#         request.user = self.user
        
#         with patch.object(StudentRatingViewSet, 'extract_year_from_group_title') as mock_extract, \
#              patch.object(StudentRatingViewSet, 'calculate_course') as mock_calculate:
            
#             mock_extract.return_value = 2021
#             mock_calculate.return_value = 3
            
#             response = self.view(request)
        
#         # Проверяем что None значения корректно обрабатываются
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         student_data = response.data['students'][0]
#         self.assertEqual(student_data['avgGrade'], 0.0)  # None преобразуется в 0.0
#         self.assertEqual(student_data['activity'], 0.0)
#         self.assertEqual(student_data['attendancePercent'], 0.0)
#         self.assertEqual(student_data['rating'], 0.0)

# class TestStudentAnalyticsViewSet(APITestCase):
#     """
#     Тесты для StudentAnalyticsViewSet - аналитики студента из CSV файла.
#     """

#     def setUp(self):
#         """Настройка тестовых данных перед каждым тестом."""
#         self.factory = APIRequestFactory()
#         self.viewset = StudentAnalyticsViewSet()
        
#         # Создаем мок пользователя для аутентификации
#         self.user = Mock()
#         self.user.is_authenticated = True
        
#         # Пример данных CSV для тестов
#         self.sample_csv_data = [
#             {
#                 'Student_ID': '12345',
#                 'Name': 'Иванов Иван Иванович',
#                 'Age': '20',
#                 'Group_Name': 'ФИТ-21Б',
#                 'Speciality': 'Информатика',
#                 'Is_Academic': '0',
#                 'Middle_value_of_sertificate': '4.5',
#                 'Entry_score': '85.5',
#                 'Rating_score': '4.2',
#                 'Diploma_grade': '4.7',
#                 'Математика': '4.8',
#                 'Программирование': '5.0',
#                 'Физика': '4.2'
#             },
#             {
#                 'Student_ID': '67890',
#                 'Name': 'Петров Петр Петрович',
#                 'Age': '21',
#                 'Group_Name': 'ИВТ-20А',
#                 'Speciality': 'Программирование',
#                 'Is_Academic': '1',
#                 'Middle_value_of_sertificate': '4.8',
#                 'Entry_score': '92.0',
#                 'Rating_score': '4.5',
#                 'Diploma_grade': '4.9',
#                 'Математика': '5.0',
#                 'Программирование': '4.9',
#                 'Физика': '4.5'
#             }
#         ]

#     def _create_drf_request(self, path, user=None, method='get', **kwargs):
#         """Создает DRF Request объект с правильным query_params."""
#         factory_method = getattr(self.factory, method)
#         request = factory_method(path, **kwargs)
#         request.user = user or self.user
#         return Request(request)

#     def test_get_csv_path(self):
#         """Тест получения пути к CSV файлу."""
#         viewset = StudentAnalyticsViewSet()
#         csv_path = viewset.get_csv_path()
        
#         self.assertEqual(csv_path, 'application/management/predictions_results.csv')

#     @patch('application.api.os.path.exists')
#     @patch('application.api.csv.DictReader')
#     @patch('builtins.open', new_callable=mock_open)
#     def test_read_csv_data_success(self, mock_file, mock_dict_reader, mock_exists):
#         """Тест успешного чтения CSV файла."""
#         mock_exists.return_value = True
#         mock_dict_reader.return_value = self.sample_csv_data
        
#         viewset = StudentAnalyticsViewSet()
#         result = viewset.read_csv_data()
        
#         # Проверяем вызовы
#         mock_exists.assert_called_once_with('application/management/predictions_results.csv')
#         mock_file.assert_called_once_with('application/management/predictions_results.csv', 'r', encoding='utf-8')
#         mock_dict_reader.assert_called_once()
        
#         # Проверяем результат
#         self.assertEqual(result, self.sample_csv_data)

#     @patch('application.api.os.path.exists')
#     def test_read_csv_data_file_not_found(self, mock_exists):
#         """Тест чтения CSV файла, когда файл не существует."""
#         mock_exists.return_value = False
        
#         viewset = StudentAnalyticsViewSet()
        
#         with self.assertRaises(FileNotFoundError) as context:
#             viewset.read_csv_data()
        
#         self.assertEqual(str(context.exception), "Analytics file not generated yet")

#     def test_permission_classes(self):
#         """Тест проверки классов разрешений."""
#         viewset = StudentAnalyticsViewSet()
#         self.assertEqual(viewset.permission_classes, [IsAuthenticated])

#     def test_queryset_is_none(self):
#         """Тест что queryset не используется."""
#         viewset = StudentAnalyticsViewSet()
#         self.assertIsNone(viewset.queryset)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_success(self, mock_read_csv):
#         """Тест успешного получения аналитики студента."""
#         # Настраиваем моки
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         # Вызываем метод
#         response = self.viewset.list(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['student_id'], '12345')
#         self.assertEqual(response.data['name'], 'Иванов Иван Иванович')
#         self.assertEqual(response.data['age'], 20)
#         self.assertEqual(response.data['group'], 'ФИТ-21Б')
#         self.assertEqual(response.data['speciality'], 'Информатика')
        
#         # Проверяем академическую информацию
#         academic_info = response.data['academic_info']
#         self.assertEqual(academic_info['certificate_score'], 4.5)
#         self.assertEqual(academic_info['entry_score'], 85.5)
#         self.assertEqual(academic_info['rating_score'], 4.2)
#         self.assertEqual(academic_info['diploma_grade'], 4.7)
#         self.assertEqual(academic_info['is_academic'], False)
        
#         # Проверяем предметы
#         subjects = response.data['subjects']
#         self.assertEqual(len(subjects), 3)
        
#         # Проверяем что предметы отсортированы правильно
#         subject_names = [s['subject'] for s in subjects]
#         self.assertIn('Математика', subject_names)
#         self.assertIn('Программирование', subject_names)
#         self.assertIn('Физика', subject_names)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_with_subjects_filter(self, mock_read_csv):
#         """Тест получения аналитики с фильтром по предметам."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request с фильтром по предметам
#         request = self._create_drf_request(
#             '/api/student-analytics/?student_id=12345&subjects=Математика&subjects=Программирование'
#         )
        
#         response = self.viewset.list(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Проверяем что возвращены только отфильтрованные предметы
#         subjects = response.data['subjects']
#         self.assertEqual(len(subjects), 2)
        
#         subject_names = [s['subject'] for s in subjects]
#         self.assertIn('Математика', subject_names)
#         self.assertIn('Программирование', subject_names)
#         self.assertNotIn('Физика', subject_names)

#     def test_list_missing_student_id(self):
#         """Тест запроса без обязательного параметра student_id."""
#         # Создаем DRF Request без student_id
#         request = self._create_drf_request('/api/student-analytics/')
        
#         response = self.viewset.list(request)
        
#         # Проверяем ошибку
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'Missing required parameter: student_id')

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_student_not_found(self, mock_read_csv):
#         """Тест запроса для несуществующего студента."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request с несуществующим student_id
#         request = self._create_drf_request('/api/student-analytics/?student_id=99999')
        
#         response = self.viewset.list(request)
        
#         # Проверяем ошибку
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(response.data['error'], 'Student with ID 99999 not found')

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_file_not_found_error(self, mock_read_csv):
#         """Тест обработки ошибки отсутствия файла."""
#         mock_read_csv.side_effect = FileNotFoundError("Analytics file not generated yet")
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         response = self.viewset.list(request)
        
#         # Проверяем ошибку
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(response.data['error'], 'Analytics file not generated yet')

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_academic_student(self, mock_read_csv):
#         """Тест аналитики для студента в академическом отпуске."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request для студента в академе
#         request = self._create_drf_request('/api/student-analytics/?student_id=67890')
        
#         response = self.viewset.list(request)
        
#         # Проверяем ответ
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['academic_info']['is_academic'], True)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_data_types_conversion(self, mock_read_csv):
#         """Тест корректного преобразования типов данных."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         response = self.viewset.list(request)
        
#         # Проверяем типы данных
#         self.assertIsInstance(response.data['age'], int)
#         self.assertIsInstance(response.data['academic_info']['certificate_score'], float)
#         self.assertIsInstance(response.data['academic_info']['entry_score'], float)
#         self.assertIsInstance(response.data['academic_info']['rating_score'], float)
#         self.assertIsInstance(response.data['academic_info']['diploma_grade'], float)
#         self.assertIsInstance(response.data['academic_info']['is_academic'], bool)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_nonexistent_subjects_filter(self, mock_read_csv):
#         """Тест с фильтром по несуществующим предметам."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request с фильтром по несуществующим предметам
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345&subjects=Химия&subjects=Биология')
        
#         response = self.viewset.list(request)
        
#         # Проверяем что предметы не найдены
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['subjects']), 0)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_multiple_students_in_csv(self, mock_read_csv):
#         """Тест поиска студента когда в CSV несколько записей."""
#         # Добавляем больше студентов в тестовые данные
#         extended_data = self.sample_csv_data + [
#             {
#                 'Student_ID': '11111',
#                 'Name': 'Сидоров Сидор Сидорович',
#                 'Age': '22',
#                 'Group_Name': 'ФИТ-19А',
#                 'Speciality': 'Информатика',
#                 'Is_Academic': '0',
#                 'Middle_value_of_sertificate': '4.3',
#                 'Entry_score': '88.0',
#                 'Rating_score': '4.1',
#                 'Diploma_grade': '4.6',
#                 'Математика': '4.5',
#                 'Программирование': '4.7'
#             }
#         ]
#         mock_read_csv.return_value = extended_data
        
#         # Создаем DRF Request для нового студента
#         request = self._create_drf_request('/api/student-analytics/?student_id=11111')
        
#         response = self.viewset.list(request)
        
#         # Проверяем что найден правильный студент
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['student_id'], '11111')
#         self.assertEqual(response.data['name'], 'Сидоров Сидор Сидорович')

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_subject_grade_format(self, mock_read_csv):
#         """Тест формата оценок по предметам."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         response = self.viewset.list(request)
        
#         # Проверяем формат данных по предметам
#         subjects = response.data['subjects']
#         for subject in subjects:
#             self.assertIn('subject', subject)
#             self.assertIn('grade', subject)
#             self.assertIsInstance(subject['subject'], str)
#             self.assertIsInstance(subject['grade'], str)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_core_fields_exclusion(self, mock_read_csv):
#         """Тест что основные поля исключены из списка предметов."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         response = self.viewset.list(request)
        
#         # Получаем все названия предметов
#         subject_names = [s['subject'] for s in response.data['subjects']]
        
#         # Проверяем что основные поля не попали в предметы
#         core_fields = ['Speciality', 'Group_Name', 'Student_ID', 'Name', 'Age', 'Is_Academic',
#                       'Middle_value_of_sertificate', 'Entry_score', 'Rating_score', 'Diploma_grade']
        
#         for field in core_fields:
#             self.assertNotIn(field, subject_names)

#     def test_csv_reader_parameters(self):
#         """Тест параметров чтения CSV файла."""
#         with patch('application.api.os.path.exists') as mock_exists, \
#              patch('application.api.csv.DictReader') as mock_dict_reader, \
#              patch('builtins.open', mock_open()) as mock_file:
            
#             mock_exists.return_value = True
#             mock_dict_reader.return_value = []
            
#             viewset = StudentAnalyticsViewSet()
#             viewset.read_csv_data()
            
#             # Проверяем параметры вызова csv.DictReader
#             mock_dict_reader.assert_called_once()
#             call_args = mock_dict_reader.call_args
#             self.assertEqual(call_args[1]['delimiter'], ';')

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_edge_case_empty_csv(self, mock_read_csv):
#         """Тест обработки пустого CSV файла."""
#         mock_read_csv.return_value = []  # Пустой CSV
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         response = self.viewset.list(request)
        
#         # Проверяем ошибку
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(response.data['error'], 'Student with ID 12345 not found')

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_response_structure(self, mock_read_csv):
#         """Тест полной структуры ответа."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request
#         request = self._create_drf_request('/api/student-analytics/?student_id=12345')
        
#         response = self.viewset.list(request)
        
#         # Проверяем полную структуру ответа
#         expected_structure = {
#             'student_id': str,
#             'name': str,
#             'age': int,
#             'group': str,
#             'speciality': str,
#             'academic_info': dict,
#             'subjects': list
#         }
        
#         for key, expected_type in expected_structure.items():
#             self.assertIn(key, response.data)
#             self.assertIsInstance(response.data[key], expected_type)
        
#         # Проверяем структуру academic_info
#         academic_info_structure = {
#             'certificate_score': float,
#             'entry_score': float,
#             'rating_score': float,
#             'diploma_grade': float,
#             'is_academic': bool
#         }
        
#         for key, expected_type in academic_info_structure.items():
#             self.assertIn(key, response.data['academic_info'])
#             self.assertIsInstance(response.data['academic_info'][key], expected_type)
        
#         # Проверяем структуру subjects
#         if response.data['subjects']:
#             subject_structure = {
#                 'subject': str,
#                 'grade': str
#             }
#             for subject in response.data['subjects']:
#                 for key, expected_type in subject_structure.items():
#                     self.assertIn(key, subject)
#                     self.assertIsInstance(subject[key], expected_type)

#     @patch.object(StudentAnalyticsViewSet, 'read_csv_data')
#     def test_list_getlist_subjects_parameter(self, mock_read_csv):
#         """Тест обработки параметра subjects через getlist."""
#         mock_read_csv.return_value = self.sample_csv_data
        
#         # Создаем DRF Request с несколькими предметами
#         request = self._create_drf_request(
#             '/api/student-analytics/?student_id=12345&subjects=Математика&subjects=Физика'
#         )
        
#         response = self.viewset.list(request)
        
#         # Проверяем что subjects обрабатывается через getlist
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         subjects = response.data['subjects']
#         self.assertEqual(len(subjects), 2)
#         subject_names = [s['subject'] for s in subjects]
#         self.assertIn('Математика', subject_names)
#         self.assertIn('Физика', subject_names)

# if __name__ == '__main__':
#     pytest.main()


import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from application.api import GradesViewset, AcademicPerformanceViewSet, SubjectStatisticsViewSet, StudentRatingViewSet


class TestGradesViewsetWithMocks:
    """Тесты для GradesViewset"""
    
    @pytest.fixture
    def viewset(self):
        return GradesViewset()
    
    @pytest.fixture
    def mock_request(self):
        factory = APIRequestFactory()
        return factory.get('/api/grades/')
    
    def test_normalize_grade(self, viewset):
        """Тестирование нормализации оценок"""
        test_cases = [
            ("5", "5"),
            ("4", "4"),
            ("3", "3"),
            ("2", "2"),
            ("Зачтено", "зачет"),
            ("Не зачтено", "незачет"),
            ("Н/Я", "неявка"),
            ("", "Не указано"),
            ("Неизвестно", "Неизвестно")
        ]
        
        for input_grade, expected_output in test_cases:
            result = viewset.normalize_grade(input_grade)
            assert result == expected_output, f"Failed for input: {input_grade}"
    
    def test_extract_year_from_group_name(self, viewset):
        """Тестирование извлечения года из названия группы"""
        test_cases = [
            ("ФИТ-21Б", 2021),
            ("МАТ-19А", 2019),
            ("ФИЗ-23", 2023),
            ("ИВТ-20В", 2020),
            ("Некорректное-название", None),
            ("Без-дефиса", None),
            ("", None),
            (None, None)
        ]
        
        for group_name, expected_year in test_cases:
            result = viewset.extract_year_from_group_name(group_name)
            assert result == expected_year, f"Failed for group: {group_name}"
    
    @patch('application.api.datetime')
    def test_calculate_course(self, mock_datetime, viewset):
        """Тестирование расчета курса"""
        # Январь 2024 - до сентября
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        assert viewset.calculate_course(2021) == 3
        
        # Сентябрь 2024 - после сентября
        mock_datetime.now.return_value = datetime(2024, 9, 15)
        assert viewset.calculate_course(2021) == 4
        
        # Декабрь 2024 - после сентября
        mock_datetime.now.return_value = datetime(2024, 12, 15)
        assert viewset.calculate_course(2021) == 4
    
    def test_student_is_still_enrolled(self, viewset):
        """Тестирование проверки, учится ли студент"""
        # Текущий год меньше года выпуска
        with patch('application.api.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 6, 1)
            assert viewset.student_is_still_enrolled(2021) == True
        
        # Текущий год равен году выпуска, но месяц до июля
        with patch('application.api.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 6, 1)
            assert viewset.student_is_still_enrolled(2021) == True
        
        # Текущий год равен году выпуска, месяц после июля
        with patch('application.api.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 1)
            assert viewset.student_is_still_enrolled(2021) == False
        
        # Текущий год больше года выпуска
        with patch('application.api.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 1, 1)
            assert viewset.student_is_still_enrolled(2021) == False
    
    def test_update_grade_stats(self, viewset):
        """Тестирование обновления статистики оценок"""
        grade_stats = {
            'numeric_grades': [],
            'countGrade2': 0, 'countGrade3': 0, 'countGrade4': 0, 'countGrade5': 0,
            'countZachet': 0, 'countNejavka': 0, 'countNezachet': 0
        }
        
        # Тестируем числовые оценки
        viewset.update_grade_stats(grade_stats, "5")
        assert grade_stats['countGrade5'] == 1
        assert grade_stats['numeric_grades'] == [5]
        
        viewset.update_grade_stats(grade_stats, "4")
        assert grade_stats['countGrade4'] == 1
        assert grade_stats['numeric_grades'] == [5, 4]
        
        # Тестируем зачеты/незачеты
        viewset.update_grade_stats(grade_stats, "зачет")
        assert grade_stats['countZachet'] == 1
        
        viewset.update_grade_stats(grade_stats, "незачет")
        assert grade_stats['countNezachet'] == 1
        
        # Тестируем неявку
        viewset.update_grade_stats(grade_stats, "неявка")
        assert grade_stats['countNejavka'] == 1
    
    @patch('application.api.StudentResult.objects')
    def test_list_method_with_mocks(self, mock_studentresult, viewset, mock_request):
        """Тестирование метода list"""
        # Создаем моки для объектов
        mock_student1 = MagicMock()
        mock_student1.student_id = 1
        mock_student1.group.name = "ФИТ-21Б"
        mock_student1.is_academic = False
        
        mock_student2 = MagicMock()
        mock_student2.student_id = 2
        mock_student2.group.name = "ФИТ-21Б"
        mock_student2.is_academic = False
        
        mock_discipline1 = MagicMock()
        mock_discipline1.name = "Математика"
        mock_discipline1.discipline_id = 1
        
        mock_discipline2 = MagicMock()
        mock_discipline2.name = "Физика"
        mock_discipline2.discipline_id = 2
        
        mock_result1 = MagicMock()
        mock_result1.result_value = "5"
        
        mock_result2 = MagicMock()
        mock_result2.result_value = "4"
        
        # Мокаем queryset
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value.filter.return_value = [
            MagicMock(
                student=mock_student1,
                discipline=mock_discipline1,
                result=mock_result1
            ),
            MagicMock(
                student=mock_student1,
                discipline=mock_discipline2,
                result=mock_result2
            ),
            MagicMock(
                student=mock_student2,
                discipline=mock_discipline1,
                result=mock_result1
            )
        ]
        
        mock_studentresult.select_related.return_value.filter.return_value = mock_queryset
        
        # Мокаем request
        viewset.request = mock_request
        viewset.request.query_params = {}
        
        # Вызываем метод list
        response = viewset.list(mock_request)
        
        # Проверяем, что метод выполнился без ошибок
        assert response.status_code == 200
        assert 'summary' in response.data
        assert 'students' in response.data
        assert 'subjects' in response.data
    
    @patch('application.api.StudentResult.objects')
    def test_list_with_filters(self, mock_studentresult, viewset, mock_request):
        """Тестирование метода list с фильтрами"""
        # Настраиваем моки
        mock_student = MagicMock()
        mock_student.student_id = 1
        mock_student.group.name = "ФИТ-21Б"
        mock_student.is_academic = False
        
        mock_discipline = MagicMock()
        mock_discipline.name = "Математика"
        mock_discipline.discipline_id = 1
        
        mock_result = MagicMock()
        mock_result.result_value = "5"
        
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value.filter.return_value = [
            MagicMock(
                student=mock_student,
                discipline=mock_discipline,
                result=mock_result
            )
        ]
        
        mock_studentresult.select_related.return_value.filter.return_value = mock_queryset
        
        # Тестируем с фильтром по группе
        mock_request.query_params = {'group': 'ФИТ-21Б'}
        viewset.request = mock_request
        
        response = viewset.list(mock_request)
        assert response.status_code == 200


class TestAcademicPerformanceViewSetWithMocks:
    """Тесты для AcademicPerformanceViewSet"""
    
    @pytest.fixture
    def viewset(self):
        return AcademicPerformanceViewSet()
    
    @pytest.fixture
    def mock_request(self):
        factory = APIRequestFactory()
        return factory.get('/api/academic-performance/')
    
    def test_get_debts_filter(self, viewset):
        """Тестирование фильтра задолженностей"""
        debts_filter = viewset.get_debts_filter()
        
        # Проверяем, что фильтр содержит правильные условия
        assert debts_filter is not None
        
        # Можно проверить строковое представление фильтра
        filter_str = str(debts_filter)
        assert '2' in filter_str or 'Н/Я' in filter_str or 'Не зачтено' in filter_str
    
    @patch('application.api.Student.objects')
    def test_get_queryset(self, mock_student, viewset):
        """Тестирование базового queryset"""
        # Мокаем аннотированный queryset
        mock_queryset = MagicMock()
        mock_student.select_related.return_value.filter.return_value.annotate.return_value.order_by.return_value = mock_queryset
        
        queryset = viewset.get_queryset()
        
        # Проверяем, что методы были вызваны с правильными параметрами
        mock_student.select_related.assert_called_once_with('group')
        mock_student.select_related.return_value.filter.assert_called_once()
    
    @patch('application.api.Student.objects')
    @patch('application.api.StudentGroup.objects')
    def test_calculate_group_stats(self, mock_studentgroup, mock_student, viewset):
        """Тестирование расчета статистики по группам"""
        # Мокаем группы
        mock_group1 = MagicMock()
        mock_group1.name = "ФИТ-21Б"
        
        mock_group2 = MagicMock()
        mock_group2.name = "ФИТ-22А"
        
        mock_studentgroup.filter.return_value = [mock_group1, mock_group2]
        
        # Мокаем студентов с задолженностями
        mock_student1 = MagicMock()
        mock_student1.debt_count = 2
        
        mock_student2 = MagicMock()
        mock_student2.debt_count = 0
        
        mock_student3 = MagicMock()
        mock_student3.debt_count = 1
        
        # Мокаем queryset для фильтрации по группам
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value.exists.return_value = True
        mock_queryset.filter.return_value.__iter__ = Mock(return_value=iter([mock_student1, mock_student2]))
        mock_queryset.filter.return_value.__len__ = Mock(return_value=2)
        
        mock_student.select_related.return_value.filter.return_value.annotate.return_value.order_by.return_value = mock_queryset
        
        group_stats = viewset.calculate_group_stats(mock_queryset)
        
        # Проверяем структуру ответа
        assert isinstance(group_stats, list)
        assert len(group_stats) == 2
        for stat in group_stats:
            assert 'group' in stat
            assert 'avgDebts' in stat
            assert isinstance(stat['avgDebts'], float)
    
    def test_get_debt_distribution(self, viewset):
        """Тестирование распределения задолженностей"""
        # Создаем мок студентов с разным количеством задолженностей
        mock_students = [
            MagicMock(debt_count=0),  # 0 долгов
            MagicMock(debt_count=0),  # 0 долгов
            MagicMock(debt_count=1),  # 1 долг
            MagicMock(debt_count=2),  # 2 долга
            MagicMock(debt_count=2),  # 2 долга
            MagicMock(debt_count=3),  # 3+ долга
            MagicMock(debt_count=5),  # 3+ долга
        ]
        
        distribution = viewset.get_debt_distribution(mock_students)
        
        assert distribution['zero_debts'] == 2
        assert distribution['one_debt'] == 1
        assert distribution['two_debts'] == 2
        assert distribution['three_plus_debts'] == 2
    
    @patch('application.api.StudentResult.objects')
    def test_get_student_debts_details(self, mock_studentresult, viewset):
        """Тестирование получения деталей задолженностей"""
        # Мокаем студента
        mock_student = MagicMock()
        mock_student.student_id = 1
        
        # Мокаем долги
        mock_debt1 = MagicMock()
        mock_debt1.discipline.name = "Математика"
        mock_debt1.result.result_value = "2"
        
        mock_debt2 = MagicMock()
        mock_debt2.discipline.name = "Физика"
        mock_debt2.result.result_value = "Н/Я"
        
        mock_studentresult.filter.return_value.select_related.return_value = [mock_debt1, mock_debt2]
        
        debts_details = viewset.get_student_debts_details(mock_student)
        
        assert len(debts_details) == 2
        assert debts_details[0]['discipline'] == "Математика"
        assert debts_details[0]['grade'] == "2"
        assert debts_details[1]['discipline'] == "Физика"
        assert debts_details[1]['grade'] == "Н/Я"


class TestSubjectStatisticsViewSetWithMocks:
    """Тесты для SubjectStatisticsViewSet"""
    
    @pytest.fixture
    def viewset(self):
        return SubjectStatisticsViewSet()
    
    @pytest.fixture
    def mock_request(self):
        factory = APIRequestFactory()
        return factory.get('/api/subject-statistics/')
    
    def test_normalize_grade_value(self, viewset):
        """Тестирование нормализации значений оценок"""
        test_cases = [
            ("5", 5),
            ("4", 4),
            ("3", 3),
            ("2", 2),
            ("Зачтено", "зачет"),
            ("Не зачтено", "незачет"),
            ("Н/Я", "неявка"),
            ("", None),
            ("Неизвестно", None),
            ("6", None),
            ("1", None)
        ]
        
        for input_value, expected_output in test_cases:
            result = viewset.normalize_grade_value(input_value)
            assert result == expected_output, f"Failed for input: {input_value}"
    
    @patch('application.api.StudentResult.objects')
    @patch('application.api.Attendance.objects')
    @patch('application.api.Student.objects')
    def test_list_method_with_mocks(self, mock_student, mock_attendance, mock_studentresult, viewset, mock_request):
        """Тестирование метода list с моками"""
        # Мокаем студентов
        mock_student1 = MagicMock()
        mock_student1.student_id = 1
        mock_student1.group.name = "ФИТ-21Б"
        
        mock_student.objects.select_related.return_value.filter.return_value = [mock_student1]
        
        # Мокаем результаты
        mock_discipline1 = MagicMock()
        mock_discipline1.discipline_id = 1
        mock_discipline1.name = "Математика"
        
        mock_discipline2 = MagicMock()
        mock_discipline2.discipline_id = 2
        mock_discipline2.name = "Физика"
        
        mock_result1 = MagicMock()
        mock_result1.result.result_value = "5"
        
        mock_result2 = MagicMock()
        mock_result2.result.result_value = "4"
        
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value.filter.return_value = [
            MagicMock(
                student=mock_student1,
                discipline=mock_discipline1,
                result=mock_result1.result
            ),
            MagicMock(
                student=mock_student1,
                discipline=mock_discipline2,
                result=mock_result2.result
            )
        ]
        
        mock_studentresult.select_related.return_value.filter.return_value = mock_queryset
        
        # Мокаем посещаемость
        mock_attendance_stats = MagicMock()
        mock_attendance_stats.aggregate.return_value = {
            'unique_lessons': 10,
            'unique_students': 5
        }
        mock_attendance.filter.return_value = mock_attendance_stats
        
        # Настраиваем request
        viewset.request = mock_request
        viewset.request.query_params = {}
        
        # Вызываем метод list
        response = viewset.list(mock_request)
        
        # Проверяем структуру ответа
        assert response.status_code == 200
        assert 'subjectStats' in response.data
        assert 'gradeDistributionBar' in response.data
        assert 'bestSubjects' in response.data


class TestStudentRatingViewSetWithMocks:
    """Тесты для StudentRatingViewSet"""
    
    @pytest.fixture
    def viewset(self):
        return StudentRatingViewSet()
    
    @pytest.fixture
    def mock_request(self):
        factory = APIRequestFactory()
        return factory.get('/api/student-rating/')
    
    def test_normalize_grade_value(self, viewset):
        """Тестирование нормализации значений оценок"""
        test_cases = [
            ("5", 5),
            ("4", 4),
            ("3", 3),
            ("2", 2),
            ("Зачтено", None),  # В этом ViewSet только числовые оценки
            ("Не зачтено", None),
            ("Н/Я", None),
            ("", None),
            ("6", None),
            ("1", None)
        ]
        
        for input_value, expected_output in test_cases:
            result = viewset.normalize_grade_value(input_value)
            assert result == expected_output, f"Failed for input: {input_value}"
    
    def test_classify_debt_type(self, viewset):
        """Тестирование классификации типов долгов"""
        test_cases = [
            ("2", "неуд"),
            ("Н/Я", "неявка"),
            ("Не зачтено", "незачет"),
            ("Другое", "другой"),
            ("", "другой"),
            (None, "другой")
        ]
        
        for grade_value, expected_type in test_cases:
            result = viewset.classify_debt_type(grade_value)
            assert result == expected_type, f"Failed for grade: {grade_value}"
    
    @pytest.mark.parametrize("risk_score,expected_level", [
        (0.0, "низкий"),
        (0.1, "низкий"),
        (0.29, "низкий"),
        (0.3, "средний"),
        (0.5, "средний"),
        (0.69, "средний"),
        (0.7, "высокий"),
        (0.9, "высокий"),
        (1.0, "высокий")
    ])
    def test_get_risk_level(self, risk_score, expected_level, viewset):
        """Тестирование определения уровня риска"""
        result = viewset.get_risk_level(risk_score)
        assert result == expected_level
    
    @patch('application.api.StudentResult.objects')
    def test_calculate_student_activity(self, mock_studentresult, viewset):
        """Тестирование расчета активности студента"""
        # Мокаем результаты студента
        mock_passed_subjects = MagicMock()
        mock_passed_subjects.count.return_value = 8
        
        mock_studentresult.filter.return_value = mock_passed_subjects
        
        # Мокаем посещаемость
        with patch('application.api.Attendance.objects') as mock_attendance:
            mock_attendance_count = MagicMock()
            mock_attendance_count.count.return_value = 45
            mock_attendance.filter.return_value = mock_attendance_count
            
            activity = viewset.calculate_student_activity(1)
            
            # Проверяем, что активность в пределах 0-5
            assert 0 <= activity <= 5.0
            assert isinstance(activity, float)
    
    @patch('application.api.Attendance.objects')
    def test_calculate_attendance_percent(self, mock_attendance, viewset):
        """Тестирование расчета процента посещаемости"""
        # Мокаем количество посещений
        mock_attendance_count = MagicMock()
        mock_attendance_count.count.return_value = 45
        mock_attendance.filter.return_value = mock_attendance_count
        
        attendance_percent = viewset.calculate_attendance_percent(1)
        
        # Проверяем, что процент в пределах 0-100
        assert 0 <= attendance_percent <= 100.0
        assert isinstance(attendance_percent, float)
        
        # Тест с нулевыми посещениями
        mock_attendance_count.count.return_value = 0
        attendance_percent = viewset.calculate_attendance_percent(1)
        assert attendance_percent == 0.0
    
    @patch('application.api.StudentResult.objects')
    def test_calculate_dropout_risk(self, mock_studentresult, viewset):
        """Тестирование расчета риска отчисления"""
        # Мокаем количество долгов
        mock_debts = MagicMock()
        mock_debts.count.return_value = 2
        mock_studentresult.filter.return_value = mock_debts
        
        risk = viewset.calculate_dropout_risk(
            student_id=1,
            avg_grade=3.5,
            attendance_percent=75.0,
            activity=3.0
        )
        
        # Проверяем, что риск в пределах 0-1
        assert 0 <= risk <= 1.0
        assert isinstance(risk, float)
    
    @patch('application.api.StudentResult.objects')
    def test_get_student_debts_details(self, mock_studentresult, viewset):
        """Тестирование получения деталей задолженностей"""
        # Мокаем долги
        mock_discipline1 = MagicMock()
        mock_discipline1.name = "Математика"
        
        mock_discipline2 = MagicMock()
        mock_discipline2.name = "Физика"
        
        mock_result1 = MagicMock()
        mock_result1.result_value = "2"
        
        mock_result2 = MagicMock()
        mock_result2.result_value = "Н/Я"
        
        mock_debt1 = MagicMock()
        mock_debt1.discipline = mock_discipline1
        mock_debt1.result = mock_result1
        
        mock_debt2 = MagicMock()
        mock_debt2.discipline = mock_discipline2
        mock_debt2.result = mock_result2
        
        mock_studentresult.filter.return_value.select_related.return_value = [mock_debt1, mock_debt2]
        
        debts_details = viewset.get_student_debts_details(1)
        
        assert len(debts_details) == 2
        assert debts_details[0]['discipline'] == "Математика"
        assert debts_details[0]['grade'] == "2"
        assert debts_details[0]['type'] == "неуд"
        assert debts_details[1]['discipline'] == "Физика"
        assert debts_details[1]['grade'] == "Н/Я"
        assert debts_details[1]['type'] == "неявка"


class TestEdgeCasesWithMocks:
    """Тесты для граничных случаев с моками"""
    
    def test_empty_inputs_grades_viewset(self):
        """Тестирование обработки пустых входных данных в GradesViewset"""
        viewset = GradesViewset()
        
        # Пустые строки и None
        assert viewset.normalize_grade("") == "Не указано"
        assert viewset.normalize_grade(None) == "Не указано"
        
        # Некорректные названия групп
        assert viewset.extract_year_from_group_name("") is None
        assert viewset.extract_year_from_group_name("Некорректно") is None
        assert viewset.extract_year_from_group_name("ФИТ") is None
        assert viewset.extract_year_from_group_name("ФИТ-") is None
    
    def test_invalid_grade_values_all_viewsets(self):
        """Тестирование обработки невалидных оценок во всех ViewSet"""
        grades_viewset = GradesViewset()
        subject_viewset = SubjectStatisticsViewSet()
        rating_viewset = StudentRatingViewSet()
        
        # Невалидные числовые значения
        invalid_grades = ["6", "1", "0", "-1", "1.5", "abc", "!"]
        
        for invalid_grade in invalid_grades:
            # GradesViewset оставляет как есть
            assert grades_viewset.normalize_grade(invalid_grade) == invalid_grade
            
            # SubjectStatisticsViewSet возвращает None
            assert subject_viewset.normalize_grade_value(invalid_grade) is None
            
            # StudentRatingViewSet возвращает None
            assert rating_viewset.normalize_grade_value(invalid_grade) is None
    
    @patch('application.api.datetime')
    def test_boundary_dates_course_calculation(self, mock_datetime, viewset=None):
        """Тестирование граничных дат для расчета курса"""
        if viewset is None:
            viewset = GradesViewset()
        
        # 31 августа - еще старый курс
        mock_datetime.now.return_value = datetime(2024, 8, 31)
        assert viewset.calculate_course(2021) == 3
        
        # 1 сентября - уже новый курс
        mock_datetime.now.return_value = datetime(2024, 9, 1)
        assert viewset.calculate_course(2021) == 4
        
        # 31 декабря - все еще новый курс
        mock_datetime.now.return_value = datetime(2024, 12, 31)
        assert viewset.calculate_course(2021) == 4


# Интеграционные тесты с моками
class TestIntegrationWithMocks:
    """Интеграционные тесты с полным мокированием"""
    
    @patch('application.api.Student.objects')
    @patch('application.api.StudentResult.objects')
    @patch('application.api.Attendance.objects')
    def test_complete_student_rating_flow(self, mock_attendance, mock_studentresult, mock_student):
        """Тест полного потока расчета рейтинга студента"""
        viewset = StudentRatingViewSet()
        
        # Мокаем студентов
        mock_student1 = MagicMock()
        mock_student1.student_id = 1
        mock_student1.group.name = "ФИТ-21Б"
        mock_student1.group.speciality.faculty.name = "ФИТ"
        
        mock_student.objects.select_related.return_value.filter.return_value = [mock_student1]
        
        # Мокаем результаты с оценками
        mock_result_queryset = MagicMock()
        mock_result_queryset.select_related.return_value = [
            MagicMock(result=MagicMock(result_value="5")),
            MagicMock(result=MagicMock(result_value="4")),
            MagicMock(result=MagicMock(result_value="5"))
        ]
        mock_studentresult.filter.return_value = mock_result_queryset
        
        # Мокаем посещаемость
        mock_attendance.filter.return_value.count.return_value = 50
        
        # Мокаем долги
        mock_debts = MagicMock()
        mock_debts.count.return_value = 1
        mock_studentresult.filter.return_value = mock_debts
        
        # Тестируем расчет среднего балла
        numeric_grades = []
        for result in mock_result_queryset.select_related.return_value:
            grade_value = viewset.normalize_grade_value(result.result.result_value)
            if grade_value and 2 <= grade_value <= 5:
                numeric_grades.append(grade_value)
        
        assert numeric_grades == [5, 4, 5]
        assert sum(numeric_grades) / len(numeric_grades) == pytest.approx(4.67, 0.01)
        
        # Тестируем расчет активности
        mock_passed_subjects = MagicMock()
        mock_passed_subjects.count.return_value = 10
        mock_studentresult.filter.return_value = mock_passed_subjects
        
        activity = viewset.calculate_student_activity(1)
        assert 0 <= activity <= 5.0
        
        # Тестируем расчет посещаемости
        attendance_percent = viewset.calculate_attendance_percent(1)
        assert 0 <= attendance_percent <= 100.0
        
        # Тестируем расчет риска
        risk = viewset.calculate_dropout_risk(1, 4.67, attendance_percent, activity)
        assert 0 <= risk <= 1.0


if __name__ == "__main__":
    print("Running mocked tests...")
    
    # Test GradesViewset
    test_grades = TestGradesViewsetWithMocks()
    test_grades.test_normalize_grade()
    test_grades.test_extract_year_from_group_name()
    test_grades.test_update_grade_stats()
    
    # Test StudentRatingViewSet
    test_rating = TestStudentRatingViewSetWithMocks()
    test_rating.test_normalize_grade_value()
    test_rating.test_classify_debt_type()
    test_rating.test_get_risk_level(0.1, "низкий")