# query_reformulation_warmup

## Overview

The **Warmup API** and **Warmup Frontend** are components of a Streamlit and Flask application designed to fetch and rank stories from Hacker News based on a user's bio. I've utilized sentence embeddings to rank stories similar to the user's bio.

## Project Structure

- **warmup_api.py**: Contains the backend logic for fetching stories from Hacker News and processing user input.
- **warmup_frontend.py**: The streamlit frontend that interacts with the user, collects input, and displays ranked stories.
- **warmup_app.py**: Streamlit app that is used for hosting on streamlit cloud.

## Local Installation
To run the app locally, simply execute "bash start.sh" in your terminal, which will install the requirements, and run the flask and streamlit files. You can then proceed to the localhost streamlit address to access the application, which will in turn call the API using POST method to return results.

## Design Decisions

* The application uses caching (duration 60 minutes) to store the top 500 stories returned. The cache duration is set to ensure that data is refreshed periodically while minimizing unnecessary API calls. 

* Given the user bio, we a create a list of documents where the first document is the user bio text. The next 500 list documents are a concatenation of each stories title and text. This was done to minimize loss of context since the title can be thought of as a concise summary and the text can be thought of as the full extract of information. This leads to us capturing more semantic information, as well as covering the edge case of a story not having a title or text.

* This list of documents is then passed to be encoded via the "all-MiniLM-L6-v2" model. This model was chose because it requires relatively lesser memory, and offers fast inference while also offering high quality sentence embeddings.

* I've used sentence embeddings to capture the meaning of the sentence, rather than using word embeddings to focus on individual words. This was done since it improves the contextual understanding, handles ambiguity better, allows for an optimized solution since we're not creating embeddings for every single word. I also tried using the topic modeling approach via Latent Dirichlet Allocation, but that required that I pass the number of topics as a parameter to the model, and in our case that is variable depending upon the length of the text, so I choose not to choose this as the final model.

* Once we have the sentence embeddings, similarities between them are calculated using cosine similarity. I also tried out euclidean distance measure, but found the results to be better when using the former approach.

* I could also have used an LLM to extract user interests from each hacker news story, and convert them into embeddings and store them in a vector database. Then given the user bio as input, I would again call the LLM to extract interests, convert to embeddings and use the vector db to return most similar stories. Since would likely perform better, but I choose not to follow this option since we had to optimize for development time.