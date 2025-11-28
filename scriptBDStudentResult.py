import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Параметры подключения к БД
DB_CONFIG = {
    'host': 'localhost',
    'database': 'project_db',
    'user': 'postgres',
    'password': '12345',  # замените на ваш пароль
    'port': '5432'
}

def create_connection():
    """Создание подключения к БД"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

def insert_faculty_data(conn, df):
    """Заполнение таблицы faculty"""
    try:
        cur = conn.cursor()
        
        # Получаем уникальные факультеты
        faculties = df[['Faculty_ID', 'Faculty']].drop_duplicates()
        
        for _, row in faculties.iterrows():
            cur.execute(
                "INSERT INTO faculty (faculty_id, name) VALUES (%s, %s) ON CONFLICT (faculty_id) DO NOTHING",
                (row['Faculty_ID'], row['Faculty'])
            )
        
        conn.commit()
        print(f"Добавлено {len(faculties)} записей в таблицу faculty")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в faculty: {e}")

def insert_speciality_data(conn, df):
    """Заполнение таблицы speciality"""
    try:
        cur = conn.cursor()
        
        # Получаем уникальные специальности
        specialities = df[['Speciality_ID', 'Speciality', 'Faculty_ID']].drop_duplicates()
        
        for _, row in specialities.iterrows():
            cur.execute(
                "INSERT INTO speciality (speciality_id, name, faculty_id) VALUES (%s, %s, %s) ON CONFLICT (speciality_id) DO NOTHING",
                (row['Speciality_ID'], row['Speciality'], row['Faculty_ID'])
            )
        
        conn.commit()
        print(f"Добавлено {len(specialities)} записей в таблицу speciality")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в speciality: {e}")

def insert_student_group_data(conn, df):
    """Заполнение таблицы student_group"""
    try:
        cur = conn.cursor()
        
        # Получаем уникальные группы
        groups = df[['Group', 'Speciality_ID']].drop_duplicates()
        
        # Создаем словарь для сопоставления группы с ID
        group_id_mapping = {}
        
        for idx, (_, row) in enumerate(groups.iterrows(), 1):
            group_name = row['Group']
            speciality_id = row['Speciality_ID']
            
            # Вставляем группу и получаем её ID
            cur.execute(
                "INSERT INTO student_group (group_id, name, speciality_id) VALUES (%s, %s, %s) ON CONFLICT (group_id) DO NOTHING",
                (idx, group_name, speciality_id)
            )
            group_id_mapping[group_name] = idx
        
        conn.commit()
        print(f"Добавлено {len(groups)} записей в таблицу student_group")
        return group_id_mapping
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в student_group: {e}")
        return {}

def insert_student_data(conn, df, group_id_mapping):
    """Заполнение таблицы student"""
    try:
        cur = conn.cursor()
        
        # Получаем уникальных студентов
        students = df[['student', 'Birthday', 'Is_Academic', 'Group']].drop_duplicates()
        
        for _, row in students.iterrows():
            student_id = row['student']
            birthday = row['Birthday']
            is_academic = bool(row['Is_Academic'])
            group_name = row['Group']
            
            # Получаем ID группы из словаря
            group_id = group_id_mapping.get(group_name)
            
            if group_id:
                cur.execute(
                    """INSERT INTO student (student_id, birthday, is_academic, group_id) 
                    VALUES (%s, %s, %s, %s) ON CONFLICT (student_id) DO NOTHING""",
                    (student_id, birthday, is_academic, group_id)
                )
        
        conn.commit()
        print(f"Добавлено {len(students)} записей в таблицу student")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в student: {e}")

def insert_discipline_data(conn, df):
    """Заполнение таблицы discipline"""
    try:
        cur = conn.cursor()
        
        # Получаем уникальные дисциплины
        disciplines = df[['discipline_id', 'Discipline']].drop_duplicates()
        
        for _, row in disciplines.iterrows():
            cur.execute(
                "INSERT INTO discipline (discipline_id, name) VALUES (%s, %s) ON CONFLICT (discipline_id) DO NOTHING",
                (row['discipline_id'], row['Discipline'])
            )
        
        conn.commit()
        print(f"Добавлено {len(disciplines)} записей в таблицу discipline")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в discipline: {e}")

def insert_result_type_data(conn, df):
    """Заполнение таблицы result_type"""
    try:
        cur = conn.cursor()
        
        # Получаем уникальные типы результатов
        result_types = df[['Result_ID', 'Result']].drop_duplicates()
        
        for _, row in result_types.iterrows():
            result_id = row['Result_ID']
            result_value = row['Result']
            
            # Пропускаем NaN значения
            if pd.isna(result_id):
                continue
                
            cur.execute(
                "INSERT INTO result_type (result_id, result_value) VALUES (%s, %s) ON CONFLICT (result_id) DO NOTHING",
                (int(result_id), str(result_value))
            )
        
        conn.commit()
        print(f"Добавлено {len(result_types)} записей в таблицу result_type")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в result_type: {e}")

def insert_student_result_data(conn, df):
    """Заполнение таблицы student_result"""
    try:
        cur = conn.cursor()
        
        # Обрабатываем каждую запись
        for _, row in df.iterrows():
            student_id = row['student']
            discipline_id = row['discipline_id']
            result_id = row['Result_ID']
            
            # Пропускаем записи с NaN в Result_ID
            if pd.isna(result_id):
                continue
                
            cur.execute(
                """INSERT INTO student_result (student_id, discipline_id, result_id) 
                VALUES (%s, %s, %s) ON CONFLICT (student_id, discipline_id) DO NOTHING""",
                (student_id, discipline_id, int(result_id))
            )
        
        conn.commit()
        print(f"Добавлено {len(df)} записей в таблицу student_result")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в student_result: {e}")

def insert_attendance_data(conn, df):
    """Заполнение таблицы attendance с проверкой внешних ключей"""
    try:
        cur = conn.cursor()
        
        # Получаем существующие ID из связанных таблиц
        
        cur.execute("SELECT student_id FROM student")
        existing_students = {row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT discipline_id FROM discipline")
        existing_disciplines = {row[0] for row in cur.fetchall()}
        
        
        # Подготовка данных для вставки
        attendance_data = []
        skipped_records = 0
        
        for _, row in df.iterrows():
            # Проверяем наличие необходимых данных и внешних ключей
            if ( 
                int(row['student']) in existing_students and
                int(row['discipline_id']) in existing_disciplines):
                
                
                attendance_record = (
                    int(row['lesson_id']),
                    int(row['student']),
                    row['created_at'],
                    row['updated_at'],
                    int(row['user_id']),
                    int(row['discipline_id'])
                )
                attendance_data.append(attendance_record)
            else:
                skipped_records += 1
        
        # Вставляем данные
        insert_query = """
        INSERT INTO attendance (lesson_id, student_id, created_at, updated_at, user_id, discipline_id) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (lesson_id, student_id) DO NOTHING
        """
        
        cur.executemany(insert_query, attendance_data)
        conn.commit()
        print(f"Успешно добавлено {len(attendance_data)} записей в таблицу attendance")
        print(f"Пропущено {skipped_records} записей из-за отсутствия внешних ключей или данных")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке в attendance: {e}")

def main():
    # Загрузка данных из CSV
    print("Загрузка данных из CSV...")
    df = pd.read_csv(r'C:\Users\Kopikou\Desktop\Result_2.csv')
    print(f"Загружено {len(df)} записей")
    
    # Подключение к БД
    print("Подключение к базе данных...")
    conn = create_connection()
    if not conn:
        return
    
    try:
        # Заполняем таблицы в правильном порядке (с учетом внешних ключей)
        # insert_faculty_data(conn, df)
        # insert_speciality_data(conn, df)
        # group_id_mapping = insert_student_group_data(conn, df)
        # insert_student_data(conn, df, group_id_mapping)
        # insert_discipline_data(conn, df)
        # insert_result_type_data(conn, df)
        # insert_student_result_data(conn, df)
        insert_attendance_data(conn, df)
        
        print("Все данные успешно загружены в базу данных!")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()