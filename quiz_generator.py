from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

# Create Groq client
client = Groq(api_key=api_key)


def generate_quiz(topic, num_questions, difficulty):

    num_questions = int(num_questions)

    prompt = f"""
    Generate {num_questions} {difficulty} level multiple-choice questions about "{topic}".

    Requirements:
    - Each question must have exactly 4 options.
    - Only one option should be correct.
    - Questions should match the {difficulty} difficulty level.
    - Keep explanations clear and educational.

    Return ONLY valid JSON in this format:

    [
    {{
        "question": "question text",
        "options": ["option1","option2","option3","option4"],
        "answer": "correct option",
        "explanation": "short explanation why the answer is correct"
    }}
    ]

    Important rules:
    - Do NOT include any text outside the JSON.
    - Do NOT include markdown like ```json.
    - The response must start with [ and end with ].
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    quiz_text = response.choices[0].message.content

    # Remove markdown formatting if present
    quiz_text = quiz_text.replace("```json", "").replace("```", "").strip()

    try:
        quiz_data = json.loads(quiz_text)
    except json.JSONDecodeError:
        print("Invalid JSON from AI")
        quiz_data = []
    quiz_data = quiz_data[:num_questions]
    return quiz_data


# Test mode
if __name__ == "__main__":
    quiz = generate_quiz("Python", 5, "Medium")
    print(quiz)