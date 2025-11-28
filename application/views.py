# from django.shortcuts import render
# from rest_framework.generics import DestroyAPIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.response import Response
# from rest_framework.generics import ListAPIView
# from rest_framework.views import APIView
# from .permissions import IsStaffOrSuperUser
# from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
# from rest_framework.permissions import AllowAny
# from django.contrib.auth import authenticate
# from rest_framework.generics import get_object_or_404


# # Authentification serializers
# from app.serializers import LoginSerializer, RegisterSerializer
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.viewsets import ModelViewSet

# # For analytics
# import pandas as pd
# import numpy as np
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import accuracy_score
# from rest_framework import status

# from .models import Academ, Attendance, CourseProjects, DebtAudit, Debts, Diploma, Disciples, EducationPlan, FormControl, Grades, Group, HoursPerSemest, Nagruzka, Practise, PractiseType, Rating, RatingType, Specialty, Student, Teachers
# from app.serializers import AcademSerializer, AttendanceSerializer, CourseProjectsSerializer, DebtAuditSerializer, DebtsSerializer, DiplomaSerializer, DisciplesSerializer, EducationPlanSerializer, FormControlSerializer, GradesSerializer, GroupSerializer, HoursPerSemestSerializer, NagruzkaSerializer, PractiseSerializer, PractiseTypeSerializer, RatingSerializer, RatingTypeSerializer, SpecialtySerializer, StudentSerializer, TeachersSerializer


# import logging

# from django.views.decorators.csrf import csrf_exempt #добавила
# from django.utils.decorators import method_decorator  #добавила


# logger = logging.getLogger(__name__)

# class CheckPermissionsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({
#             "permissions": list(request.user.get_all_permissions())
#         })
      
      
# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Administrator created successfully!'}, status=201)
#         return Response(serializer.errors, status=400)

# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     @method_decorator(csrf_exempt) # добавила
#     def dispatch(self, *args, **kwargs): # добавила
#         return super().dispatch(*args, **kwargs)

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
#             if user:
#                 refresh = RefreshToken.for_user(user)
#                 access_token = str(refresh.access_token)

#                 # Создаём response и добавляем HTTPOnly Cookie
#                 response = Response({
#                     'refresh': str(refresh),
#                     'access': access_token
#                 })
#                 response.set_cookie(
#                     key="access_token", 
#                     value=access_token, 
#                     httponly=True,
#                     samesite='Lax',
#                     secure=False  # todo включить True, если используется HTTPS
#                 )
#                 return response

#             return Response({"error": "Неверные данные"}, status=401)
#         return Response(serializer.errors, status=400)


# class HelloWorldAPIView(APIView):
#     def get(self, request):
#         return Response({"message": "Hello, World!"})

# #######################################################################################################
# class AcademListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         academ = Academ.objects.all()
#         serializer = AcademSerializer(academ, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class AttendanceListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         attendance = Attendance.objects.all()
#         serializer = AttendanceSerializer(attendance, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class CourseProjectsListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         course_projects = CourseProjects.objects.all()
#         serializer = CourseProjectsSerializer(course_projects, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class DebtAuditListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         debt_audit = DebtAudit.objects.all()
#         serializer = DebtAuditSerializer(debt_audit, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class DebtsListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         debts = Debts.objects.all()
#         serializer = DebtsSerializer(debts, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class DiplomaListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         diploma = Diploma.objects.all()
#         serializer = DiplomaSerializer(diploma, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class DisciplesListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         disciples = Disciples.objects.all()
#         serializer = DisciplesSerializer(disciples, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class EducationPlanListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         education_plan = EducationPlan.objects.all()
#         serializer = EducationPlanSerializer(education_plan, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class FormControlListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         form_control = FormControl.objects.all()
#         serializer = FormControlSerializer(form_control, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class GradesListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         grades = Grades.objects.all()
#         serializer = GradesSerializer(grades, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class GroupListView(APIView):    
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         groups = Group.objects.all()
#         serializer = GroupSerializer(groups, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()
    
# class GroupIDView(APIView):#Для вывода по ID
#     permission_classes = [IsStaffOrSuperUser]

#     def get(self, request, group_id):
#         group = get_object_or_404(Group, group_id=group_id) 
#         serializer = GroupSerializer(group)
#         return Response(serializer.data)

# class HoursPerSemestListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         hours_per_semest = HoursPerSemest.objects.all()
#         serializer = HoursPerSemestSerializer(hours_per_semest, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class NagruzkaListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         nagruzka = Nagruzka.objects.all()
#         serializer = NagruzkaSerializer(nagruzka, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class PractiseListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         practise = Practise.objects.all()
#         serializer = PractiseSerializer(practise, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class PractiseTypeListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         practise_type = PractiseType.objects.all()
#         serializer = PractiseTypeSerializer(practise_type, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class RatingListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         rating = Rating.objects.all()
#         serializer = RatingSerializer(rating, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class RatingTypeListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         rating_type = RatingType.objects.all()
#         serializer = RatingTypeSerializer(rating_type, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class SpecialtyListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         specialty = Specialty.objects.all()
#         serializer = SpecialtySerializer(specialty, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()

# class StudentListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         students = Student.objects.all()
#         serializer = StudentSerializer(students, many=True)
#         return Response(serializer.data)
    
#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()
    
# class StudentIDView(APIView):#Для вывода по ID
#     permission_classes = [IsStaffOrSuperUser]

#     def get(self, request, student_id):
#         student = get_object_or_404(Student, student_id=student_id) 
#         serializer = StudentSerializer(student)
#         return Response(serializer.data)
    
# class TeachersListView(APIView):
#     permission_classes = [IsStaffOrSuperUser]
#     def get(self, request):
#         teachers = Teachers.objects.all()
#         serializer = TeachersSerializer(teachers, many=True)
#         return Response(serializer.data)
    
#     # queryset = Teachers.objects.all()
#     # serializer_class = TeachersSerializer

#     def get_queryset(self):
#         user = self.request.user
#         return super().get_queryset()
    
# class TeachersIDView(APIView):
#     permission_classes = [IsStaffOrSuperUser]

#     def get(self, request, teacher_id):
#         teacher = get_object_or_404(Teachers, teacher_id=teacher_id) 
#         serializer = TeachersSerializer(teacher)
#         return Response(serializer.data)
# #######################################################################################################

# class AnalyticsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             file_path = 'application/media/Testovaya_vygruzka.xlsx'

#             df = pd.read_excel(file_path)

#             df_cleaned = df.drop(columns=['ФИО', 'Страна_ПП', 'Регион_ПП', 'Город', 'ВидОбразования', 'Статус', 'status', 'Название_Спец', 'Факультет', 'Название', 'Название2'])

#             for column in df_cleaned.columns:
#                 if df_cleaned[column].dtype == np.number:
#                     df_cleaned[column].fillna(0, inplace=True)
#                 else:
#                     df_cleaned[column].fillna("не указано", inplace=True)

#             for column in df_cleaned.select_dtypes(include=[object]).columns:
#                 df_cleaned[column] = df_cleaned[column].astype(str)

#             for column in df_cleaned.select_dtypes(include=[bool]).columns:
#                 df_cleaned[column] = df_cleaned[column].astype(str)

#             numeric_features = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
#             categorical_features = df_cleaned.select_dtypes(include=[object]).columns.tolist()

#             preprocessor = ColumnTransformer(
#                 transformers=[
#                     ('num', StandardScaler(), numeric_features),
#                     ('cat', OneHotEncoder(), categorical_features)
#                 ])

#             pipeline = Pipeline(steps=[('preprocessor', preprocessor),
#                                        ('kmeans', KMeans(n_clusters=3, random_state=42))])

#             pipeline.fit(df_cleaned)
#             labels = pipeline.named_steps['kmeans'].labels_
#             df['Cluster'] = labels

#             df['Зачислен'] = df['Зачислен'].fillna(0)
#             df['Cluster'] = df['Cluster'].fillna(0)
#             df['Зачислен'] = df['Зачислен'].astype(int)
#             df['Cluster'] = df['Cluster'].astype(int)

#             df['Target'] = df['Зачислен'].apply(lambda x: 'Поступил' if x else 'Не поступил')

#             cluster_data = df.groupby(['Cluster', 'Target']).size().unstack(fill_value=0)

#             chart_data = {
#                 "clusters": cluster_data.index.tolist(),
#                 "поступил": cluster_data['Поступил'].tolist(),
#                 "не_поступил": cluster_data['Не поступил'].tolist()
#             }

#             accuracy = accuracy_score(df['Зачислен'], df['Cluster'])

#             return Response({
#                 "accuracy": accuracy,
#                 "chart_data": chart_data
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# views.py
from django.shortcuts import render
from rest_framework.generics import DestroyAPIView, ListAPIView, get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import pandas as pd
from .permissions import IsStaffOrSuperUser
from .models import (
    Administrator, Faculty, Speciality, StudentGroup, 
    Student, Discipline, ResultType, StudentResult, Attendance
)
from app.serializers import (
    LoginSerializer, RegisterSerializer,
    FacultySerializer, SpecialitySerializer, StudentGroupSerializer,
    StudentSerializer, DisciplineSerializer, ResultTypeSerializer, 
    StudentResultSerializer, AttendanceSerializer
)

import logging
logger = logging.getLogger(__name__)

class CheckPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "permissions": list(request.user.get_all_permissions())
        })

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Administrator created successfully!'}, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                response = Response({
                    'refresh': str(refresh),
                    'access': access_token
                })
                response.set_cookie(
                    key="access_token", 
                    value=access_token, 
                    httponly=True,
                    samesite='Lax',
                    secure=False
                )
                return response

            return Response({"error": "Неверные данные"}, status=401)
        return Response(serializer.errors, status=400)

class HelloWorldAPIView(APIView):
    def get(self, request):
        return Response({"message": "Hello, World!"})

#######################################################################################################
# API Views для новых моделей

class FacultyListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        faculties = Faculty.objects.all()
        serializer = FacultySerializer(faculties, many=True)
        return Response(serializer.data)

class FacultyIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, faculty_id):
        faculty = get_object_or_404(Faculty, faculty_id=faculty_id)
        serializer = FacultySerializer(faculty)
        return Response(serializer.data)

class SpecialityListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        specialities = Speciality.objects.all()
        serializer = SpecialitySerializer(specialities, many=True)
        return Response(serializer.data)

class SpecialityIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, speciality_id):
        speciality = get_object_or_404(Speciality, speciality_id=speciality_id)
        serializer = SpecialitySerializer(speciality)
        return Response(serializer.data)

class StudentGroupListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        groups = StudentGroup.objects.all()
        serializer = StudentGroupSerializer(groups, many=True)
        return Response(serializer.data)

class StudentGroupIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, group_id):
        group = get_object_or_404(StudentGroup, group_id=group_id)
        serializer = StudentGroupSerializer(group)
        return Response(serializer.data)

class StudentListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class StudentIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

class DisciplineListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        disciplines = Discipline.objects.all()
        serializer = DisciplineSerializer(disciplines, many=True)
        return Response(serializer.data)

class DisciplineIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, discipline_id):
        discipline = get_object_or_404(Discipline, discipline_id=discipline_id)
        serializer = DisciplineSerializer(discipline)
        return Response(serializer.data)

class ResultTypeListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        result_types = ResultType.objects.all()
        serializer = ResultTypeSerializer(result_types, many=True)
        return Response(serializer.data)

class ResultTypeIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, result_id):
        result_type = get_object_or_404(ResultType, result_id=result_id)
        serializer = ResultTypeSerializer(result_type)
        return Response(serializer.data)

class StudentResultListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        student_results = StudentResult.objects.all()
        serializer = StudentResultSerializer(student_results, many=True)
        return Response(serializer.data)

class StudentResultByStudentView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, student_id):
        student_results = StudentResult.objects.filter(student_id=student_id)
        serializer = StudentResultSerializer(student_results, many=True)
        return Response(serializer.data)

class StudentResultByDisciplineView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, discipline_id):
        student_results = StudentResult.objects.filter(discipline_id=discipline_id)
        serializer = StudentResultSerializer(student_results, many=True)
        return Response(serializer.data)

class AttendanceListView(APIView):
    permission_classes = [IsStaffOrSuperUser]
    
    def get(self, request):
        """
        Получить все записи о посещаемости
        """
        attendance = Attendance.objects.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

class AttendanceIDView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, lesson_id):
        """
        Получить запись о посещаемости по ID занятия
        """
        attendance = get_object_or_404(Attendance, lesson_id=lesson_id)
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)

class AttendanceByStudentView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, student_id):
        """
        Получить посещаемость конкретного студента
        """
        attendance = Attendance.objects.filter(student_id=student_id)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

class AttendanceByDisciplineView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, discipline_id):
        """
        Получить посещаемость по конкретной дисциплине
        """
        attendance = Attendance.objects.filter(discipline_id=discipline_id)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

class AttendanceByStudentDisciplineView(APIView):
    permission_classes = [IsStaffOrSuperUser]

    def get(self, request, student_id, discipline_id):
        """
        Получить посещаемость студента по конкретной дисциплине
        """
        attendance = Attendance.objects.filter(
            student_id=student_id, 
            discipline_id=discipline_id
        )
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)