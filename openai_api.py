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
    - use_case: generate a use case statement based on the refined question

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

# For testing purposes
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        test_question = sys.argv[1]
        refined = refine_question(test_question)
        print(f"Original: {test_question}")
        print(f"Refined: {refined}")
    else:
        print("Please provide a question as an argument.")
