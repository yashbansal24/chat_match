from flask import Flask
from flask import jsonify, request
from flask_cors import CORS, cross_origin
from datetime import datetime
from flask import render_template
from EmotionAnalysisModel.emotion_analysis import find_emotion
from FlirtationDetection.flirtation_detection import predictFlirtationBonus
import json
import math

app = Flask(__name__)

@app.route("/")
def home():
    return render_template(
        "home.html"
    )

@app.route("/hello", methods=["POST"])
@cross_origin()
def hello_there(name = None):
    chats = json.loads(request.form.get('data'))
    resp = find_emotion(chats)
    percentage = 0
    positives = list(filter(lambda r: r[0] == True, resp))
    for _,p in positives:
        percentage+=p
    if len(positives) >= 1:
        percentage/=len(positives)
    flirtBonus = predictFlirtationBonus(chats)

    percentage = min( percentage + flirtBonus , 1)
    percentage*=100.0
    return jsonify({ "percentage" : math.floor(percentage) })