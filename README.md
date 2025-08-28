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
4. Query filtering capabilities through user edit panel.

## Start looking for your dream vacation !
1. First join or login.
2. Search your dream vacation in natural language.
3. Browse the suggestions from our AI algorithm !

## How it works ?
1. We create our JSON of properties with information as per the project requirements with the provided prompt.
2. The info in these properties are then parsed and sent our in a chat request to Llama-3 to copywrite and create custom listing descriptions.
3. We use HuggingFace embedding models to vectorize the text and inser into our FAISS database.
4. We pass the user query, vectorize, and retrieve relevant queries to your search input !

## Disclaimer:
This project contains portions of code that were developed with the assistance of artificial intelligence tools, including GitHub Copilot and OpenAI’s ChatGPT. These tools were used to generate code suggestions and documentation. All AI-generated content has been reviewed, modified, and integrated by the project authors, who bear responsibility for the final implementation.
