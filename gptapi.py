from openai import AsyncOpenAI
import os
from typing import Final
from dotenv import load_dotenv

## api key for open ai
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AI_GENERATED: Final = "Assesment book questions"
REAL_PAPER: Final = "Past Year Questions"

async def send_image_to_openai(base64_image):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    prompt = """
Based on the image, you must:
1. Read all the questions in the image and identify the overall topic, difficulty level, and question structure (e.g., multiple-choice, short-answer, long-answer).
2. Generate 4 new questions on the same topic and difficulty level, ensuring that the new questions follow the exact same structure and format as the questions in the image.
3. Ensure the questions are coherent, make sense, and align with the Singapore syllabus. Do not generate random or irrelevant questions.
4. After creating the 4 new questions, provide the answers for each question along with a short explanation.

Important: Do not output any additional analysis such as the overall topic, difficulty level, or structure to the student. Only provide the questions and their corresponding answers. Keep the format clean and simple, with no special characters like `**` or `##`.
"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # Using gpt-4o-mini as per the documentation
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt  
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "auto"  # You can change this to "low" or "high" if needed
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return response.choices[0].message.content


async def chat_with_gpt(text):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal:paper-cut:A0VCkgl2",
        messages=[
            {
                "role": "system",
                "content": "You are an experienced educator for Singapore students. Based on the Grade, Subject and Topic provided, create 3 questions covering the topics within the subject for students in grade. Ensure the questions vary in difficulty and format, including multiple-choice, short-answer, and essay-type questions. Align the questions with the Singaporean curriculum standards and provide clear instructions and context for each question. After giving the questions, you must also give them answers."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content
