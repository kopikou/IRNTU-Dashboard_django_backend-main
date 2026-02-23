from collections import defaultdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from django.db.models import Count
from application.models import Student, StudentResult, Discipline, Attendance


class SubjectStatisticsService:
    @staticmethod
    def calculate_course(year_of_admission: int) -> int:
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        if current_month < 9:
            return current_year - year_of_admission
        else:
            return current_year - year_of_admission + 1

    @staticmethod
    def extract_year_from_group_name(name: str) -> Optional[int]:
        try:
            parts = name.split('-')
            if len(parts) < 2:
                return None
            year_part = parts[1][:2]
            year_suffix = int(year_part)
            current_year = datetime.now().year % 100
            century = 2000 if year_suffix <= current_year else 1900
            return century + year_suffix
        except (IndexError, ValueError, AttributeError):
            return None

    @staticmethod
    def normalize_grade_value(result_value: str):
        if not result_value:
            return None
        grade_clean = result_value.strip()
        if grade_clean in ["2", "3", "4", "5"]:
            return int(grade_clean)
        elif grade_clean == "Зачтено":
            return "зачет"
        elif grade_clean == "Не зачтено":
            return "незачет"
        elif grade_clean == "Н/Я":
            return "неявка"
        return None

    @classmethod
    def get_students_in_course(cls, course: int) -> List[int]:
        """Возвращает список student_id студентов на указанном курсе"""
        student_ids = []
        students = Student.objects.select_related('group').filter(is_academic=False)
        for student in students:
            if student.group and student.group.name:
                year = cls.extract_year_from_group_name(student.group.name)
                if year is not None:
                    student_course = cls.calculate_course(year)
                    if student_course == course:
                        student_ids.append(student.student_id)
        return student_ids

    @classmethod
    def get_attendance_percent_for_discipline(cls, discipline_id: int, student_ids: List[int]) -> float:
        """Рассчитывает средний процент посещаемости по предмету."""
        if not student_ids:
            return 0.0

        stats = Attendance.objects.filter(
            discipline_id=discipline_id,
            student_id__in=student_ids
        ).aggregate(
            unique_lessons=Count('lesson_id', distinct=True),
            unique_students=Count('student_id', distinct=True)
        )

        unique_lessons = stats['unique_lessons'] or 0
        unique_students = stats['unique_students'] or 0

        if unique_students == 0 or unique_lessons == 0:
            return 0.0

        avg_lessons_per_student = unique_lessons / unique_students
        NORMALIZATION_FACTOR = 8
        attendance_percent = min((avg_lessons_per_student / NORMALIZATION_FACTOR) * 100, 100)
        return round(attendance_percent, 2)

    @classmethod
    def get_statistics(
        cls,
        course: Optional[int] = None,
        subject: Optional[str] = None,
        groups: Optional[List[str]] = None,
        sort_by: str = 'avg',
        limit: int = 5
    ) -> Dict[str, Any]:
        results_qs = StudentResult.objects.select_related(
            'student__group', 'discipline', 'result'
        ).filter(student__is_academic=False)

        # Фильтр по группам
        if groups:
            results_qs = results_qs.filter(student__group__name__in=groups)

        # Фильтр по курсу
        if course is not None:
            student_ids = cls.get_students_in_course(course)
            if not student_ids:
                return cls._empty_response()
            results_qs = results_qs.filter(student_id__in=student_ids)

        # Фильтр по предмету
        if subject:
            results_qs = results_qs.filter(discipline__name__icontains=subject)

        # Сбор данных
        numeric_grades = []
        grade_distribution_bar = {'2': 0, '3': 0, '4': 0, '5': 0}
        subject_data = defaultdict(lambda: {
            'grades': [],
            'name': None,
            'student_ids': set()
        })

        for result in results_qs:
            discipline = result.discipline
            result_value = result.result.result_value if result.result else None
            normalized = cls.normalize_grade_value(result_value)
            if normalized is None:
                continue

            disc_id = discipline.discipline_id
            subject_data[disc_id]['name'] = discipline.name
            subject_data[disc_id]['student_ids'].add(result.student.student_id)

            if isinstance(normalized, int) and 2 <= normalized <= 5:
                numeric_grades.append(normalized)
                grade_distribution_bar[str(normalized)] += 1
                subject_data[disc_id]['grades'].append(normalized)

        # Общая статистика
        if numeric_grades:
            subject_stats = {
                "minGrade": min(numeric_grades),
                "avgGrade": round(sum(numeric_grades) / len(numeric_grades), 2),
                "maxGrade": max(numeric_grades)
            }
        else:
            subject_stats = {"minGrade": None, "avgGrade": None, "maxGrade": None}

        # Топ предметов
        best_subjects_data = []
        for disc_id, data in subject_data.items():
            grades = data['grades']
            if not grades:
                continue
            avg_grade = sum(grades) / len(grades)
            best_subjects_data.append({
                'name': data['name'],
                'avg': round(avg_grade, 2),
                'max': max(grades),
                'count': len(grades),
                'avg_attendance': cls.get_attendance_percent_for_discipline(
                    disc_id, list(data['student_ids'])
                )
            })

        # Сортировка
        sort_field = {'avg': 'avg', 'max': 'max', 'count': 'count'}.get(sort_by, 'avg')
        best_subjects_data.sort(key=lambda x: x[sort_field], reverse=True)
        top_subjects = best_subjects_data[:limit]

        best_subjects_response = [
            {
                "subject": s['name'],
                "avg": s['avg'],
                "max": s['max'],
                "count": s['count'],
                "avgAttendance": s['avg_attendance'],
                "avgActivity": None  
            }
            for s in top_subjects
        ]

        return {
            "subjectStats": subject_stats,
            "gradeDistributionBar": grade_distribution_bar,
            "bestSubjects": best_subjects_response
        }

    @staticmethod
    def _empty_response() -> Dict[str, Any]:
        return {
            "subjectStats": {"minGrade": None, "avgGrade": None, "maxGrade": None},
            "gradeDistributionBar": {'2': 0, '3': 0, '4': 0, '5': 0},
            "bestSubjects": []
        }