from flask import Flask, request, jsonify
import requests
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

cached_stories = []  # cache for stories
last_updated = 0  # last timestamp when stories were updated
cache_duration = 3600  # in seconds
model = SentenceTransformer("all-MiniLM-L6-v2")


def fetch_story(story_id):
    """This function fetches a single story, and if the url is empty (primarily
    for Ask HN threads), corrects the url for that story"""
    try:
        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()
        if "url" not in story or not story["url"]:
            story["url"] = f"https://news.ycombinator.com/item?id={story_id}"
        return story
    except Exception as e:
        print(f"Error fetching story {story_id}: {e}")
        return None


# Function to fetch top stories from Hacker News
def fetch_top_stories():
    """This function fetches the top 500 (parameterized) stories from Hacker
    News. cached_stories and last_updated have been declared as global within 
    the function to prevent the function from creating new local variables with
    the same names.
    """
    global cached_stories, last_updated
    current_time = time.time()
    try:
        if current_time - last_updated > cache_duration:
            response = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            story_ids = response.json()[:500]
            with ThreadPoolExecutor(max_workers=10) as executor:
                stories = list(executor.map(fetch_story, story_ids))
            cached_stories = [story for story in stories if story]
            last_updated = current_time
    except Exception as e:
        print(f"An unexpected error occurred while fetching stories: {e}")
    return cached_stories


def rank_stories_with_sentence_embeddings(user_bio, stories):
    story_texts = [
        story.get("title", "") + " " + story.get("text", "") for story in stories
    ]
    # story_texts = [story.get('text', '') for story in stories]
    documents = [user_bio] + story_texts
    embeddings = model.encode(documents)
    cosine_similarities = cosine_similarity([embeddings[0]], embeddings[1:]).flatten()
    ranked_stories = sorted(
        zip(cosine_similarities, stories), key=lambda x: x[0], reverse=True
    )
    return [story for _, story in ranked_stories]


@app.route("/")
def home():
    return "Hello, Flask is running!"


@app.route("/ranked_stories", methods=["POST"])
def get_ranked_stories():
    user_bio = request.json.get("bio", "")

    if not any(char.isalnum() for char in user_bio):
        return (
            jsonify(
                {"error": "User bio must contain at least one alphanumeric character."}
            ),
            400,
        )

    stories = fetch_top_stories()
    # ranked_stories = rank_stories_tfidf(user_bio, stories)
    # ranked_stories = rank_stories_with_lda(user_bio, stories)
    ranked_stories = rank_stories_with_sentence_embeddings(user_bio, stories)
    return jsonify(ranked_stories)


if __name__ == "__main__":
    app.run(debug=True)
