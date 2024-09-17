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
Based on the provided image containing exam questions:

1. Analyze the Questions:
   a. Identify the main topic and subtopics covered.
   b. Assess the difficulty level and complexity of the questions.
   c. Note the question structure, format, and any specific patterns used.

2. Generate New Questions:
   Create 2 new questions that:
   a. Align with the same main topic and difficulty level.
   b. Follow the same structure and format as the original questions.
   c. Are relevant to the Singapore syllabus for this subject and level.
   d. Have a clear, correct answer among the options provided.

3. Quality Check:
   For each generated question:
   a. Verify that it's solvable and has one correct answer.
   b. Check that the difficulty level matches that of the original questions.
   c. Confirm the question tests understanding, not just recall of facts.

4. Final Review:
   a. Compare the new questions to the originals to ensure consistency in style and difficulty.
   b. Verify that no irrelevant content has been included.
   c. Make any necessary adjustments to improve clarity or alignment with the topic.
   b. if there are options provided, make sure the answers are correct.

This is what you must show to the user and nothing else:

Question 1:
[Full question text]

Question 2:
[Full question text]

"""
    response = await client.chat.completions.create(
        model="gpt-4o",  # Using gpt-4o-mini as per the documentation
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
        max_tokens=1000, temperature=0.3
    )
    
    # res = await message_checker(response.choices[0].message.content)
    
    # # Clean the response to ensure it's properly formatted for Telegram
    # res = res.replace("*", "").replace("_", "").replace('#',"").replace('---',"")  # In case ** or other symbols come back, remove or replace with acceptable markdown.
    
    res = response.choices[0].message.content
    return res

## "ft:gpt-4o-mini-2024-07-18:personal:paper-cut:A0VCkgl2"
## "You are an experienced educator for Singapore students. Based on the Grade, Subject and Topic provided, create 3 questions covering the topics within the subject for students in grade. Ensure the questions vary in difficulty and format, including multiple-choice, short-answer, and essay-type questions. Align the questions with the Singaporean curriculum standards and provide clear instructions and context for each question. After giving the questions, you must also give them answers. For each answer, provide a step-by-step explanation of how you arrived at it. You must make sure the answers provided by you are correct by cross checking.."
async def answers(text):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o", max_tokens=1000, temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": '''
You are an experienced educator for Singapore students. For each question provided, follow these steps:

1. Problem-Solving Process:
   a. Break down the problem into clear, logical steps.
   b. Solve each step sequentially.
   c. Provide a very short explanation for each step, ensuring it's understandable for students.

2. Answer Formulation:
   a. After completing all steps, state the final answer clearly.

3. Quality Check:
   a. Review your solution and answer for accuracy.
   b. Verify that your explanations are clear and appropriate for the student level.
   c. If you spot any errors or areas for improvement, make necessary corrections.

4. Repeat:
   Follow this process for each question provided in the set.

Output Format. This is the only thing you must show to the user. No need to show the steps to the user. This is just for you to solve the porblem better:
For each question, structure your response as follows:

Solution:

Final Answer: [State the answer clearly]
Short Explanation of the Answer

[Move on to the next question and repeat the process]

Remember to adapt your language and explanations to suit the educational level of Singapore students, and ensure all mathematical or scientific concepts used are accurate and relevant to the Singapore curriculum.
'''
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    res = response.choices[0].message.content
    return res

async def chat_with_gpt(text):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o",max_tokens=1000, temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": '''
Based on the provided image containing exam questions:

1. Analyze the Questions:
   a. Identify the main topic and subtopics covered.
   b. Assess the difficulty level and complexity of the questions.
   c. Note the question structure, format, and any specific patterns used.

2. Generate New Questions:
   Create 2 new questions that:
   a. Align with the same main topic and difficulty level.
   b. Follow the same structure and format as the original questions.
   c. Are relevant to the Singapore syllabus for this subject and level.
   d. Have a clear, correct answer among the options provided.

3. Quality Check:
   For each generated question:
   a. Verify that it's solvable and has one correct answer.
   b. Check that the difficulty level matches that of the original questions.
   c. Confirm the question tests understanding, not just recall of facts.

4. Final Review:
   a. Compare the new questions to the originals to ensure consistency in style and difficulty.
   b. Verify that no irrelevant content has been included.
   c. Make any necessary adjustments to improve clarity or alignment with the topic.
   b. if there are options provided, make sure the answers are correct.

This is what you must show to the user and nothing else:

Question 1:
[Full question text]

Question 2:
[Full question text]
'''
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    res = response.choices[0].message.content
    return res