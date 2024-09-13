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

async def get_subjects_from_db():

    query = "SELECT subject_name FROM subjects"  # Adjust the table and column name as needed.
    
    subjects = []
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query)
    subjects = cur.fetchall()
    cur.close()
    conn.close()
    return subjects
 
async def get_grades_for_subject(subject_name):
    # Function to get grades associated with a selected subject from the database
    query = """
    SELECT g.grade_name 
    FROM grades g
    JOIN subject_grade sg ON g.id = sg.grade_id
    JOIN subjects s ON sg.subject_id = s.id
    WHERE s.subject_name = %s
    """
    
    grades = []
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, (subject_name))
    grades = cur.fetchall()
    cur.close()
    conn.close()
    return grades

# Function to retrieve random questions from the database
def get_random_questions(grade, subject, topic, limit=1):
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

# After grade, subject, and topic have been selected
async def generate_questions(update, context):
    grade = context.user_data["grade"]
    subject = context.user_data["subject"]
    topic = context.user_data["topic"]

    # Fetch random questions from the database
    questions = get_random_questions(grade, subject, topic)

    # Respond with the questions
    if questions:
        for question, answer in questions:
            formatted_message = f"**Question**: {question}\n**Answer**: {answer}"
            await update.message.reply_text(formatted_message)
    else:
        await update.message.reply_text("No questions found for the selected criteria.")

##-----