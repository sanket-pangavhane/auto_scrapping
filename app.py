from models import Session, BackgroundVerification, Employee
from flask import Flask, request, jsonify, send_file
from browser_use import BrowserConfig, Browser, Agent
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from flask_cors import CORS
from extract_result import gpt_extraction
from file_download import download_pdf
import asyncio
import os

app = Flask(__name__)
CORS(app)

# Browser Configuration
config = BrowserConfig(headless=True, disable_security=True)
browser = Browser(config=config)

@app.route('/get_records', methods=['POST'])
def run_agent():
    """Process employee background verification request and store results."""
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

    # Check if background verification already exists
    existing_case = session.query(BackgroundVerification).filter_by(employee_id=employee_id).first()

    if existing_case:
        return jsonify({"msg": "success"}), 200

    START_DATE = start_date.strftime('%Y-%m-%d')
    END_DATE = end_date.strftime('%Y-%m-%d')

    # Corrected task with escaped curly braces
    task = f"""
    Visit https://ujsportal.pacourts.us/CaseSearch.
        Search for {name} with the date range from {START_DATE} to {END_DATE}.
        (Date format: yyyy-MM-dd. Use calendar icon, click month/year at top-left to navigate quickly.)
        Immediately perform the search without waiting for input.
        From the results grid, scroll fully down to load all records.
        Extract and provide the docket_sheet links for each record listed. And stop

    **Mandatory Rules for Accurate Data Extraction:**
    1. Ensure extracted dates strictly follow the yyyy-MM-dd format.
    2. Do NOT perform any additional actions beyond what's explicitly instructed.
    3. Extract all fields as key-value pairs, including NULL values if present.
    4. Present extracted data strictly as a JSON list—even if only one record is found.
    5. Do NOT include irrelevant information.

    **Required JSON Output Format (Concrete Example):**
    [
        {{
            "docket_number": "MJ-05219-CR-0000199-2024",
            "primary_participant": "Newman, David",
            "docket_sheet": "/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000199-2024&dnh=0gLs2%2B7%2Fh5J9hO0mmhrJAQ%3D%3D"
        }},
        {{
            "docket_number": "MJ-05219-CR-0000050-2023",
            "primary_participant": "Smith, John",
            "docket_sheet": "/Report/MdjDocketSheet?docketNumber=MJ-05219-CR-0000050-2023&dnh=1fLs1%2B8%2Fh2X9hQ5mkdrKBR%3D%3D"
        }}
    ]

    **Final Task Execution Steps:**
    - After performing the search, scroll down fully to load all available records.
    - Extract and immediately return **only** the docket_number, primary_participant, and docket_sheet URL for each listed record.
    - Once data extraction is complete, stop immediately. Do NOT perform any further steps.
    """

    async def run_agent_task(task):
        agent = Agent(
            browser=browser,
            task=task,
            llm=ChatOpenAI(model="gpt-4o"),
        )
        result = await agent.run()
        return result

    result = asyncio.run(run_agent_task(task))
    result = result.final_result()
    extracted_data = gpt_extraction(result)
    # print("********************************************************************************************************")
    # print(extracted_data)
    
    if extracted_data.get("msg") == "empty":
        return jsonify({"msg": "success","data":"No records found"}), 200
    
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

    session.commit()

    return jsonify({"msg": "success"}), 200


@app.route('/download-file/<int:employee_id>', methods=['GET'])
def download_report(employee_id):
    """Download background verification report for given employee ID."""
    download_folder = "/home/sanket/Desktop/browser_use_poc/upload/"

    try:
        session = Session()
        file = session.query(BackgroundVerification).filter_by(employee_id=employee_id).first()

        if not file:
            return jsonify({"error": "No pdf found for this employee"}), 404

        file_path = os.path.join(download_folder, file.verification_file_path)

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found on the server"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
