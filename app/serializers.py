from rest_framework import serializers
from application.models import Administrator
from application.models import Academ, Attendance, CourseProjects, DebtAudit, Debts, Diploma, Disciples, EducationPlan, FormControl, Grades, Group, HoursPerSemest, Nagruzka, Practise, PractiseType, Rating, RatingType, Specialty, Student, Teachers
from django.contrib.auth import get_user_model


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = ['email', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user = Administrator.objects.create_user(email=email, password=password, **validated_data)
        return user


class AcademSerializer(serializers.ModelSerializer):
    class Meta:
        model = Academ
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class CourseProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProjects
        fields = '__all__'

class DebtAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtAudit
        fields = '__all__'

class DebtsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debts
        fields = '__all__'

class DiplomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diploma
        fields = '__all__'

class DisciplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciples
        fields = '__all__'

class EducationPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationPlan
        fields = '__all__'

class FormControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormControl
        fields = '__all__'

class GradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grades
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class HoursPerSemestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoursPerSemest
        fields = '__all__'

class NagruzkaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nagruzka
        fields = '__all__'

class PractiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practise
        fields = '__all__'

class PractiseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PractiseType
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

class RatingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingType
        fields = '__all__'

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeachersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = '__all__'
