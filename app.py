import streamlit as st
import pandas as pd
import random
import logging
from io import BytesIO
from stackoverflow_api import fetch_questions
from openai_api import refine_question, generate_questions, break_down_topic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to load and clean CSV file


def load_and_clean_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    logger.info(f"CSV file read successfully: {df.head()}")
    raw_topics = df['Topics'].tolist()
    cleaned_topics = [topic.strip().strip('"').strip(',').rstrip(
        '"') for topic in raw_topics if topic.strip() and topic.strip() not in ['[', ']']]
    logger.info(f"Extracted topics: {cleaned_topics}")
    return cleaned_topics

# Function to fetch or generate questions


def fetch_or_generate_questions(topic, num_questions, full_topic_name, years, progress_bar=None, progress_step=0):
    topic_variations = break_down_topic(topic)

    for variation in topic_variations:
        questions = fetch_questions(variation, num_questions, years)
        if questions:
            num_fetched_questions = len(questions)
            if num_fetched_questions < num_questions:
                remaining_questions_needed = num_questions - num_fetched_questions
                logger.info(
                    f"Fetched {num_fetched_questions} questions from StackOverflow for variation '{variation}'. Generating {remaining_questions_needed} more questions using ChatGPT.")
                generated_questions = generate_questions(
                    full_topic_name, remaining_questions_needed, sub_topic=variation)
                questions.extend([{'title': q} for q in generated_questions])
            break
    else:
        questions = generate_questions(
            full_topic_name, num_questions, sub_topic=topic)
        questions = [{'title': q} for q in questions]

    results = []
    for i, q in enumerate(questions):
        refined_data = refine_question(q['title'])
        if isinstance(refined_data, str):
            refined_data = {'refined_question': 'Error',
                            'domain': 'Error', 'use_case': 'Error'}

        result = {
            'Full Topic Name': full_topic_name,
            'Topic': topic,
            # Use the refined question
            'Question Title': refined_data.get('refined_question', 'Error'),
            'Domain': refined_data.get('domain', 'Error'),
            'Use Case Statement': refined_data.get('use_case', 'Error'),
            'Question Link': q.get('link', ''),
        }
        results.append(result)
        if progress_bar:
            current_progress = progress_step + (i + 1) / num_questions
            # Ensure progress doesn't exceed 1.0
            progress_bar.progress(min(current_progress, 1.0))
    return results

# Function to process the topics and fetch or generate questions


def process_topics(selected_topics, num_questions, full_topic_name, years):
    all_questions = []
    total_steps = len(selected_topics) * num_questions
    progress_bar = st.progress(0)
    progress_step = 0

    for i, topic in enumerate(selected_topics):
        questions = fetch_or_generate_questions(
            topic, num_questions, full_topic_name, years, progress_bar, progress_step)
        all_questions.extend(questions)
        progress_step = (i + 1) * num_questions / total_steps
        # Ensure progress doesn't exceed 1.0
        progress_bar.progress(min(progress_step, 1.0))

    return pd.DataFrame(all_questions)

# Function to convert DataFrame to Excel


def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Main function to run the Streamlit app


def main():
    st.title("QGen")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        cleaned_topics = load_and_clean_csv(uploaded_file)

        num_topics = st.number_input(
            "How many sub-topics would you like to generate questions for?", min_value=1, max_value=len(cleaned_topics))
        num_questions = st.number_input(
            "Enter the number of questions you would like to generate for each topic", min_value=1)
        full_topic_name = st.text_input("Enter the full topic name:")
        past_years = st.number_input(
            "For the past how many years (leave blank for no filter):", min_value=0, step=1, format="%d")

        if st.button("Submit"):
            selected_topics = random.sample(cleaned_topics, num_topics)
            logger.info(f"Selected topics: {selected_topics}")

            years = past_years if past_years > 0 else None
            questions_df = process_topics(
                selected_topics, num_questions, full_topic_name, years)
            logger.info(f"Questions DataFrame: {questions_df.head()}")

            if not questions_df.empty:
                st.write(questions_df)
                excel_data = convert_df_to_excel(questions_df)
                st.download_button(
                    label="Download data as Excel",
                    data=excel_data,
                    file_name='questions.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.write(
                    "No questions were fetched. Please try different topics or check your network connection.")


if __name__ == "__main__":
    main()
