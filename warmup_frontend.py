import streamlit as st
import requests

st.title("Hacker News Story Ranker")
st.markdown(
    """This is an application where you can enter your bio and see the top 500 
    stories from hackernews, ranked in order of decreasing similarity to your 
    interests."""
)

user_bio = st.text_area("Enter your bio:", height=150)

if st.button("Submit"):
    if user_bio:
        response = requests.post(
            "http://127.0.0.1:5000/ranked_stories", json={"bio": user_bio}
        )

        if response.status_code == 200:
            ranked_stories = response.json()
            st.subheader("Ranked Stories:")

            for story in ranked_stories:
                title = story.get("title", "No Title")
                url = story.get("url", "#")
                st.markdown(f"[{title}]({url})")
        else:
            st.error(response.json().get("error"))
    else:
        st.warning("Please enter a bio.")
