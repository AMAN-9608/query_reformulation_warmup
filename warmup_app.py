import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import time

model = SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
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
        st.error(f"Error fetching story {story_id}: {e}")
        return None


@st.cache_data
def fetch_top_stories():
    """This function fetches the top 500 (parameterized) stories from Hacker
    News.
    """
    try:
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json"
        )
        story_ids = response.json()[:500]
        with ThreadPoolExecutor(max_workers=10) as executor:
            stories = list(executor.map(fetch_story, story_ids))
        return [story for story in stories if story]
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching stories: {e}")
        return []


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


st.title("Hacker News Story Ranker")
st.markdown(
    """This is an application where you can enter your bio and see the top 500 
    stories from hackernews, ranked in order of decreasing similarity to your 
    interests."""
)

user_bio = st.text_area("Enter your bio:", height=150)

if st.button("Submit"):
    if not user_bio:
        st.error("User bio is required.")
    elif not any(char.isalnum() for char in user_bio):
        st.error("User bio must contain at least one alphanumeric character.")
    else:
        stories = fetch_top_stories()
        ranked_stories = rank_stories_with_sentence_embeddings(user_bio, stories)
        if ranked_stories:
            st.write("Ranked Stories:")
            for story in ranked_stories:
                st.write(f"- [{story.get('title')}]({story.get('url')})")
        else:
            st.write("No stories found.")    
