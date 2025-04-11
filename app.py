from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 🔍 Plagiarism check using n-grams
def plagiarism(t1, t2, threshold=0.6, n=5):
    if not t1 or not t2:
        return False
    t1_ngrams = set(t1[i:i+n] for i in range(len(t1) - n + 1))
    t2_ngrams = set(t2[i:i+n] for i in range(len(t2) - n + 1))
    if not t1_ngrams:
        return False
    common = t1_ngrams.intersection(t2_ngrams)
    score = len(common) / len(t1_ngrams)
    return score >= threshold

# 🧠 Compare student answers
def check_plagiarism_between_students(assignments, threshold=0.6, n=5):
    results = []
    students = list(assignments.keys())

    for i in range(len(students)):
        for j in range(i + 1, len(students)):
            s1 = students[i]
            s2 = students[j]
            for question in assignments[s1]:
                a1 = assignments[s1].get(question, "")
                a2 = assignments[s2].get(question, "")
                if plagiarism(a1, a2, threshold, n):
                    pair = sorted([s1, s2])
                    if pair not in results:
                        results.append(pair)
                        break
    return results

# 🏠 Simple home route
@app.route("/")
def home():
    return jsonify({"message": "Plagiarism detection API is running!"})

# 📥 Plagiarism checker route
@app.route("/plagiarism", methods=["POST"])
def detect_plagiarism():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        assignments = data.get("assignments")
        threshold = float(data.get("threshold", 0.6))
        ngram_size = int(data.get("ngram_size", 5))

        if not isinstance(assignments, dict):
            return jsonify({"error": "'assignments' must be a nested dictionary"}), 400

        results = check_plagiarism_between_students(assignments, threshold, ngram_size)

        return jsonify({
            "plagiarism_pairs": results,
            "threshold": threshold,
            "ngram_size": ngram_size
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Run app locally or in Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
