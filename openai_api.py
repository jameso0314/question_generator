import openai
import os
from dotenv import load_dotenv
import logging
import json

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def refine_question(title):

    refined_question_instruction = f"""
    Can you generate a more refined question based on the questions {title} on a level that would match a use case statement rather 
    than a first person statement. Why? Having a first person statement may only limit the user (trainer) think in one scenario. 
    But having it in a use case statement would allow them to think out of the box too and incorporate few additional items as well 
    that would help solve the problem.

    please dont start your statement with the follwoing:

    Certainly! Here's a refined question framed as a use case statement:

    Just give me the refined question and make it one long sentence.
   
    """

    instruction = f"""
    Given the following question title, generate a JSON response with the following fields:
    - refined_question: {refined_question_instruction}
    - domain: categorize the question into one of the domains such as : "python basics & scripting", "other languages", "mobile development", "web development", etc
    - use_case: generate a use case statement based on the refined question, ensuring it is written in the third person

    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )

        response_text = response.choices[0].message.content.strip()
        logging.info(f"GPT model response: {response_text}")

       # Remove wrapping ```json and ``` if they exist
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()
            logging.info(f"Trimmed response text: {response_text}")

        try:
            result = json.loads(response_text)
            logging.info(f"GPT model response JSON: {result}")
            return result
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return {"refined_question": "Error", "domain": "Error", "use_case": f"JSON decode error: {e}"}
    except Exception as e:
        logging.error(f"Error refining question: {e}")
        return f"Error: {e}"
    

def generate_questions(topic, num_questions, sub_topic):
    instruction = f"""
    Generate {num_questions} questions, a real world question based on the following topic:
    Topic: "{topic}"
    Sub Topic: "{sub_topic}"

    Ensure the questions are relevant to the topic and sub topic and suitable for learning and discussion.

    Please do not number the questions. eg 1., 2., 3. etc
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )

        response_text = response.choices[0].message.content.strip()
        logging.info(f"GPT model response text for generating questions: {response_text}")

        questions = response_text.split('\n')
        questions = [q.strip() for q in questions if q.strip()]
        logging.info(f"Generated questions: {questions}")
        return questions
    except Exception as e:
        logging.error(f"Error generating questions: {e}")
        return ["Error: Unable to generate questions"]


# For testing purposes
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 2:
        test_title = sys.argv[1]
        num_questions = int(sys.argv[2])
        result = generate_questions(test_title, num_questions)
        print(f"Original: {test_title}")
        print(f"Generated Questions: {result}")
    elif len(sys.argv) > 1:
        test_title = sys.argv[1]
        result = refine_question(test_title)
        print(f"Original: {test_title}")
        print(f"Result: {result}")
    else:
        print("Please provide a question title and optionally the number of questions as arguments.")