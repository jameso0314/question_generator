import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_questions(query, num_questions):
    logger.info(f"Fetching questions for query: {query}")
    url = "https://api.stackexchange.com/2.3/search/advanced"
    cutoff_date = datetime.now() - timedelta(days=3*365)
    cutoff_timestamp = int(cutoff_date.timestamp())
    params = {
        'order': 'desc',
        'sort': 'votes',
        'q': query,
        'site': 'stackoverflow',
        'filter': 'withbody',
        'fromdate': cutoff_timestamp
    }
    
    response = requests.get(url, params=params)
    logger.info(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        questions = data.get('items', [])
        logger.info(f"Number of questions fetched: {len(questions)}")

        if len(questions) < num_questions:
            # Perform a broader search if not enough questions are fetched
            broader_cutoff_date = datetime.now() - timedelta(days=5*365)
            broader_cutoff_timestamp = int(broader_cutoff_date.timestamp())
            params['fromdate'] = broader_cutoff_timestamp
            response = requests.get(url, params=params)
            logger.info(f"Broader search response status code: {response.status_code}")
            if response.status_code == 200:
                broader_data = response.json()
                questions += broader_data.get('items', [])
                questions = sorted(
                    questions,
                    key=lambda x: (x['score'], x['answer_count']),
                    reverse=True
                )[:num_questions]
        
        sorted_questions = sorted(
            [q for q in questions if datetime.fromtimestamp(q['creation_date']) > cutoff_date and 'attachment' not in q['body'].lower()],
            key=lambda x: (x['score'], x['answer_count']),
            reverse=True
        )
        return sorted_questions[:num_questions]
    else:
        return []

# To make the module directly executable for testing purposes
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        questions = fetch_questions(topic, 5)
        for question in questions:
            print(question)
            print(f"{question['title']} - {question['link']}")
    else:
        print("Please provide a search query as an argument.")
