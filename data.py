
import psycopg2
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

# Function to retrieve random questions from the database
def get_random_questions(grade, subject, subtopic, limit=4):
    conn = connect_to_db()
    cur = conn.cursor()

    query = """
    SELECT q.question_text, q.answer_text
    FROM Questions q
    JOIN Grades g ON q.grade_id = g.id
    JOIN Subjects s ON q.subject_id = s.id
    JOIN Subtopics st ON q.subtopic_id = st.id
    WHERE g.grade_name = %s
      AND s.subject_name = %s
      AND st.subtopic_name = %s
      AND st.grade_id = g.id
    ORDER BY RAND()
    LIMIT %s;
    """
    cur.execute(query, (grade, subject, subtopic, limit))
    questions = cur.fetchall()

    cur.close()
    conn.close()
    return questions

# After grade, subject, and subtopic have been selected
async def generate_questions(update, context):
    grade = context.user_data["grade"]
    subject = context.user_data["subject"]
    subtopic = context.user_data["subtopic"]

    # Fetch random questions from the database
    questions = get_random_questions(grade, subject, subtopic)

    # Respond with the questions
    if questions:
        for question, answer in questions:
            formatted_message = f"**Question**: {question}\n**Answer**: {answer}"
            await update.message.reply_text(formatted_message)
    else:
        await update.message.reply_text("No questions found for the selected criteria.")

##-----