import openai
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def refine_question(title, description):
    instruction = f"""
    Given the following information, generate a single conversational question in the third person that is clear, concise, and about two lines long.

    Title: "{title}"
    Description: "{description}"

    The question should be based on the title and description, and written as if asking someone else.
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

        refined_question = response.choices[0].message.content.strip()
        logging.info(f"GPT model response: {refined_question}")
        return refined_question
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
