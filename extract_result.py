
from openai import OpenAI
import json

client = OpenAI()

def gpt_extraction(text):
    
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
    {
        "role": "system",
        "content": """
            You are an expert JSON data extraction assistant tasked with extracting structured JSON data from provided text input.

            ### Instructions:
            - **Only extract relevant JSON data** as specified below and ignore all other unrelated text.
            - If multiple JSON entries are present, return a list of JSON objects.
            - If no relevant structured data or JSON is found, return exactly:
            {
                "msg": "empty"
            }

            ### Expected Output Format:
            [
                {
                    "docket_number": "<docket_number_value>",
                    "primary_participant": "<participant_name>",
                    "docket_sheet": "<URL_to_docket_sheet>"
                },
                {
                    "docket_number": "<docket_number_value>",
                    "primary_participant": "<participant_name>",
                    "docket_sheet": "<URL_to_docket_sheet>"
                }
            ]

            ### Extraction Rules:
            1. Prioritize extracting data from clearly identified JSON structures if present. Example:
            "results": [{"key": "value"}, {...}]
            - Convert any existing structured data into the above-specified format.

            2. If structured JSON is **not explicitly present**, but the text clearly mentions:
            - docket numbers (e.g., MJ-05219-CR-0000199-2024),
            - primary participant names (e.g., Newman, David),
            - docket_sheet URLs (links containing "/Report/MdjDocketSheet?..."),
            
            then explicitly extract these details and format them into the above-specified JSON structure.

            3. If the input text lacks identifiable docket numbers, participant names, or docket_sheet URLs, return exactly:
            {
                "msg": "empty"
            }

            ### Example Scenario:

            **Input:**
            '''
            Some data extracted
            results":[{"docket_number":"MJ-05219-CR-0000199-2024","primary_participant":"Newman, David","docket_sheet":"/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024&dnh=0gLs2%2B7%2Fh5J9hO0mmhrJAQ%3D%3D"}]
            Data extracted successfully.
            '''

            **Output:**
            [
                {
                    "docket_number": "MJ-05219-CR-0000199-2024",
                    "primary_participant": "Newman, David",
                    "docket_sheet": "/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024&dnh=0gLs2%2B7%2Fh5J9hO0mmhrJAQ%3D%3D"
                }
            ]

            ### Example Scenario (No structured JSON, but clear text data):

            **Input:**
            '''
            New court records found:
            1. Docket: MJ-05219-CR-0000199-2024, Name: Newman, David, Sheet: /Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024
            '''

            **Output:**
            [
                {
                    "docket_number": "MJ-05219-CR-0000199-2024",
                    "primary_participant": "Newman, David",
                    "docket_sheet": "/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024"
                }
            ]

            ### Example Scenario (No relevant data):

            **Input:**
            '''
            No relevant records found for this individual.
            '''

            **Output:**
            {
                "msg": "empty"
            }
            """
                },
                {
                    "role": "user",
                    "content": f"{text}"
                }
            ]  )

    response = completion.choices[0].message.content
    json_str = response.strip('```json\n').strip('```')   
    data_list = json.loads(json_str)
    
    return data_list











