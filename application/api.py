from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.db.models import Avg, Count, Min, Max, Q, IntegerField, Value, Case, When, F, ExpressionWrapper, FloatField
from .models import Grades, Academ, CourseProjects
from app.serializers import GradesSerializer
from datetime import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import mixins, viewsets
from django.utils import timezone


from collections import defaultdict

from .models import Student, Debts, Group

from itertools import chain

from application.management.commands import analytics

from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.viewsets import ViewSet

from django.core.management import call_command

from rest_framework.decorators import action

import os

import pandas as pd

import csv

class GradesViewset(mixins.ListModelMixin, GenericViewSet):
    """
    ViewSet для получения оценок студентов с агрегированной статистикой.
    
    Назначение:
    - Предоставляет API endpoint для получения детализированной информации об оценках
    - Объединяет данные из моделей Grades и CourseProjects
    - Формирует статистику по успеваемости с распределением по типам оценок
    - Поддерживает фильтрацию по курсу, семестру, группе и предмету
    
    Входные параметры (query parameters):
    - course: номер курса (целое число, опционально)
    - semester: номер семестра (целое число, опционально) 
    - group: название группы (строка, опционально)
    - subject: название предмета (строка, опционально)
    
    Выходные данные:
    - JSON объект с тремя основными разделами:
      1. summary - общая статистика по оценкам
      2. students - детализированные данные по студентам с их оценками
      3. subjects - список всех предметов в выборке
    """
    queryset = Grades.objects.select_related('student', 'student__group', 'fc')
    serializer_class = GradesSerializer

    def calculate_course(self, year_of_admission: int) -> int:
        """
        Вычисляет текущий курс студента на основе года поступления.
        
        Параметры:
        - year_of_admission: int - год поступления студента
        
        Возвращает:
        - int: текущий курс студента
        
        Логика расчета:
        - Если текущий месяц до сентября: курс = текущий год - год поступления
        - Если текущий месяц сентябрь или позднее: курс = текущий год - год поступления + 1
        """
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        if current_month < 9:
            return current_year - year_of_admission
        else:
            return current_year - year_of_admission + 1

    def extract_year_from_group_title(self, title: str) -> int | None:
        """
        Извлекает год поступления из названия группы.
        
        Параметры:
        - title: str - название группы (формат: "XXX-YYZZ", где YY - год)
        
        Возвращает:
        - int | None: год поступления или None при ошибке парсинга
        
        Логика работы:
        - Разделяет строку по дефису и берет вторую часть
        - Определяет век (2000 или 1900) на основе текущего года
        - Пример: "ФИТ-21Б" → 2021 год
        """
        try:
            parts = title.split('-')
            year_suffix = int(parts[1])
            current_year = datetime.now().year % 100
            century = 2000 if year_suffix <= current_year else 1900
            return century + year_suffix
        except (IndexError, ValueError):
            return None

    def student_is_still_enrolled(self, year_of_admission: int) -> bool:
        """
        Проверяет, продолжает ли студент обучение.
        
        Параметры:
        - year_of_admission: int - год поступления студента
        
        Возвращает:
        - bool: True если студент еще учится, False если должен был уже выпуститься
        
        Логика расчета:
        - Ожидаемый год выпуска = год поступления + 4
        - Если текущий год меньше ожидаемого выпуска → учится
        - Если текущий год равен выпуску и месяц до июля → учится
        """
        now = datetime.now()
        expected_graduation_year = year_of_admission + 4
        return now.year < expected_graduation_year or (now.year == expected_graduation_year and now.month < 7)

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения оценок студентов.
        
        Входные параметры:
        - request: HTTP-запрос с параметрами фильтрации
        
        Выходные данные:
        - Response: JSON объект со структурой:
          {
            "summary": {
                "totalStudents": int,
                "averageGrade": float,
                "countGrade2": int,
                "countGrade3": int, 
                "countGrade4": int,
                "countGrade5": int,
                "countZachet": int,
                "countNejavka": int,
                "minGrade": int,
                "maxGrade": int
            },
            "students": [
                {
                    "id": int,
                    "name": str,
                    "group": str,
                    "course": int,
                    "subjects": [
                        {
                            "subject": str,
                            "grades": list
                        }
                    ]
                }
            ],
            "subjects": [
                {
                    "id": int,
                    "name": str
                }
            ]
          }
        
        Особенности реализации:
        - Объединяет данные из обычных оценок и курсовых проектов
        - Валидирует соответствие курса и семестра
        - Фильтрует только действующих студентов
        - Группирует оценки по предметам для каждого студента
        """
        # Get regular grades queryset
        grades_queryset = self.get_queryset()
        
        # Get course projects queryset
        course_projects_queryset = CourseProjects.objects.select_related(
            'student', 'student__group', 'hps', 'hps__disciple'
        )

        course_param = request.query_params.get('course')
        semester = request.query_params.get('semester')
        group = request.query_params.get('group')
        subject = request.query_params.get('subject')

        # Validate course-semester pair
        if course_param and semester:
            try:
                course_int = int(course_param)
                semester_int = int(semester)
                if semester_int not in [(course_int - 1) * 2 + 1, (course_int - 1) * 2 + 2]:
                    return Response({
                        "summary": {
                            "totalStudents": 0,
                            "averageGrade": None,
                            "countGrade2": 0,
                            "countGrade3": 0,
                            "countGrade4": 0,
                            "countGrade5": 0,
                            "countZachet": 0,
                            "countNejavka": 0,
                            "minGrade": None,
                            "maxGrade": None
                        },
                        "students": []
                    })
            except ValueError:
                pass

        # Apply filters to both querysets
        if semester:
            grades_queryset = grades_queryset.filter(fc__hps__semester=semester)
            course_projects_queryset = course_projects_queryset.filter(hps__semester=semester)
        if group:
            grades_queryset = grades_queryset.filter(student__group__title=group)
            course_projects_queryset = course_projects_queryset.filter(student__group__title=group)
        if subject:
            grades_queryset = grades_queryset.filter(fc__hps__disciple__disciple_name=subject)
            course_projects_queryset = course_projects_queryset.filter(hps__disciple__disciple_name=subject)

        try:
            course_param = int(course_param) if course_param else None
        except ValueError:
            course_param = None

        # Process grades and course projects
        students_data_dict = defaultdict(lambda: {
            "id": None,
            "name": None,
            "group": None,
            "course": None,
            "subjects": defaultdict(list)
        })
        
        subjects_info = set()
        grade_stats = {
            'numeric_grades': [],
            'countGrade2': 0,
            'countGrade3': 0,
            'countGrade4': 0,
            'countGrade5': 0,
            'countZachet': 0,
            'countNejavka': 0
        }

        # Process regular grades
        for grade in grades_queryset.select_related('student', 'student__group', 'fc__hps__disciple'):
            student = grade.student
            group_obj = student.group
            subject_obj = grade.fc.hps.disciple if grade.fc and grade.fc.hps and grade.fc.hps.disciple else None
            
            if not grade.grade or not subject_obj:
                continue
                
            if group_obj and group_obj.title:
                year_of_admission = self.extract_year_from_group_title(group_obj.title)
                if year_of_admission:
                    if not self.student_is_still_enrolled(year_of_admission):
                        continue
                    course = self.calculate_course(year_of_admission)
                    if course_param and course != course_param:
                        continue
            
            # Заполняем основную информацию о студенте
            students_data_dict[student.student_id]["id"] = student.student_id
            students_data_dict[student.student_id]["name"] = student.name
            students_data_dict[student.student_id]["group"] = group_obj.title if group_obj else None
            students_data_dict[student.student_id]["course"] = self.calculate_course(
                self.extract_year_from_group_title(group_obj.title)
            ) if group_obj and group_obj.title else None
            
            # Обрабатываем оценку
            grade_value = str(grade.grade).strip()
            subject_name = subject_obj.disciple_name
            subjects_info.add((subject_name, subject_obj.disciple_id))
            
            if grade_value.isdigit():
                grade_int = int(grade_value)
                if 2 <= grade_int <= 5:
                    students_data_dict[student.student_id]["subjects"][subject_name].append(grade_int)
                    grade_stats['numeric_grades'].append(grade_int)
                    grade_stats[f'countGrade{grade_int}'] += 1
            elif grade_value.lower() == 'зачет':
                students_data_dict[student.student_id]["subjects"][subject_name].append(grade_value)
                grade_stats['countZachet'] += 1
            elif grade_value.lower() == 'неявка':
                students_data_dict[student.student_id]["subjects"][subject_name].append(grade_value)
                grade_stats['countNejavka'] += 1

        # Process course projects
        for course_project in course_projects_queryset:
            student = course_project.student
            group_obj = student.group
            subject_obj = course_project.hps.disciple if course_project.hps and course_project.hps.disciple else None
            
            if not course_project.grade or not subject_obj:
                continue
                
            if group_obj and group_obj.title:
                year_of_admission = self.extract_year_from_group_title(group_obj.title)
                if year_of_admission:
                    if not self.student_is_still_enrolled(year_of_admission):
                        continue
                    course = self.calculate_course(year_of_admission)
                    if course_param and course != course_param:
                        continue
            
            # Заполняем основную информацию о студенте
            students_data_dict[student.student_id]["id"] = student.student_id
            students_data_dict[student.student_id]["name"] = student.name
            students_data_dict[student.student_id]["group"] = group_obj.title if group_obj else None
            students_data_dict[student.student_id]["course"] = self.calculate_course(
                self.extract_year_from_group_title(group_obj.title)
            ) if group_obj and group_obj.title else None
            
            # Обрабатываем оценку
            grade_int = course_project.grade
            subject_name = subject_obj.disciple_name
            subjects_info.add((subject_name, subject_obj.disciple_id))
            
            if 2 <= grade_int <= 5:
                students_data_dict[student.student_id]["subjects"][subject_name].append(grade_int)
                grade_stats['numeric_grades'].append(grade_int)
                grade_stats[f'countGrade{grade_int}'] += 1

        # Prepare final students data
        students_data = []
        for student_id, student_data in students_data_dict.items():
            if not student_data["id"]:
                continue
                
            subjects_list = [
                {
                    "subject": subject_name,
                    "grades": grades
                }
                for subject_name, grades in student_data["subjects"].items()
            ]
            
            students_data.append({
                "id": student_data["id"],
                "name": student_data["name"],
                "group": student_data["group"],
                "course": student_data["course"],
                "subjects": subjects_list
            })

        # Calculate statistics
        numeric_grades = grade_stats['numeric_grades']
        total_students = len(students_data)
        
        stats = {
            "totalStudents": total_students,
            "averageGrade": round(sum(numeric_grades) / len(numeric_grades), 2) if numeric_grades else None,
            "countGrade2": grade_stats['countGrade2'],
            "countGrade3": grade_stats['countGrade3'],
            "countGrade4": grade_stats['countGrade4'],
            "countGrade5": grade_stats['countGrade5'],
            "countZachet": grade_stats['countZachet'],
            "countNejavka": grade_stats['countNejavka'],
            "minGrade": min(numeric_grades) if numeric_grades else None,
            "maxGrade": max(numeric_grades) if numeric_grades else None
        }

        response_data = {
            "summary": stats,
            "students": students_data,
            "subjects": [{"id": sub_id, "name": sub_name} for sub_name, sub_id in subjects_info]
        }

        return Response(response_data)

# class GradesViewset(mixins.ListModelMixin, GenericViewSet):
#     queryset = Grades.objects.select_related('student', 'student__group', 'fc')
#     serializer_class = GradesSerializer

#     def calculate_course(self, year_of_admission: int) -> int:
#         now = datetime.now()
#         current_year = now.year
#         current_month = now.month
#         if current_month < 9:
#             return current_year - year_of_admission
#         else:
#             return current_year - year_of_admission + 1

#     def extract_year_from_group_title(self, title: str) -> int | None:
#         try:
#             parts = title.split('-')
#             year_suffix = int(parts[1])
#             current_year = datetime.now().year % 100
#             century = 2000 if year_suffix <= current_year else 1900
#             return century + year_suffix
#         except (IndexError, ValueError):
#             return None

#     def student_is_still_enrolled(self, year_of_admission: int) -> bool:
#         now = datetime.now()
#         expected_graduation_year = year_of_admission + 4
#         return now.year < expected_graduation_year or (now.year == expected_graduation_year and now.month < 7)

#     def list(self, request, *args, **kwargs):
#         # Get regular grades queryset
#         grades_queryset = self.get_queryset()
        
#         # Get course projects queryset
#         course_projects_queryset = CourseProjects.objects.select_related(
#             'student', 'student__group', 'hps', 'hps__disciple'
#         )

#         course_param = request.query_params.get('course')
#         semester = request.query_params.get('semester')
#         group = request.query_params.get('group')
#         subject = request.query_params.get('subject')

#         # Validate course-semester pair
#         if course_param and semester:
#             try:
#                 course_int = int(course_param)
#                 semester_int = int(semester)
#                 if semester_int not in [(course_int - 1) * 2 + 1, (course_int - 1) * 2 + 2]:
#                     return Response({
#                         "summary": {
#                             "totalStudents": 0,
#                             "averageGrade": None,
#                             "countGrade2": 0,
#                             "countGrade3": 0,
#                             "countGrade4": 0,
#                             "countGrade5": 0,
#                             "countZachet": 0,
#                             "countNejavka": 0,
#                             "minGrade": None,
#                             "maxGrade": None
#                         },
#                         "students": []
#                     })
#             except ValueError:
#                 pass

#         # Apply filters to both querysets
#         if semester:
#             grades_queryset = grades_queryset.filter(fc__hps__semester=semester)
#             course_projects_queryset = course_projects_queryset.filter(hps__semester=semester)
#         if group:
#             grades_queryset = grades_queryset.filter(student__group__title=group)
#             course_projects_queryset = course_projects_queryset.filter(student__group__title=group)
#         if subject:
#             grades_queryset = grades_queryset.filter(fc__hps__disciple__disciple_name=subject)
#             course_projects_queryset = course_projects_queryset.filter(hps__disciple__disciple_name=subject)

#         try:
#             course_param = int(course_param) if course_param else None
#         except ValueError:
#             course_param = None

#         # Process grades and course projects
#         students_grades = defaultdict(list)
#         grade_stats = {
#             'numeric_grades': [],
#             'countGrade2': 0,
#             'countGrade3': 0,
#             'countGrade4': 0,
#             'countGrade5': 0,
#             'countZachet': 0,
#             'countNejavka': 0
#         }

#         # Process regular grades
#         for grade in grades_queryset.select_related('student', 'student__group', 'fc__hps__disciple'):
#             student = grade.student
#             group_obj = student.group
            
#             if not grade.grade:
#                 continue
                
#             if group_obj and group_obj.title:
#                 year_of_admission = self.extract_year_from_group_title(group_obj.title)
#                 if year_of_admission:
#                     if not self.student_is_still_enrolled(year_of_admission):
#                         continue
#                     course = self.calculate_course(year_of_admission)
#                     if course_param and course != course_param:
#                         continue
            
#             grade_value = str(grade.grade).strip()
            
#             if grade_value.isdigit():
#                 grade_int = int(grade_value)
#                 if 2 <= grade_int <= 5:
#                     students_grades[student.student_id].append({
#                         "grade": grade_int,
#                         "type": "grade"
#                     })
#                     grade_stats['numeric_grades'].append(grade_int)
#                     grade_stats[f'countGrade{grade_int}'] += 1
#             elif grade_value.lower() == 'зачет':
#                 students_grades[student.student_id].append({
#                     "grade": grade_value,
#                     "type": "zachet"
#                 })
#                 grade_stats['countZachet'] += 1
#             elif grade_value.lower() == 'неявка':
#                 students_grades[student.student_id].append({
#                     "grade": grade_value,
#                     "type": "nejavka"
#                 })
#                 grade_stats['countNejavka'] += 1

#         # Process course projects
#         for course_project in course_projects_queryset:
#             student = course_project.student
#             group_obj = student.group
            
#             if not course_project.grade:
#                 continue
                
#             if group_obj and group_obj.title:
#                 year_of_admission = self.extract_year_from_group_title(group_obj.title)
#                 if year_of_admission:
#                     if not self.student_is_still_enrolled(year_of_admission):
#                         continue
#                     course = self.calculate_course(year_of_admission)
#                     if course_param and course != course_param:
#                         continue
            
#             grade_int = course_project.grade
#             if 2 <= grade_int <= 5:
#                 students_grades[student.student_id].append({
#                     "grade": grade_int,
#                     "type": "grade",
#                     "is_course_project": True
#                 })
#                 grade_stats['numeric_grades'].append(grade_int)
#                 grade_stats[f'countGrade{grade_int}'] += 1

#         # Prepare students data
#         students_data = []
#         processed_student_ids = set()
        
#         # Combine data from both querysets
#         for grade in chain(
#             grades_queryset.select_related('student', 'student__group'),
#             course_projects_queryset.select_related('student', 'student__group')
#         ):
#             student = grade.student
#             if student.student_id in processed_student_ids:
#                 continue
                
#             if student.student_id not in students_grades:
#                 continue
                
#             group_obj = student.group
            
#             students_data.append({
#                 "id": student.student_id,
#                 "name": student.name,
#                 "group": group_obj.title if group_obj else None,
#                 "course": self.calculate_course(self.extract_year_from_group_title(group_obj.title)) 
#                            if group_obj and group_obj.title else None,
#                 "grades": [g["grade"] for g in students_grades[student.student_id]]
#             })
#             processed_student_ids.add(student.student_id)

#         # Calculate statistics
#         numeric_grades = grade_stats['numeric_grades']
#         total_students = len(students_data)
        
#         stats = {
#             "totalStudents": total_students,
#             "averageGrade": round(sum(numeric_grades) / len(numeric_grades), 2) if numeric_grades else None,
#             "countGrade2": grade_stats['countGrade2'],
#             "countGrade3": grade_stats['countGrade3'],
#             "countGrade4": grade_stats['countGrade4'],
#             "countGrade5": grade_stats['countGrade5'],
#             "countZachet": grade_stats['countZachet'],
#             "countNejavka": grade_stats['countNejavka'],
#             "minGrade": min(numeric_grades) if numeric_grades else None,
#             "maxGrade": max(numeric_grades) if numeric_grades else None
#         }

#         return Response({
#             "summary": stats,
#             "students": students_data
#         })

class AcademicPerformanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet для получения статистики по успеваемости студентов с учётом истории задолженностей.
    
    Назначение:
    - Предоставляет API endpoint для анализа академической успеваемости
    - Учитывает только активные задолженности (не закрытые)
    - Формирует распределение студентов по количеству задолженностей
    - Рассчитывает средние показатели по группам
    
    Входные параметры (query parameters):
    - group: название группы (строка, точное совпадение, опционально)
    - search: поисковый запрос по имени студента (строка, опционально)
    
    Выходные данные:
    - JSON объект с тремя основными разделами:
      1. debtsDistribution - распределение студентов по количеству задолженностей
      2. groupAverages - средние показатели задолженностей по группам
      3. students - детализированная информация по студентам
    """
    
    queryset = Student.objects.none()
    
    def get_active_debts_filter(self):
        """
        Создает фильтр для активных задолженностей.
        
        Возвращает:
        - Q: объект фильтра Django для активных задолженностей
        
        Логика фильтрации:
        - Долг сформирован (debts__debtaudit__debt_event='Долг сформирован')
        - Долг не закрыт (~Q(debts__debtaudit__debt_event='Долг закрыт'))
        """
        return Q(debts__debtaudit__debt_event='Долг сформирован') & \
               ~Q(debts__debtaudit__debt_event='Долг закрыт')
    
    def get_queryset(self):
        """
        Получает базовый queryset с аннотацией активных задолженностей.
        
        Возвращает:
        - QuerySet: Студенты с аннотированным количеством активных задолженностей
        
        Особенности:
        - Использует select_related для оптимизации запросов к группе
        - Аннотирует количество активных задолженностей для каждого студента
        - Сортирует студентов по имени
        """
        return Student.objects.select_related('group').annotate(
            active_debt_count=Count('debts', 
                                  filter=self.get_active_debts_filter(),
                                  distinct=True)
        ).order_by('name')
    
    def calculate_group_stats(self, queryset):
        """
        Рассчитывает статистику по группам с учётом активных задолженностей.
        
        Параметры:
        - queryset: QuerySet - отфильтрованный набор студентов
        
        Возвращает:
        - list: список словарей со статистикой по группам
        
        Структура элемента:
        {
            "group": str,      # Название группы
            "avgDebts": float  # Среднее количество задолженностей в группе
        }
        """
        groups = Group.objects.filter(
            student__in=queryset
        ).distinct()
        
        group_stats = []
        
        for group in groups:
            avg_debts = Student.objects.filter(
                group=group
            ).annotate(
                active_debt_count=Count('debts', 
                                      filter=self.get_active_debts_filter())
            ).aggregate(
                avg=Avg('active_debt_count')
            )['avg'] or 0
            
            group_stats.append({
                "group": group.title,
                "avgDebts": round(float(avg_debts), 1)
            })
        
        return group_stats
    
    def get_debt_distribution(self, queryset):
        """
        Получает распределение студентов по количеству активных задолженностей.
        
        Параметры:
        - queryset: QuerySet - отфильтрованный набор студентов
        
        Возвращает:
        - dict: словарь с количеством студентов по категориям задолженностей
        
        Категории:
        - zero_debts: студенты без задолженностей
        - one_debt: студенты с 1 задолженностью
        - two_debts: студенты с 2 задолженностями
        - three_plus_debts: студенты с 3 и более задолженностями
        """
        return queryset.aggregate(
            zero_debts=Count(Case(When(active_debt_count=0, then=1), output_field=IntegerField())),
            one_debt=Count(Case(When(active_debt_count=1, then=1), output_field=IntegerField())),
            two_debts=Count(Case(When(active_debt_count=2, then=1), output_field=IntegerField())),
            three_plus_debts=Count(Case(When(active_debt_count__gte=3, then=1), output_field=IntegerField()))
        )
    
    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения статистики успеваемости.
        
        Входные параметры:
        - request: HTTP-запрос с параметрами фильтрации
        
        Выходные данные:
        - Response: JSON объект со структурой:
          {
            "debtsDistribution": {
                "0": int,    # Студентов без задолженностей
                "1": int,    # Студентов с 1 задолженностью
                "2": int,    # Студентов с 2 задолженностями
                "3plus": int # Студентов с 3+ задолженностями
            },
            "groupAverages": [
                {
                    "group": str,
                    "avgDebts": float
                }
            ],
            "students": [
                {
                    "id": int,
                    "name": str, 
                    "group": str,
                    "debts": int
                }
            ]
          }
        
        Особенности реализации:
        - Применяет фильтры по группе и поисковому запросу
        - Рассчитывает распределение задолженностей
        - Формирует средние показатели по группам
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Применяем фильтры
        group_filter = request.query_params.get('group')
        search_query = request.query_params.get('search', '').strip()
        
        if group_filter:
            queryset = queryset.filter(group__title=group_filter)
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        # Подготавливаем данные студентов
        students_data = [
            {
                "id": student.student_id,
                "name": student.name,
                "group": student.group.title if student.group else None,
                "debts": student.active_debt_count
            }
            for student in queryset
        ]
        
        # Рассчитываем распределение задолженностей
        debt_distribution = self.get_debt_distribution(queryset)
        
        # Рассчитываем средние значения по группам
        group_averages = self.calculate_group_stats(queryset)
        
        # Формируем ответ
        response_data = {
            "debtsDistribution": {
                "0": debt_distribution['zero_debts'] or 0,
                "1": debt_distribution['one_debt'] or 0,
                "2": debt_distribution['two_debts'] or 0,
                "3plus": debt_distribution['three_plus_debts'] or 0
            },
            "groupAverages": group_averages,
            "students": students_data
        }
        
        return Response(response_data)


class AcademicReturnsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet для получения статистики по возвратам из академических отпусков.
    
    Назначение:
    - Предоставляет API endpoint для получения статистики по студентам, 
      находящимся в академических отпусках
    - Анализирует статусы студентов (возвращены, отчислены, продолжают обучение)
    - Формирует отчет с распределением по статусам и детализацией по студентам
    
    Входные параметры:
    - Стандартные параметры DRF (пагинация, фильтрация)
    - Возможность фильтрации через backend filters (если настроены)
    
    Выходные данные:
    - JSON объект с двумя основными разделами:
      1. statusDistribution - статистика по статусам студентов
      2. students - детальная информация по студентам с завершенными отпусками
    """
    # Добавляем обязательный queryset
    queryset = Academ.objects.none()
    
    def get_queryset(self):
        """
        Получает базовый queryset с выборкой всех записей об академотпусках.
        
        Возвращает:
        - QuerySet: Все записи об академических отпусках с предзагрузкой 
          связанных данных через select_related 
        
        Оптимизированные связи:
        - student → основная информация о студенте
        - student__group → текущая группа студента
        - previous_group → предыдущая группа (до академа)
        - relevant_group → актуальная группа для возврата
        """
        return Academ.objects.select_related(
            'student',
            'student__group',
            'previous_group',
            'relevant_group'
        ).all()
    
    def determine_status(self, academ):
        """
        Определяет текущий статус студента на основе данных об академическом отпуске.
        
        Параметры:
        - academ: объект модели Academ - запись об академическом отпуске
        
        Возвращает:
        - str: текстовое описание статуса студента:
          * "Продолжает обучение" - если отпуск еще продолжается или нет даты окончания
          * "Возвращён" - если отпуск завершен и студент прикреплен к группе
          * "Отчислен" - если отпуск завершен, но студент не прикреплен к группе
        
        Логика определения:
        1. Если нет даты окончания отпуска → статус "Продолжает обучение"
        2. Если дата окончания прошла:
           - Есть текущая группа → "Возвращён"
           - Нет текущей группы → "Отчислен"
        3. Если дата окончания еще не наступила → "Продолжает обучение"
        """
        if not academ.end_date:
            return "Продолжает обучение"
        
        if academ.end_date < timezone.now().date():
            if academ.student.group:
                return "Возвращён"
            else:
                return "Отчислен"
        return "Продолжает обучение"
    
    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения статистики по возвратам.
        
        Входные параметры:
        - request: HTTP-запрос (может содержать параметры фильтрации)
        
        Выходные данные:
        - Response: JSON объект с структурой:
          {
            "statusDistribution": {
                "Отчислен": int,
                "Возвращён": int, 
                "Продолжает обучение": int
            },
            "students": [
                {
                    "id": int,           # ID студента
                    "name": str,         # ФИО студента
                    "group": str,        # Название группы
                    "returnDate": str,   # Дата возврата (YYYY-MM-DD)
                    "status": str        # Статус студента
                },
                ...
            ]
          }
        
        Особенности:
        - В раздел students включаются только записи с заполненной датой окончания отпуска
        - Студенты сортируются по дате возврата (сначала новые)
        - Используется фильтрация через DRF filters (если настроены)
        """
        # Получаем отфильтрованный queryset
        academ_records = self.filter_queryset(self.get_queryset())
        
        # Подготовка данных
        status_counts = {
            "Отчислен": 0,
            "Возвращён": 0,
            "Продолжает обучение": 0
        }
        
        students_data = []
        
        for academ in academ_records:
            status = self.determine_status(academ)
            status_counts[status] += 1
            
            # Добавляем в список только завершенные отпуска (с датой окончания)
            if academ.end_date:
                students_data.append({
                    "id": academ.student.student_id,
                    "name": academ.student.name,
                    "group": academ.relevant_group.title if academ.relevant_group else 
                            (academ.student.group.title if academ.student.group else None),
                    "returnDate": academ.end_date.strftime("%Y-%m-%d"),
                    "status": status
                })
        
        # Сортируем студентов по дате возвращения (новые сверху)
        students_data.sort(key=lambda x: x["returnDate"], reverse=True)
        
        return Response({
            "statusDistribution": status_counts,
            "students": students_data
        })


class SubjectStatisticsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    ViewSet для получения статистики по успеваемости по предметам.
    
    Назначение:
    - Предоставляет API endpoint для анализа успеваемости студентов по предметам
    - Формирует статистику оценок, распределение по баллам и топ предметов
    - Поддерживает фильтрацию по курсу, семестру, группам и названию предмета
    
    Входные параметры (query parameters):
    - course: номер курса (целое число, опционально)
    - semester: номер семестра (целое число, опционально)
    - subject: название предмета (строка, частичное совпадение, опционально)
    - groups: список групп через запятую (строка, опционально)
    - sortBy: критерий сортировки топ-предметов ('avg', 'max', 'count')
    - limit: ограничение количества топ-предметов (целое число, по умолчанию 5)
    
    Выходные данные:
    - JSON объект с тремя основными разделами:
      1. subjectStats - общая статистика по выбранным оценкам
      2. gradeDistributionBar - распределение оценок по баллам
      3. bestSubjects - топ предметов по выбранному критерию
    """
    queryset = Grades.objects.select_related(
        'student', 
        'student__group', 
        'fc', 
        'fc__hps', 
        'fc__hps__disciple'
    )
    
    def calculate_course(self, year_of_admission: int) -> int:
        """
        Вычисляет текущий курс студента на основе года поступления.
        
        Параметры:
        - year_of_admission: int - год поступления студента
        
        Возвращает:
        - int: текущий курс студента
        
        Логика расчета:
        - Если текущий месяц до сентября: курс = текущий год - год поступления
        - Если текущий месяц сентябрь или later: курс = текущий год - год поступления + 1
        - Учитывает переход учебного года в сентябре
        """
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        if current_month < 9:
            return current_year - year_of_admission
        else:
            return current_year - year_of_admission + 1

    def extract_year_from_group_title(self, title: str) -> int | None:
        """
        Извлекает год поступления из названия группы.
        
        Параметры:
        - title: str - название группы (формат: "XXX-YYZZ", где YY - год)
        
        Возвращает:
        - int | None: год поступления или None при ошибке парсинга
        
        Логика работы:
        - Разделяет строку по дефису и берет вторую часть
        - Извлекает первые две цифры как год
        - Определяет век (2000 или 1900) на основе текущего года
        - Пример: "ФИТ-21Б" → 2021 год
        """
        try:
            parts = title.split('-')
            year_suffix = int(parts[1][:2])  # Берем только первые две цифры (например, из "21Б" берем 21)
            current_year = datetime.now().year % 100
            century = 2000 if year_suffix <= current_year else 1900
            return century + year_suffix
        except (IndexError, ValueError, AttributeError):
            return None

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения статистики по предметам.
        
        Входные параметры (query parameters):
        - course: int - фильтр по курсу (опционально)
        - semester: int - фильтр по семестру (опционально)
        - subject: str - фильтр по названию предмета (частичное совпадение, опционально)
        - groups: str - список групп через запятую (опционально)
        - sortBy: str - критерий сортировки топ-предметов ('avg', 'max', 'count')
        - limit: int - количество топ-предметов в результате (по умолчанию 5)
        
        Выходные данные:
        - Response: JSON объект со структурой:
          {
            "subjectStats": {
                "minGrade": float,  # Минимальная оценка
                "avgGrade": float,  # Средняя оценка
                "maxGrade": float   # Максимальная оценка
            },
            "gradeDistributionBar": {
                "2": int,  # Количество двоек
                "3": int,  # Количество троек
                "4": int,  # Количество четверок
                "5": int   # Количество пятерок
            },
            "bestSubjects": [
                {
                    "subject": str,        # Название предмета
                    "avg": float,          # Средняя оценка
                    "max": int,            # Максимальная оценка
                    "count": int,          # Количество оценок
                    "avgAttendance": float, # Средняя посещаемость
                    "avgActivity": None    # Средняя активность
                },
                ...
            ]
          }
        
        Особенности реализации:
        - Валидация соответствия курса и семестра
        - Обработка ошибок парсинга параметров
        - Сортировка топ-предметов по выбранному критерию
        """
        # Получаем параметры запроса
        course_param = request.query_params.get('course')
        semester_param = request.query_params.get('semester')
        subject_name = request.query_params.get('subject')
        groups = request.query_params.get('groups', '').split(',')
        sort_by = request.query_params.get('sortBy', 'avg')
        limit = int(request.query_params.get('limit', 5))

        # Преобразуем параметры в нужные типы
        try:
            course_param = int(course_param) if course_param else None
        except ValueError:
            course_param = None

        try:
            semester_param = int(semester_param) if semester_param else None
        except ValueError:
            semester_param = None

        # Проверка соответствия курса и семестра
        if course_param is not None and semester_param is not None:
            valid_semesters = [
                (course_param - 1) * 2 + 1,
                (course_param - 1) * 2 + 2
            ]
            if semester_param not in valid_semesters:
                return Response({
                    "subjectStats": {"minGrade": None, "avgGrade": None, "maxGrade": None},
                    "gradeDistributionBar": {"2": 0, "3": 0, "4": 0, "5": 0},
                    "bestSubjects": []
                }, status=status.HTTP_200_OK)

        # Базовый запрос
        queryset = Grades.objects.select_related(
            'student__group', 
            'fc__hps__disciple'
        )
        
        # 1. Фильтр по группе
        if groups and groups[0]:
            queryset = queryset.filter(student__group__title__in=groups)
        
        # 2. Фильтр по курсу (если нужен)
        if course_param:
            # Реализуйте ваш метод фильтрации по курсу
            pass
        
        # 3. Фильтр по семестру
        if semester_param:
            queryset = queryset.filter(fc__hps__semester=semester_param)
        
        # 4. Фильтр по предмету
        if subject_name:
            queryset = queryset.filter(fc__hps__disciple__disciple_name__icontains=subject_name)

        # Преобразуем оценки в числовой формат для вычислений
        annotated_queryset = queryset.annotate(
            grade_int=Case(
                When(grade='2', then=Value(2)),
                When(grade='3', then=Value(3)),
                When(grade='4', then=Value(4)),
                When(grade='5', then=Value(5)),
                default=Value(None),
                output_field=IntegerField()
            )
        )

        # Статистика для выбранного предмета
        subject_stats = annotated_queryset.aggregate(
            min_grade=Min('grade_int'),
            avg_grade=Avg('grade_int'),
            max_grade=Max('grade_int')
        )

        # Распределение оценок (2, 3, 4, 5)
        grade_distribution = annotated_queryset.values('grade') \
            .annotate(count=Count('grade')) \
            .order_by('grade')

        grade_distribution_bar = {
            '2': 0, '3': 0, '4': 0, '5': 0
        }
        for grade in grade_distribution:
            if grade['grade'] in ['2', '3', '4', '5']:
                grade_distribution_bar[grade['grade']] = grade['count']

        # Топ предметов по выбранному критерию (avg, max, count)
        # Сначала определяем поле для сортировки
        sort_field_map = {
            'avg': 'avg_grade',
            'max': 'max_grade',
            'count': 'count'
        }
        sort_field = sort_field_map.get(sort_by, 'avg_grade')

        top_subjects = (
            annotated_queryset
            .filter(grade_int__isnull=False)  # Только предметы с оценками
            .values('fc__hps__disciple__disciple_name')
            .annotate(
                avg_grade=Avg('grade_int'),
                max_grade=Max('grade_int'),
                count=Count('grade_int'),
                # avg_attendance=Avg('student__attendance__percent_of_attendance')
                avg_attendance=Avg(
                    'student__attendance__percent_of_attendance',
                    filter=Q(student__attendance__nagruzka__fc=F('fc'))
                )
            )
            .order_by('-' + sort_field)
            .exclude(avg_grade__isnull=True)  # Исключаем предметы без оценок
            [:limit]
        )

        # Формирование ответа
        response_data = {
            "subjectStats": {
                "minGrade": subject_stats['min_grade'],
                "avgGrade": subject_stats['avg_grade'],
                "maxGrade": subject_stats['max_grade']
            },
            "gradeDistributionBar": grade_distribution_bar,
            "bestSubjects": []
        }

        for subject in top_subjects:
            response_data["bestSubjects"].append({
                "subject": subject['fc__hps__disciple__disciple_name'],
                "avg": subject['avg_grade'],
                "max": subject['max_grade'],
                "count": subject['count'],
                "avgAttendance": subject.get('avg_attendance'),  # Может быть None
                "avgActivity": None  # Заглушка, как просили
            })

        return Response(response_data, status=status.HTTP_200_OK)
    
class StudentRatingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet для получения рейтинга студентов с комплексной оценкой успеваемости.
    
    Назначение:
    - Предоставляет API endpoint для рейтинговой системы студентов
    - Рассчитывает комплексный рейтинг на основе оценок, активности и посещаемости
    - Формирует данные для визуализации (графиков) и детализированный список студентов
    
    Входные параметры (query parameters):
    - course: номер курса (целое число, опционально)
    - group: название группы (строка, точное совпадение, опционально)
    - subject: название предмета (строка, частичное совпадение, опционально)
    - sortBy: критерий сортировки ('rating', 'performance', 'attendance', 'activity')
    - limit: количество студентов в результате (целое число, по умолчанию 10)
    
    Выходные данные:
    - JSON объект с двумя основными разделами:
      1. chartData - упрощенные данные для построения графиков
      2. students - детализированная информация по студентам
    """
    queryset = Student.objects.all().select_related('group')
    
    def calculate_course(self, year_of_admission: int) -> int:
        """
        Вычисляет текущий курс студента на основе года поступления.
        
        Параметры:
        - year_of_admission: int - год поступления студента
        
        Возвращает:
        - int: текущий курс студента
        
        Логика расчета:
        - Если текущий месяц сентябрь или позднее: прибавляется 1 к разнице лет
        - Если текущий месяц до сентября: используется простая разница лет
        - Пример: поступление в 2021, сейчас октябрь 2024 → 4 курс
        """
        now = datetime.now()
        return now.year - year_of_admission + (1 if now.month >= 9 else 0)

    def extract_year_from_group_title(self, title: str) -> int | None:
        """
        Извлекает год поступления из названия группы.
        
        Параметры:
        - title: str - название группы (ожидается формат с дефисом, например "ФИТ-21Б")
        
        Возвращает:
        - int | None: год поступления или None при ошибке парсинга
        
        Логика работы:
        - Разделяет название по дефису и берет вторую часть
        - Извлекает первые две цифры как год
        - Определяет век (2000 или 1900) на основе сравнения с текущим годом
        - Обрабатывает исключения для некорректных форматов
        """
        try:
            parts = title.split('-')
            year_suffix = int(parts[1][:2])
            current_year = datetime.now().year % 100
            century = 2000 if year_suffix <= current_year else 1900
            return century + year_suffix
        except Exception:
            return None

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения рейтинга студентов.
        
        Входные параметры:
        - course: int - фильтр по курсу (опционально)
        - group: str - фильтр по названию группы (точное совпадение, опционально)
        - subject: str - фильтр по предмету (частичное совпадение, опционально)
        - sortBy: str - критерий сортировки:
            * 'rating' - по комплексному рейтингу (по умолчанию)
            * 'performance' - по среднему баллу
            * 'attendance' - по посещаемости
            * 'activity' - по активности
        - limit: int - количество возвращаемых студентов (по умолчанию 10)
        
        Выходные данные:
        - Response: JSON объект со структурой:
          {
            "chartData": [
                {
                    "name": str,           # ФИО студента
                    "avgGrade": float,     # Средний балл (округленный до 2 знаков)
                    "activity": float,     # Уровень активности
                    "attendancePercent": float  # Процент посещаемости
                },
                ...
            ],
            "students": [
                {
                    "id": int,             # ID студента
                    "name": str,           # ФИО студента
                    "group": str,          # Название группы
                    "course": int,         # Текущий курс
                    "avgGrade": float,     # Средний балл
                    "activity": float,     # Уровень активности
                    "attendancePercent": float,  # Процент посещаемости
                    "dropoutRisk": float,  # Риск отчисления (заглушка - 0.25)
                    "rating": float        # Комплексный рейтинг
                },
                ...
            ]
          }
        
        Особенности реализации:
        - Комплексный рейтинг рассчитывается по формуле: 
          (avg_grade × 0.5 + activity × 0.3 + attendance × 0.2) × 20
        - Фильтрация по курсу осуществляется через анализ названия группы
        - Используются аннотации Django ORM для вычислений в БД
        - Поддержка сортировки по различным критериям
        - Обработка граничных случаев и ошибок ввода
        """
        # Параметры
        course = request.query_params.get('course')
        group = request.query_params.get('group')
        subject = request.query_params.get('subject')
        sort_by = request.query_params.get('sortBy', 'calculated_rating')
        limit = int(request.query_params.get('limit', 10) or 10)

        qs = self.get_queryset()
        
        # Фильтрация по группе
        if group:
            qs = qs.filter(group__title=group)
            
        # Фильтрация по курсу
        if course:
            try:
                c = int(course)
                valid_ids = []
                for s in qs:
                    year = self.extract_year_from_group_title(s.group.title) if s.group else None
                    if year and self.calculate_course(year) == c:
                        valid_ids.append(s.student_id)
                qs = qs.filter(student_id__in=valid_ids)
            except ValueError:
                pass
                
        # Фильтрация по предмету
        if subject:
            qs = qs.filter(
                grades__fc__hps__disciple__disciple_name__icontains=subject
            )

        # Аннотация полей
        grade_case = Case(
            When(grades__grade='2', then=Value(2)),
            When(grades__grade='3', then=Value(3)),
            When(grades__grade='4', then=Value(4)),
            When(grades__grade='5', then=Value(5)),
            default=Value(None),
            output_field=IntegerField()
        )
        
        qs = qs.annotate(
            avg_grade=Avg(grade_case),
            attendance_percent=Avg('attendance__percent_of_attendance'),
            avg_activity=F('practise')  # Используем поле practise как активность
        ).annotate(
            calculated_rating=ExpressionWrapper(
                (F('avg_grade') * 0.5 + F('avg_activity') * 0.3 + F('attendance_percent') * 0.2) * 20,
                output_field=FloatField()
            )
        )

        # Сопоставление sortBy → поля
        sort_field_map = {
            'rating': 'calculated_rating',
            'performance': 'avg_grade',
            'attendance': 'attendance_percent',
            'activity': 'avg_activity'
        }
        field = sort_field_map.get(sort_by, 'calculated_rating')
        
        # Сортировка и ограничение
        qs = qs.order_by(f'-{field}')[:limit]

        # Формируем ответ
        chartData = [{
            'name': s.name,
            'avgGrade': round(float(s.avg_grade or 0), 2),
            'activity': round(float(s.avg_activity or 0), 2),
            'attendancePercent': round(float(s.attendance_percent or 0), 2)
        } for s in qs]

        students = [{
            'id': s.student_id,
            'name': s.name,
            'group': s.group.title if s.group else None,
            'course': (
                self.calculate_course(
                    self.extract_year_from_group_title(s.group.title) or 0
                ) if s.group else None
            ),
            'avgGrade': round(float(s.avg_grade or 0), 2),
            'activity': round(float(s.avg_activity or 0), 2),
            'attendancePercent': round(float(s.attendance_percent or 0), 2),
            'dropoutRisk': 0.25,  # Заглушка - фиксированные 25% для всех
            'rating': round(float(s.calculated_rating or 0), 2)
        } for s in qs]

        return Response({
            'chartData': chartData,
            'students': students
        }, status=status.HTTP_200_OK)
    
class TrainModelViewSet(viewsets.ViewSet):
    """
    ViewSet для запуска обучения ML-модели аналитики студентов.
    
    Назначение:
    - Предоставляет API endpoint для запуска процесса обучения модели
    - Вызывает Django management command для генерации предсказаний
    - Сохраняет результаты анализа в CSV файл для последующего использования
    
    Требования:
    - Пользователь должен быть аутентифицирован (IsAuthenticated)
    - Должна существовать management command 'analytics'
    - Необходимы соответствующие права для выполнения команды
    
    Входные параметры:
    - Не требуются (GET запрос без параметров)
    
    Выходные данные:
    - Успех: сообщение об успешном выполнении
    - Ошибка: описание ошибки при выполнении команды
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Обрабатывает GET-запрос для запуска обучения модели.
        
        Входные параметры:
        - request: HTTP-запрос (без параметров)
        
        Выходные данные:
        - Response: JSON объект с результатом выполнения:
          Успех (200):
          {
            "message": "Модель успешно обучена, результаты сохранены в CSV."
          }
          
          Ошибка (500):
          {
            "error": "Описание ошибки"
          }
        
        Процесс работы:
        1. Вызывает management command 'analytics'
        2. Ожидает завершения процесса обучения модели
        3. Сохраняет результаты в CSV файл
        4. Возвращает статус выполнения
        
        Особенности:
        - Команда выполняется синхронно (блокирующе)
        - Требует значительных вычислительных ресурсов
        - Рекомендуется использовать для периодического переобучения модели
        """
        try:
            call_command('analytics')
            return Response(
                {"message": "Модель успешно обучена, результаты сохранены в CSV."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
                 
class StudentAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet для получения аналитики студента из предварительно сгенерированного CSV файла.
    
    Назначение:
    - Предоставляет API endpoint для доступа к результатам ML-аналитики
    - Читает данные из CSV файла, созданного командой 'analytics'
    - Фильтрует предметы по запросу для оптимизации ответа
    
    Входные параметры (query parameters):
    - student_id (обязательный) - идентификатор студента
    - subjects (опционально) - список предметов для фильтрации
    
    Требования:
    - Пользователь должен быть аутентифицирован
    - CSV файл должен быть предварительно сгенерирован через TrainModelViewSet
    - Файл должен находиться по указанному пути
    
    Выходные данные:
    - Детальная аналитическая информация по студенту
    - Успеваемость по предметам
    - Академические показатели
    """
    permission_classes = [IsAuthenticated]
    queryset = None  # Не требуется модель
    
    def get_csv_path(self):
        """
        Возвращает путь к CSV файлу с результатами аналитики.
        
        Возвращает:
        - str: абсолютный или относительный путь к файлу
        
        Расположение файла:
        - 'application/management/predictions_results.csv'
        - Файл генерируется management command 'analytics'
        """
        return 'application/management/predictions_results.csv'

    def read_csv_data(self):
        """
        Читает и кэширует данные из CSV файла.
        
        Возвращает:
        - list: список словарей с данными из CSV
        
        Исключения:
        - FileNotFoundError: если файл не существует
        - CSV parsing errors: при проблемах с форматом файла
        
        Особенности:
        - Использует кодировку UTF-8
        - Разделитель - точка с запятой (;)
        - Первая строка содержит заголовки
        """
        csv_path = self.get_csv_path()

        if not os.path.exists(csv_path):
            raise FileNotFoundError("Analytics file not generated yet")

        with open(csv_path, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f, delimiter=';'))  

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения аналитики студента.
        
        Входные параметры (query parameters):
        - student_id: str (обязательный) - ID студента
        - subjects: list (опционально) - список предметов для фильтрации
        
        Выходные данные:
        - Response: JSON объект со структурой:
          {
            "student_id": "12345",
            "name": "Иванов Иван Иванович",
            "age": 20,
            "group": "ФИТ-21Б",
            "speciality": "Информатика",
            "academic_info": {
                "certificate_score": 4.5,
                "entry_score": 85.5,
                "rating_score": 4.2,
                "diploma_grade": 4.7,
                "is_academic": false
            },
            "subjects": [
                {
                    "subject": "Математика",
                    "grade": "4.8"
                },
                {
                    "subject": "Программирование", 
                    "grade": "5.0"
                }
            ]
          }
        
        Коды ответов:
        - 200: Успешный запрос
        - 400: Отсутствует обязательный параметр student_id
        - 404: Файл не найден или студент не найден в файле
        - 500: Внутренняя ошибка сервера
        
        Логика работы:
        1. Проверка обязательного параметра student_id
        2. Чтение данных из CSV файла
        3. Поиск студента по ID
        4. Формирование структурированного ответа
        5. Фильтрация предметов по запросу (если указано)
        """
        student_id = request.query_params.get('student_id')
        subjects_filter = request.query_params.getlist('subjects', [])

        if not student_id:
            return Response(
                {"error": "Missing required parameter: student_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            csv_data = self.read_csv_data()
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        # Найдём строку нужного студента
        student_row = next((row for row in csv_data if row['Student_ID'] == student_id), None)

        if not student_row:
            return Response(
                {"error": f"Student with ID {student_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Отдельные ключи для основной информации
        core_fields = [
            'Speciality', 'Group_Name', 'Student_ID', 'Name', 'Age', 'Is_Academic',
            'Middle_value_of_sertificate', 'Entry_score', 'Rating_score', 'Diploma_grade'
        ]

        # Соберём информацию
        response_data = {
            "student_id": student_row["Student_ID"],
            "name": student_row["Name"],
            "age": int(student_row["Age"]),
            "group": student_row["Group_Name"],
            "speciality": student_row["Speciality"],
            "academic_info": {
                "certificate_score": float(student_row["Middle_value_of_sertificate"]),
                "entry_score": float(student_row["Entry_score"]),
                "rating_score": float(student_row["Rating_score"]),
                "diploma_grade": float(student_row["Diploma_grade"]),
                "is_academic": bool(int(student_row["Is_Academic"]))
            },
            "subjects": []
        }

        # Отбор предметов: все поля, кроме core_fields
        for subject, grade in student_row.items():
            if subject not in core_fields:
                if not subjects_filter or subject in subjects_filter:
                    response_data["subjects"].append({
                        "subject": subject,
                        "grade": grade
                    })

        return Response(response_data)
