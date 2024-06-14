import streamlit as st
import pandas as pd
import random
import logging
from io import BytesIO
from stackoverflow_api import fetch_questions
from openai_api import refine_question

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the title of the app
st.title("StackOverflow Topic Question Generator with Refinement")

# Upload the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    logger.info(f"CSV file read successfully: {df.head()}")

    # Clean and extract the topics from the CSV
    raw_topics = df['Topics'].tolist()
    # Remove unwanted characters and clean topics
    cleaned_topics = []
    for topic in raw_topics:
        cleaned_topic = topic.strip().strip('"').strip(',')
        if cleaned_topic and cleaned_topic not in ['[', ']']:
            cleaned_topics.append(cleaned_topic.rstrip('"'))
    logger.info(f"Extracted topics: {cleaned_topics}")

    # Select the number of topics
    num_topics = st.number_input("How many topics would you like to generate questions for?", min_value=1, max_value=len(cleaned_topics))

    # Select the number of questions per topic
    num_questions = st.number_input("Enter the number of questions you would like to generate for each topic", min_value=1)

    if st.button("Submit"):
        selected_topics = random.sample(cleaned_topics, num_topics)
        logger.info(f"Selected topics: {selected_topics}")
        all_questions = []

        for topic in selected_topics:
            questions = fetch_questions(topic, num_questions)
            for q in questions:
                refined_q = refine_question(q['title'], q['body'])
                all_questions.append({
                    'Topic': topic,
                    'Question Title': q['title'],
                   # 'Question Description': q['body'],
                    'Refined Question': refined_q,
                    'Question Link': q['link'],
                    
                })

        # Convert the list of questions to a DataFrame
        questions_df = pd.DataFrame(all_questions)
        logger.info(f"Questions DataFrame: {questions_df.head()}")

        # Make links clickable
        def make_clickable(link):
            return f'<a href="{link}" target="_blank">{link}</a>'

        questions_df['Question Link'] = questions_df['Question Link'].apply(make_clickable)

        # Display the questions in a table
        st.write(questions_df.to_html(escape=False), unsafe_allow_html=True)

        # Button to download the table as an Excel file
        if not questions_df.empty:
            @st.cache_data
            def convert_df(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                processed_data = output.getvalue()
                return processed_data

            excel_data = convert_df(questions_df)
            st.download_button(
                label="Download data as Excel",
                data=excel_data,
                file_name='questions.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
