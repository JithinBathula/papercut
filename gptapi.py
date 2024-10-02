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
Task: Analyze and Generate New Exam Questions

1. Question Analysis:

a. Identify the main topic and subtopics present in the provided exam questions.
b. Evaluate the difficulty level and complexity of each question.
c. Examine the structure and format of the questions, noting any patterns or specific types used.

2. Question Generation: Create 1 new questions that:
a. Align with the same main topic and difficulty level as the original questions.
b. MAKE SURE THERE IS ONLY 1 CORRECT ANSWER
c. Follow the same structure and format as the original questions.
d. Are relevant to the Singapore syllabus for this subject and grade level.

3. Quality Check: For each new question:
a. Ensure the question is solvable and has one correct answer.
b. Confirm that the difficulty level is consistent with the original questions.
c. Verify that the question tests understanding, rather than simple recall of facts.

Output format must be in simple text. For example, fractions must just be a simple / and so on.
Output to User. Your output must only be the questions in this format:

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
            temperature=0.5,
    # max_tokens=1500,
    # top_p=0.9,
    # frequency_penalty=0.2,
    # presence_penalty=0.0,
    # n=1  # Generate one question at a time
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
        model="gpt-4o", max_tokens=1000, temperature=1,
        messages=[
            {
                "role": "system",
                "content": '''
Task: Solve and Explain Exam Questions

You are an experienced educator for Singapore students. For question provided, follow this process:

1. Problem-Solving Process:
a. Break down the problem into clear and logical steps.
b. Solve each step sequentially and accurately.

2. Answer Formulation:
a. After completing all steps, state the final answer clearly.
b. Provide a brief explanation summarizing the final answer and key insights from the solution process.

3. Quality Assurance:
a. Double-check the solution and final answer for accuracy and adherence to the Singapore syllabus.
b. Ensure that the explanations are clear, aligned with the student's learning level, and support deep understanding of the topic.
c. Correct any errors or unclear explanations before finalizing the solution.

4. Final Output Format (for each question) This is the only thing you must output and nothing else:

Short Explanation: [Provide a short explanation of the final answer and reasoning in 2 sentences]
Final Answer: [State the answer clearly]

REMEMBER TO ONLY SHOW THE SHORT EXPLANATION AND THE FINAL ANSWER. NO NEED TO SEND THE STEPS IN THE RESPONSE. IF THERE ARE MORE THAN 1 ANSWER, PROVIDE ALL THE CORRECt ANSWERS

Important Guidelines:
Tailor your language and explanations to suit the educational level of Singapore students.
Ensure that all mathematical and scientific concepts used are accurate and relevant to the Singapore curriculum.
The solutions must be correct without fail, and the explanations must promote clear understanding.

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
Task: Generate Exam Questions Aligned with Singapore Curriculum

You are an experienced educator for Singapore students. Based on the provided Grade, Subject, and Topic, follow these steps to create 1 high-quality exam questions:

1. Question Generation:
a. Create one question that is aligned with the Singapore curriculum standards for the specified grade and topic.
b. Ensure the question cover different aspects of the topic, testing both conceptual understanding and application.
c. Question must be of the currect difficulty with respect to the grade.

2. Question Format:
a. Question format must be simple to read as this is aimed towards children. For example, fractions just use / instead of something complicated.
b. Question should have clear instructions.

3. Alignment with the Singapore Curriculum:
Ensure that the questions are relevant to the Singaporean syllabus for the subject and grade level.
The content and concepts covered should reflect current curriculum standards and be appropriate for the student’s cognitive level.

4. Clarity and Precision:
Make sure the questions are clear and unambiguous.
Provide precise instructions for how students should respond (e.g., “Choose the best answer,” or “Explain your reasoning in two sentences”). Make sure the questnos are answerable and have only 1 correct answer.
Output structure to show:
Question
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
    

async def checker(text):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    prompt = """
You will be presented with a question. This question can be multiple-choise, short answer or long answer. Your goal is to check if the question makes sense and that there is only one valid answer. If the question does not make sense. Then you must update the question a bit to make it make sense. REMEMBER, ONLY 1 CORRECT ANSWER FOR THE QUESTION. Your output would just be the question, dont mention the changes you did or didnt do, just the question. If its MCQ, make sure that the only one of the options is correct. If not, change them such that only 1 is correct.
"""
    response = await client.chat.completions.create(
        model="gpt-4o",  # Using gpt-4o-mini as per the documentation
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "system",
                        "text": prompt  
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }
        ],
    #         temperature=0.5,
    # max_tokens=1500,
    # top_p=0.9,
    # frequency_penalty=0.2,
    # presence_penalty=0.0,
    # n=1  # Generate one question at a time
    )
    
    # res = await message_checker(response.choices[0].message.content)
    
    # # Clean the response to ensure it's properly formatted for Telegram
    # res = res.replace("*", "").replace("_", "").replace('#',"").replace('---',"")  # In case ** or other symbols come back, remove or replace with acceptable markdown.
    
    res = response.choices[0].message.content
    return res