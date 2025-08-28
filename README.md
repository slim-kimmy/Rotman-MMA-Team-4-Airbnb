# Rotman-MMA-Team-4-Airbnb
Project for RSM8431Y
## Setup 
0. Clone repo at submission branch.    
    ```git clone -b submission --single-branch https://github.com/slim-kimmy/Rotman-MMA-Team-4-Airbnb.git```
1. Create a virtual environment named venv by running.
    ```python -m venv venv```
2. Navigate to the same directory as the ```requirements.txt``` file and run.
    ```pip install -r requirements.txt```
3. After you have isntalled the necessary packages navigate to the source folder and run in the terminal.
    ```streamlit run frontend.py```
4. Now run the image API by creating a new terminal in the source folder and run.
    ```uvicorn image_api:app```

## Features
1. Streamlit based frontend with scrollable images.
2. Read, Write, Insert, Delete capabilities for the user database.
3. Transformer based embeddings support natural language search capabilities.
4. Llama 4 transforms property details into rich, semantic summaries. FAISS vector search performs a rapid Approximate Nearest Neighbor (ANN) search to find the most semantically relevant properties.
5. Query filtering capabilities through user edit panel. A final filter aligns results with specific user constraints (e.g., budget, group size).

## Start looking for your dream vacation !
1. First join or login.
2. Search your dream vacation in natural language.
3. Browse the suggestions from our AI algorithm !

## How it works ?
### 1. Property Data Creation
- We create our JSON of properties with information as per the project requirements with the provided prompt.
### 2. Natural-Language Summaries with Llama 3
- The info in these properties are then parsed and sent out in a chat request to Llama-3 to copywrite and create custom listing descriptions. The model synthesizes features, tags, and locations to create rich and natural-language summaries, capturing each property’s unique character beyond simple keyword matching.
### 3. Embedding and FAISS Database
- We use HuggingFace embedding models to vectorize the text and inser into our FAISS database. FAISS retrieves the most semantically relevant property vectors in milliseconds, ensuring high-speed and exact matches.
### 4. Query Matching and Filtering
- We pass the user query, vectorize, and retrieve relevant queries. Then applying our two-step filtering (budget and group size) gives the highly relevant and actionable recommendations to your search input!
  
## Known Issue
### Insufficient Filtered Results
The current search algorithm returns the top 50 results without filtering for budget or capacity. This can lead to fewer recommendations for users. We plan to consider these constraints before similarity searching by using **FAISS IndexIDMap**.
### Performance Lag
The current search process includes an embedding generation step for a sleep on every search. This function was intended as a one-time pre-processing script, but is currently a critical source of performance latency. We are actively working to optimize this process to achieve a competitive search speed for each execution.

## Disclaimer:
This project contains portions of code that were developed with the assistance of artificial intelligence tools, including GitHub Copilot and OpenAI’s ChatGPT. These tools were used to generate code suggestions and documentation. All AI-generated content has been reviewed, modified, and integrated by the project authors, who bear responsibility for the final implementation.
