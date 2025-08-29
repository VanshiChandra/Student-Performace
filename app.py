from flask import Flask, render_template, request
import pandas as pd
from src.pipeline.predict_pipeline import PredictPipeline

app = Flask(__name__)
predict_pipeline = PredictPipeline()

# Landing page
@app.route("/")
def index():
    return render_template("index.html")

# Form page
@app.route("/home")
def home():
    return render_template("home.html")

# Prediction route
@app.route("/predictdata", methods=["POST"])
def predict_data():
    data = {
        "gender": [request.form["gender"]],
        "race_ethnicity": [request.form["race_ethnicity"]],
        "parental_level_of_education": [request.form["parental_level_of_education"]],
        "lunch": [request.form["lunch"]],
        "test_preparation_course": [request.form["test_preparation_course"]],
        "math_score": [float(request.form["math_score"])],
        "reading_score": [float(request.form["reading_score"])],
        "writing_score": [float(request.form["writing_score"])],
        "science_score": [float(request.form["science_score"])],
        "history_score": [float(request.form["history_score"])],
        "english_score": [float(request.form["english_score"])],
        "computer_score": [float(request.form["computer_score"])]
    }

    input_df = pd.DataFrame(data)
    results = predict_pipeline.predict(input_df)

    return render_template("home.html", results=results)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
