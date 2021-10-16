from flask import Flask
from datetime import datetime
from flask import render_template
from EmotionAnalysisModel.emotion_analysis import find_emotion
from FlirtationDetection.flirtation_detection import predictFlirtationBonus

app = Flask(__name__)

@app.route("/")
def home():
    return render_template(
        "home.html"
    )

@app.route("/hello/")
def hello_there(name = None):
    chats = [
        'I am groot',
        'Hey baby',
        'I want to date you']
    resp = find_emotion(chats)
    percentage = 0
    positives = list(filter(lambda r: r[0] == True, resp))
    for _,p in positives:
        percentage+=p
    percentage/=len(positives)
    flirtBonus = predictFlirtationBonus(chats)

    percentage = min( percentage + flirtBonus , 1)
    percentage*=100.0
    print(percentage)
    return render_template(
        "home.html",
        percentage=percentage,
        chats=chats
    )