import requests
import logging

logger = logging.getLogger(__name__)

def fetch_questions(query, num_questions):
    logger.info(f"Fetching questions for query: {query}")
    url = f"https://api.stackexchange.com/2.3/search/advanced"
    params = {
        'order': 'desc',
        'sort': 'votes',
        'q': query,
        'site': 'stackoverflow',
        'filter': 'withbody' 
    }
    response = requests.get(url, params=params)
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        questions = data.get('items', [])
        logger.info(f"Number of questions fetched: {len(questions)}")
        # Filter questions to get those with high popularity (high votes and answers)
        sorted_questions = sorted(questions, key=lambda x: (x['score'], x['answer_count']), reverse=True)
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
