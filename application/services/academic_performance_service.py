from collections import defaultdict
from django.db.models import Q, Count
from application.models import Student, StudentResult, StudentGroup

class AcademicPerformanceService:
    @staticmethod
    def get_debts_filter():
        return Q(studentresult__result__result_value__in=['2', 'Н/Я', 'Не зачтено'])

    @classmethod
    def get_queryset(cls):
        """Студентов с количеством долгов."""
        return Student.objects.select_related('group').filter(
            is_academic=False
        ).annotate(
            debt_count=Count('studentresult', filter=cls.get_debts_filter())
        ).order_by('student_id')

    @classmethod
    def apply_filters(cls, queryset, group: str = None, search: str = None):
        if group:
            queryset = queryset.filter(group__name=group)
        if search:
            try:
                student_id = int(search)
                queryset = queryset.filter(student_id=student_id)
            except ValueError:
                # Поиск по названию группы
                queryset = queryset.filter(group__name__icontains=search)
        return queryset

    @classmethod
    def get_debt_distribution(cls, students):
        """Распределение студентов по количеству долгов."""
        dist = {
            'zero_debts': 0,
            'one_debt': 0,
            'two_debts': 0,
            'three_plus_debts': 0
        }
        for student in students:
            c = student.debt_count
            if c == 0:
                dist['zero_debts'] += 1
            elif c == 1:
                dist['one_debt'] += 1
            elif c == 2:
                dist['two_debts'] += 1
            else:
                dist['three_plus_debts'] += 1
        return dist

    @classmethod
    def calculate_group_stats(cls, students):
        """Среднее количество долгов по группам."""
        # Группируем студентов по group_id
        groups = defaultdict(list)
        for s in students:
            if s.group_id:
                groups[s.group_id].append(s)

        if not groups:
            return []

        # Получаем названия групп
        group_ids = list(groups.keys())
        group_names = {
            g.group_id: g.name
            for g in StudentGroup.objects.filter(group_id__in=group_ids)
        }

        stats = []
        for gid, student_list in groups.items():
            total_debts = sum(s.debt_count for s in student_list)
            avg = total_debts / len(student_list)
            stats.append({
                "group": group_names.get(gid, f"Группа {gid}"),
                "avgDebts": round(float(avg), 1)
            })

        stats.sort(key=lambda x: x['group'])
        return stats

    @classmethod
    def get_student_debts_details(cls, student_id):
        """Детали долгов студента."""
        debts = StudentResult.objects.filter(
            student_id=student_id,
            result__result_value__in=['2', 'Н/Я', 'Не зачтено']
        ).select_related('discipline', 'result')
        return [
            {"discipline": d.discipline.name, "grade": d.result.result_value}
            for d in debts
        ]

    @classmethod
    def get_performance_data(cls, group: str = None, search: str = None):
        """Основной метод: возвращает полные данные для API."""
        queryset = cls.get_queryset()
        filtered_qs = cls.apply_filters(queryset, group=group, search=search)

        # Выполняем запрос один раз
        students = list(filtered_qs)

        # Подготавливаем данные
        students_data = []
        for s in students:
            students_data.append({
                "id": s.student_id,
                "group": s.group.name if s.group else None,
                "debts": s.debt_count,
                "debtsDetails": cls.get_student_debts_details(s.student_id)
            })

        debt_dist = cls.get_debt_distribution(students)
        group_averages = cls.calculate_group_stats(students)

        return {
            "debtsDistribution": {
                "0": debt_dist['zero_debts'],
                "1": debt_dist['one_debt'],
                "2": debt_dist['two_debts'],
                "3plus": debt_dist['three_plus_debts']
            },
            "groupAverages": group_averages,
            "students": students_data
        }