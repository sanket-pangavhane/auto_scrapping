from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller
from browser_use import BrowserConfig, Browser
from models import Session, BackgroundVerification,Employee  # Import your SQLAlchemy session and model
from datetime import datetime
import json
from extract_result import gpt_extraction
from file_download import download_pdf
from datetime import datetime,timedelta

app = Flask(__name__)
CORS(app) 

rules = """
Follow the rules for optimal extractions.
Rule1 : Understand that most of the sites use Date Format : yyyy-MM-dd so prefer this format.
Rule2 : When Data extraction is done dont perform any unspecified steps.
Rule3 : Extract all data fields key value though any of them is NULL.
Rule4 : Prefer the JSON format for data extraction result if multiple in JSON list.
Rule5 : Dont extract any irrelavant data until specified. 
Rule6 : Return JSON data in format for ujsportal site  :
 [
  {
    \"docket_number\": \"<Enter docket number here>\",
    \"primary_participant\": \"<Enter primary participant's name here>\",
      \"docket_sheet\": \"<Enter URL to docket sheet>\",
      \"court_summary\": \"<Enter URL to court summary>\"
    
  },
  {
    \"docket_number\": \"<Enter docket number here>\",
    \"primary_participant\": \"<Enter primary participant's name here>\",
      \"docket_sheet\": \"<Enter URL to docket sheet>\",
      \"court_summary\": \"<Enter URL to court summary>\"
    
  }
]
Rule 7:Extract the data from site and share in above JSON format if multiple share list of JSONs

"""

config = BrowserConfig(
    headless=True,
    disable_security=True
)

browser = Browser(config=config)


# Calculate dates
# end_date = datetime.today().date()
# start_date = end_date - timedelta(days=4 * 365)  # Approximate 4 years

# START_DATE = start_date.strftime('%d/%m/%Y')
# END_DATE = end_date.strftime('%d/%m/%Y')



@app.route('/get_records', methods=['POST'])
def run_agent():
    session  = Session()
    
    
    data = request.get_json()
    # employee_id = int(data.get("employee_id"))  
    # first_name = data.get("first_name")
    # last_name = data.get("last_name")
    # name = first_name+' '+last_name
    
    eid = data.get("employee_id")
    
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=3 * 365)  # Approximate 3 years
    
    
    
    employee = session.query(
    Employee.id, 
    Employee.first_name, 
    Employee.last_name
    ).filter(Employee.id == eid).first()

        
    employee_id = employee.id
    first_name = employee.first_name
    last_name = employee.last_name
    name = first_name+' '+last_name
    
    # print(name)
    

    START_DATE = start_date.strftime('%Y-%m-%d')
    END_DATE = end_date.strftime('%Y-%m-%d')
    task = f"""
        "Visit https://ujsportal.pacourts.us/CaseSearch.Search for {name} with the date range from {START_DATE} to {END_DATE}.(Date format: yyyy-MM-dd. 
        Use calendar icon, click month/year at top-left to navigate quickly.)Immediately perform the search without waiting for input.
        From the results grid, scroll fully down to load all records.
        Extract and provide the docket_sheet links for each record listed.And stop"
    """
    
    if not employee_id or not first_name:
        return jsonify({'error': 'No Data  provided for user.'}), 400

    async def run_agent_task(task):

        agent = Agent(
            browser=browser,
            task=task + rules,
            llm=ChatOpenAI(model="gpt-4o",),
            # controller=controller        
        )
        result = await agent.run()
        return result

    result = asyncio.run(run_agent_task(task))
    result = result.final_result()  # Extract the final result
    extracted_data = gpt_extraction(result)
    
 
    
    
    
    path = ''
    for result in extracted_data:
        docket_number = result.get("docket_number")
        docket_sheet = result.get("docket_sheet")
        # primary_participant = result.get("primary_participant")

        path = download_pdf(docket_number=docket_number, name=first_name+last_name, url=docket_sheet)
        
        existing_case = session.query(BackgroundVerification).filter_by(verification_file_path=path).first()

        
        if existing_case:
            # print("Record already exists. Skipping insertion.")
            continue
        else:
            # print("Inserting new record.")
            new_case = BackgroundVerification(
                employee_id=employee_id,
                verification_file_path=path,
                file_type="pdf"
            )

            session.add(new_case)
            session.commit()
            # print("Simplified data inserted successfully!")
   
    return {"msg":"Data stored successfully"}

if __name__ == '__main__':
    app.run(debug=True)
