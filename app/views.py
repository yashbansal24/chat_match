from app import app
import json
import math
from datetime import datetime

from flask import  jsonify, render_template, request
from flask_cors import cross_origin
from app.FlirtationDetection.flirtation_detection import predictFlirtationBonus
from app.simple_sentiment_analysis import simpleSentimentAnalysis

@app.route("/")
def home():
    return render_template(
        "home.html"
    )

@app.route("/hello", methods=["POST"])
@cross_origin()
def hello_there(name = None):
    chats = json.loads(request.form.get('data'))
    chats = list(map(lambda chat: chat.strip(), chats))
    chats = list(filter(lambda chat: len(chat) > 0, chats))
    percentage = 0
    if chats:
        resp = simpleSentimentAnalysis(chats)
        for result in resp:
            percentage += result.polarity * min(1 , .5 + result.subjectivity ) # threshold for subjectivity is .5
        percentage/=len(resp)
        flirtBonus = predictFlirtationBonus(chats)

        percentage = min( percentage + flirtBonus , 1)
        percentage*=100.0
    return jsonify({ "percentage" : math.floor(percentage) })
