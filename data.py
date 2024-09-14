import random
import os
import pymysql

# Database connection details
DATABASE = {
    'database': os.getenv('DATABASE_NAME'),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'host': os.getenv('DATABASE_HOST'),
    'port': os.getenv('DATABASE_PORT')
}

# Connect to the PostgreSQL database
def connect_to_db():
    conn = pymysql.connect(
        host=DATABASE['host'],
        user=DATABASE['user'],
        password=DATABASE['password'],
        database=DATABASE['database'],  # Use 'database' instead of 'dbname'
        port=int(DATABASE['port'])
    )
    return conn

async def get_topics_for_grade_and_subject(grade_id, subject_id):
    # Query to get unique topic_ids from past_paper_questions for the selected grade and subject
    query = """
    SELECT DISTINCT t.topic_name
    FROM topics t
    JOIN past_paper_questions ppq ON t.id = ppq.topic_id
    WHERE ppq.grade_id = %s AND ppq.subject_id = %s
    """
    
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, (grade_id, subject_id))
    topics = cur.fetchall()
    cur.close()
    conn.close()
    
    return topics

async def get_grade_id(grade_name):
    query = "SELECT id FROM grades WHERE grade_name = %s"
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, (grade_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

async def get_subject_id(subject_name):
    query = "SELECT id FROM subjects WHERE subject_name = %s"
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, (subject_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None


async def get_subjects_for_grade(grade_id):
    query = """
    SELECT DISTINCT s.subject_name
    FROM subjects s
    JOIN past_paper_questions ppq ON s.id = ppq.subject_id
    WHERE ppq.grade_id = %s
    """
    
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, (grade_id,))
    subjects = cur.fetchall()
    cur.close()
    conn.close()
    
    return subjects
 
async def get_grades_from_db():
    query = "SELECT grade_name FROM grades"
    
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query)
    grades = cur.fetchall()
    cur.close()
    conn.close()
    
    return grades


# Function to retrieve random questions from the database
async def get_random_questions(grade, subject, topic, limit=1):
    conn = connect_to_db()
    cur = conn.cursor()

    query = """
    SELECT q.question, q.answer
    FROM past_paper_questions q
    JOIN grades g ON q.grade_id = g.id
    JOIN subjects s ON q.subject_id = s.id
    JOIN topics t ON q.topic_id = t.id
    WHERE g.grade_name = %s
      AND s.subject_name = %s
      AND t.topic_name = %s
      AND t.subject_id = s.id
    ORDER BY RAND()
    LIMIT %s;
    """
    cur.execute(query, (grade, subject, topic, limit))
    questions = cur.fetchall()

    cur.close()
    conn.close()
    return questions



##-----