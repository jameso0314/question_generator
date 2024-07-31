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
    Can you generate a more refined question based on the question '{title}'? Make the refined question in the first person and ensure it has a human-like touch, including potential typos.
   
    """

    instruction = f"""
    Given the following question title, generate a JSON response with the following fields:
    - refined_question: {refined_question_instruction}
    - domain: categorize the question into one of the domains such as : "python basics & scripting", "other languages", "mobile development", "web development", etc
    - use_case: generate a use case statement based on the refined question, ensuring it is written in the first person

    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )

        response_text = response.choices[0].message.content.strip()
        logging.info(f"GPT model response: {response_text}")

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
    Generate {num_questions} first-person questions based on the following topic:
    Topic: "{topic}"
    Sub Topic: "{sub_topic}"

    Ensure the questions are relevant to the topic and sub topic, include potential typos, and are suitable for learning and discussion.

    Please do not number the questions. eg 1., 2., 3. etc
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )

        response_text = response.choices[0].message.content.strip()
        logging.info(
            f"GPT model response text for generating questions: {response_text}")

        questions = response_text.split('\n')
        questions = [q.strip() for q in questions if q.strip()]
        logging.info(f"Generated questions: {questions}")
        return questions
    except Exception as e:
        logging.error(f"Error generating questions: {e}")
        return ["Error: Unable to generate questions"]


def break_down_topic(topic):
    instruction = f"""
    Break down the following topic into 20 smaller, more specific subtopics that can be used for searching on StackOverflow. Include common typos and variations:
    Topic: "{topic}"
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )

        response_text = response.choices[0].message.content.strip()
        logging.info(
            f"GPT model response text for breaking down topics: {response_text}")

        subtopics = response_text.split('\n')
        subtopics = [s.strip() for s in subtopics if s.strip()]
        logging.info(f"Generated subtopics: {subtopics}")
        return subtopics
    except Exception as e:
        logging.error(f"Error breaking down topic: {e}")
        return [topic]  # Return the original topic if there's an error


# For testing purposes
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 2:
        test_topic = sys.argv[1]
        num_questions = int(sys.argv[2])
        result = generate_questions(test_topic, num_questions)
        print(f"Original: {test_topic}")
        print(f"Generated Questions: {result}")
    elif len(sys.argv) > 1:
        test_topic = sys.argv[1]
        result = break_down_topic(test_topic)
        print(f"Original: {test_topic}")
        print(f"Subtopics: {result}")
    else:
        print("Please provide a topic and optionally the number of questions as arguments.")
