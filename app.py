from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/recommend', methods=['POST'])
def recommend_endpoint():
    print("Received a request for recommendations.")
    return jsonify({
        "status": "success",
        "message": "Recommendation endpoint is working."
    })

@app.route('/explain', methods=['POST'])
def explain_endpoint():
    print("Received a request for an explanation.")
    return jsonify({
        "status": "success",
        "message": "Explanation endpoint is working."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)