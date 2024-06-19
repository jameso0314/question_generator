import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_questions(query, num_questions, past_years=None):
    logger.info(f"Fetching questions for query: {query}")
    url = f"https://api.stackexchange.com/2.3/search/advanced"
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'q': query,
        'site': 'stackoverflow',
        'filter': '!BHMIbze0EPheMk572h0ktETsgnphhU'
    }

    if past_years:
        cutoff_date = datetime.now() - timedelta(days=past_years*365)
        cutoff_timestamp = int(cutoff_date.timestamp())
        params['fromdate'] = cutoff_timestamp

    response = requests.get(url, params=params)
    logger.info(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        questions = data.get('items', [])

        logging.info(f"question fetched: {questions}")
        logger.info(f"Number of questions fetched: {len(questions)}")

        # Relax the filter criteria: include questions where query is in title or tags
        sorted_questions = sorted(
            [q for q in questions if query.lower() in q['title'].lower() or any(query.lower() in tag.lower() for tag in q.get('tags', []))],
            key=lambda x: (x.get('score', 0), x.get('answer_count', 0)),
            reverse=True
        )
        logger.info(f"Number of sorted questions: {len(sorted_questions)}")
        return sorted_questions[:num_questions]
    else:
        logger.error(f"Failed to fetch questions: {response.text}")
        return []

# To make the module directly executable for testing purposes
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        years = int(sys.argv[2]) if len(sys.argv) > 2 else None
        questions = fetch_questions(topic, 5, years)
        for question in questions:
            print(question)
            print(f"{question['title']} - {question['link']}")
    else:
        print("Please provide a search query as an argument.")
