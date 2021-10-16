from app import app
import json
import math
from datetime import datetime

from flask import  jsonify, render_template, request
from flask_cors import cross_origin
from app.EmotionAnalysisModel.emotion_analysis import find_emotion
from app.FlirtationDetection.flirtation_detection import predictFlirtationBonus


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
