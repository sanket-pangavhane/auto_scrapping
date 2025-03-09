
from openai import OpenAI
import json

client = OpenAI()

def gpt_extraction(text):
    
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": """You are a helpful assistant and prepares a well structred list of json.
                                    Ignore all other string from the input string and only get the specified format from string 
                                    If multiple json return list of jsons.
                                    If no relevant information in text the return  json in below format : 
                                    {
                                       "msg":"empty"
                                    }
                                    
                                    Input : '''Some data extracted 
                                    ''' JSON 
                                    "results":[{'some data in key values'},{....}]
                                    '''
                                    Data extracted successfully.'''
                                    
                                    
                                    Else :
                                    Expected Output :
                            [
                            {
                                "docket_number": "MJ-05219-CR-0000199-2024",
                                "primary_participant": "Newman, David",
                                "docket_sheet": "/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024&dnh=0gLs2%2B7%2Fh5J9hO0mmhrJAQ%3D%3D",
                                "court_summary": ""
                                },{
                                    "docket_number": "MJ-05219-CR-0000199-2024",
                                "primary_participant": "Newman, David",
                                "docket_sheet": "/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024&dnh=0gLs2%2B7%2Fh5J9hO0mmhrJAQ%3D%3D",
                                "court_summary": "/einowifne/sdwinfeoiwedmowem"
                                }
                            ]       
                            
                            
                            
                                                          
                                """},
        {
            "role": "user",
            "content": f"{text}"
        }
        ]
    )

    response = completion.choices[0].message.content
    json_str = response.strip('```json\n').strip('```')   
    data_list = json.loads(json_str)
    
    return data_list











