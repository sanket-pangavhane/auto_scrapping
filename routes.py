from models import Session, BackgroundVerification,Employee  # Import your SQLAlchemy session and model
from flask import Flask, request, jsonify,send_file
from browser_use import BrowserConfig, Browser
from datetime import datetime,timedelta
from langchain_openai import ChatOpenAI
from flask_cors import CORS
from browser_use import Agent
from datetime import datetime
from extract_result import gpt_extraction
from file_download import download_pdf
import asyncio
import os

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
Expected Output : 
 [
  {
    \"docket_number\": \"<Enter docket number here>\",
    \"primary_participant\": \"<Enter primary participant's name here>\",
      \"docket_sheet\": \"<Enter URL to docket sheet>\",
 
    
  },
  {
    \"docket_number\": \"<Enter docket number here>\",
    \"primary_participant\": \"<Enter primary participant's name here>\",
      \"docket_sheet\": \"<Enter URL to docket sheet>\",
    
  }
]
Rule 7:Extract the data from site and share in above JSON format if multiple share list of JSONs

"""

config = BrowserConfig(
    headless=False,
    disable_security=True
)

browser = Browser(config=config)

@app.route('/get_records', methods=['POST'])
def run_agent():
    session = Session()

    data = request.get_json()
    eid = data.get("employee_id")
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=3 * 365)

    # Query employee details
    employee = session.query(Employee).filter(Employee.id == eid).first()

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    employee_id = employee.id
    name = f"{employee.first_name} {employee.last_name}"

    # Early check if background verification already exists
    existing_case = session.query(BackgroundVerification).filter_by(employee_id=employee_id).first()

    if existing_case:
        return jsonify({"msg": "success"}), 200

    START_DATE = start_date.strftime('%Y-%m-%d')
    END_DATE = end_date.strftime('%Y-%m-%d')

    task = f"""
        Visit https://ujsportal.pacourts.us/CaseSearch.
        Search for {name} with the date range from {START_DATE} to {END_DATE}.
        (Date format: yyyy-MM-dd. Use calendar icon, click month/year at top-left to navigate quickly.)
        Immediately perform the search without waiting for input.
        From the results grid, scroll fully down to load all records.
        Extract and provide the docket_sheet links for each record listed. And stop
    """

    async def run_agent_task(task):
        agent = Agent(
            browser=browser,
            task=task + rules,
            llm=ChatOpenAI(model="gpt-4o",temperature=0.2),
        )
        result = await agent.run()
        return result

    result = asyncio.run(run_agent_task(task))
    result = result.final_result()
    extracted_data = gpt_extraction(result)

    # Insert each new background verification without redundant existence checks
    for result in extracted_data:
        docket_number = result.get("docket_number")
        docket_sheet = result.get("docket_sheet")
        path = download_pdf(docket_number=docket_number, name=f"{employee.first_name}{employee.last_name}", url=docket_sheet)

        new_case = BackgroundVerification(
            employee_id=employee_id,
            verification_file_path=path,
            file_type="pdf"
        )
        session.add(new_case)

    session.commit()  # Commit once after the loop finishes

    return jsonify({"msg": "success"}), 200




@app.route('/download-file/<int:employee_id>', methods=['GET'])
def download_report(employee_id):
    """Download the latest report for the given employee_id."""
    download_folder = "/home/sanket/Desktop/browser_use_poc/upload/"

    # print("********************REQUEST RECEIVED**************************")
    # print(employee_id)
    try:
        session = Session()
        
        # Query the database to find the background verification file for the given employee_id
        file = session.query(BackgroundVerification).filter_by(employee_id=employee_id).first()

        # If no file is found for this employee, return an error
        if not file:
            return jsonify({"error": "No pdf found for this employee"}), 404

        # Get the file path from the BackgroundVerification record
        file_path = os.path.join(download_folder, file.verification_file_path)

        # Ensure the file exists before attempting to send it
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found on the server"}), 404

    except Exception as e:
        # Return an error message if an exception occurs
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
