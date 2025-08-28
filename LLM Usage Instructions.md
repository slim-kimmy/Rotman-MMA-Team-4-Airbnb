# LLM Usage Instruction
Our system use **Meta llama-4** through *OpenAI API (Groq)*, to create a summary for Airbnb-styled property listings.
The property summary is embedded from FAISS to improve search.

## Signup API Key
0. To get an API key, you need to register for OpenRouter/Groq account first.
1. Then generate a ```.env``` file by right click in folder & change the file format to ```.env```.
2. When you have the API Key, copy & replace the key in ```.env``` file.
3. After you have installed the necessary packages navigate to the source folder and run in the terminal.
    ```streamlit run frontend.py```
4. Now run the image API by creating a new terminal in the source folder and run.
    ```uvicorn image_api:app```

## Explain how it works in the code
`create_page_content()` builds prompt from structured fields:
  ```prompt = f"""
Summarize the following property for a vacation rental listing:
Location: {property_item['location']}
Type: {property_item['type']}
Features: {', '.join(property_item['features'])}
Tags: {', '.join(property_item['tags'])}
Group size: {property_item['capacity']}
Price per night: {property_item.get('price_per_night', 'N/A')}
"""
```
  * The piece of code for ``` create_page_content() ``` is extracting the generated strings for property summary
  * Like stated above, summary is embedded and stored in FAISS

## Other Notes
  * LLM is used one time per property. This ensures the search is fast & does not reach the limit.

  * Caching is enabled for performance. If the property remains unchanged, the cached summary is reused. If the property is updated, the LLM is called again and the summary is updated.
