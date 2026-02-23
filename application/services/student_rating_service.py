from datetime import datetime
from typing import Optional, List, Dict, Any
from django.db.models import Q
from application.models import Student, StudentResult, Attendance


class StudentRatingService:
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
    def normalize_grade_value(result_value: str) -> Optional[int]:
        if not result_value:
            return None
        grade_clean = result_value.strip()
        if grade_clean in ["2", "3", "4", "5"]:
            return int(grade_clean)
        return None

    @classmethod
    def calculate_student_activity(cls, student_id: int) -> float:
        passed_subjects = StudentResult.objects.filter(
            student_id=student_id,
            result__result_value__in=['3', '4', '5', 'Зачтено']
        ).count()
        attendance_count = Attendance.objects.filter(student_id=student_id).count()
        activity_score = (passed_subjects * 0.6) + (attendance_count * 0.01 * 0.4)
        return min(activity_score / 10.0, 5.0)

    @classmethod
    def calculate_attendance_percent(cls, student_id: int) -> float:
        attended_lessons = Attendance.objects.filter(student_id=student_id).count()
        TOTAL_LESSONS = 60
        if TOTAL_LESSONS > 0:
            return min((attended_lessons / TOTAL_LESSONS) * 100, 100.0)
        return 0.0

    @classmethod
    def calculate_dropout_risk(cls, student_id: int, avg_grade: float, attendance_percent: float, activity: float) -> float:
        debt_count = StudentResult.objects.filter(
            student_id=student_id,
            result__result_value__in=['2', 'Н/Я', 'Не зачтено']
        ).count()
        debt_risk = min(debt_count / 5.0, 1.0)
        dropout_risk = (
            (1 - avg_grade / 5) * 0.4 +
            (1 - attendance_percent / 100) * 0.3 +
            (1 - activity / 5) * 0.1 +
            debt_risk * 0.2
        )
        return max(0, min(1, dropout_risk))

    @classmethod
    def get_student_debts_details(cls, student_id: int) -> List[Dict[str, str]]:
        debts = StudentResult.objects.filter(
            student_id=student_id,
            result__result_value__in=['2', 'Н/Я', 'Не зачтено']
        ).select_related('discipline', 'result')
        return [
            {
                "discipline": d.discipline.name,
                "grade": d.result.result_value,
                "type": cls.classify_debt_type(d.result.result_value)
            }
            for d in debts
        ]

    @staticmethod
    def classify_debt_type(grade_value: str) -> str:
        if grade_value == '2':
            return 'неуд'
        elif grade_value == 'Н/Я':
            return 'неявка'
        elif grade_value == 'Не зачтено':
            return 'незачет'
        return 'другой'

    @staticmethod
    def get_risk_level(risk_score: float) -> str:
        if risk_score < 0.3:
            return "низкий"
        elif risk_score < 0.7:
            return "средний"
        else:
            return "высокий"

    @classmethod
    def get_students_in_course(cls, course: int) -> List[int]:
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
    def get_rating_data(
        cls,
        course: Optional[int] = None,
        group: Optional[str] = None,
        subject: Optional[str] = None,
        sort_by: str = 'rating',
        limit: int = 10
    ) -> Dict[str, Any]:
        qs = Student.objects.select_related('group').filter(is_academic=False)

        # Фильтр по группе
        if group:
            qs = qs.filter(group__name=group)

        # Фильтр по курсу
        if course is not None:
            valid_ids = cls.get_students_in_course(course)
            qs = qs.filter(student_id__in=valid_ids)

        # Фильтр по предмету
        if subject:
            student_ids = StudentResult.objects.filter(
                discipline__name__icontains=subject
            ).values_list('student_id', flat=True).distinct()
            qs = qs.filter(student_id__in=student_ids)

        # Сбор данных
        students_data = []
        for student in qs:
            # Средний балл
            numeric_grades = []
            results = StudentResult.objects.filter(student=student).select_related('result')
            for result in results:
                grade_val = cls.normalize_grade_value(result.result.result_value)
                if grade_val and 2 <= grade_val <= 5:
                    numeric_grades.append(grade_val)
            avg_grade = sum(numeric_grades) / len(numeric_grades) if numeric_grades else 0

            # Активность и посещаемость
            activity = cls.calculate_student_activity(student.student_id)
            attendance_percent = cls.calculate_attendance_percent(student.student_id)

            # Рейтинг
            rating = (avg_grade * 0.5 + activity * 0.3 + (attendance_percent / 20) * 0.2) * 20

            # Курс
            course_num = None
            if student.group and student.group.name:
                year = cls.extract_year_from_group_name(student.group.name)
                if year is not None:
                    course_num = cls.calculate_course(year)

            students_data.append({
                'student': student,
                'avg_grade': avg_grade,
                'activity': activity,
                'attendance_percent': attendance_percent,
                'rating': rating,
                'course': course_num
            })

        # Сортировка
        sort_field_map = {
            'rating': 'rating',
            'performance': 'avg_grade',
            'attendance': 'attendance_percent',
            'activity': 'activity'
        }
        sort_key = sort_field_map.get(sort_by, 'rating')
        students_data.sort(key=lambda x: x[sort_key], reverse=True)
        students_data = students_data[:limit]

        chart_data = []
        students_response = []

        for data in students_data:
            student = data['student']
            dropout_risk = cls.calculate_dropout_risk(
                student.student_id,
                data['avg_grade'],
                data['attendance_percent'],
                data['activity']
            )
            debts_details = cls.get_student_debts_details(student.student_id)
            debt_count = len(debts_details)

            chart_data.append({
                'name': f"Студент {student.student_id}",
                'avgGrade': round(data['avg_grade'], 2),
                'activity': round(data['activity'], 2),
                'attendancePercent': round(data['attendance_percent'], 2)
            })

            students_response.append({
                'id': student.student_id,
                'name': f"Студент {student.student_id}",
                'group': student.group.name if student.group else None,
                'course': data['course'],
                'avgGrade': round(data['avg_grade'], 2),
                'activity': round(data['activity'], 2),
                'attendancePercent': round(data['attendance_percent'], 2),
                'debtCount': debt_count,
                'debtsDetails': debts_details,
                'dropoutRisk': round(dropout_risk, 2),
                'rating': round(data['rating'], 2),
                'riskLevel': cls.get_risk_level(dropout_risk)
            })

        return {
            'chartData': chart_data,
            'students': students_response
        }