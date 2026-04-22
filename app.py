from flask import Flask, request, jsonify
import requests
import uuid
import os

app = Flask(__name__)
# 这里先不用改，后面拿到地址再回来替换
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://临时地址")
SUBMISSION_EVENT_FUNC_URL = os.getenv("SUBMISSION_EVENT_FUNC_URL", "http://临时地址")

@app.route('/api/workflow/submit', methods=['POST'])
def submit_workflow():
    data = request.get_json()
    submission_id = str(uuid.uuid4())
    
    create_data = {
        "submission_id": submission_id,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "poster_filename": data.get("poster_filename", "")
    }
    create_resp = requests.post(f"{DATA_SERVICE_URL}/api/submission/create", json=create_data)
    if create_resp.status_code != 200:
        return jsonify({"code": 500, "msg": "Failed to create submission"}), 500
    
    try:
        requests.post(SUBMISSION_EVENT_FUNC_URL, json={
            "submission_id": submission_id,
            "submission_data": create_data
        }, timeout=2)
    except Exception as e:
        app.logger.error(f"Trigger event function failed: {str(e)}")
    
    return jsonify({
        "code": 200,
        "msg": "Submission accepted",
        "submission_id": submission_id
    }), 200

@app.route('/api/workflow/result/<submission_id>', methods=['GET'])
def get_result(submission_id):
    resp = requests.get(f"{DATA_SERVICE_URL}/api/submission/{submission_id}")
    return jsonify(resp.json()), resp.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)