import secrets
from app import app
from app.views import match_percentage
from flask import  json, jsonify, render_template, request, Response
import pymongo
client = pymongo.MongoClient("mongodb+srv://admin:MongoAdmin#12345@applications.stgyn.mongodb.net/textmatch?retryWrites=true&w=majority")
db = client.test
mydb = client["textmatch"]
mycol = mydb["User"]
analyticscol = mydb["analytics"]

@app.route("/generate",methods=["GET"])
def render_generate():
    return render_template(
        "api.html"
    )

@app.route("/generate-token", methods=["POST"])
def generate():
    secret_token = secrets.token_urlsafe(16)
    user_details =  {"id": "", "email": "", "name": "", "apikey": secret_token, "creation_date": ""}
    mycol.insert_one(user_details)
    return jsonify({'token': secret_token})

@app.route("/get-match", methods=["POST"])
def getDetails():
    secret_token = request.form.get('token')
    user_details =  {"id": "", "email": "", "name": "", "apikey": secret_token, "creation_date": ""}
    u = mycol.find_one(user_details)
    
    if not u:
        return Response("{'success':'false'}", status=403, mimetype='application/json')
    if u.get('blocked'):
        return Response("{'success':'false'}", status=429, mimetype='application/json')
    

    token = u.get('apikey')
    
    if not add_or_update_analytics(token):
        newvalues = { "$set": { "blocked": True } }
        mycol.update_one(u, newvalues)
        return Response("{'success':'false'}", status=429, mimetype='application/json')
    else:
        percentage = match_percentage(request.form.get('data'))
        return jsonify({'success': True, 'percentage': percentage})

def add_or_update_analytics(token):
    analysis = analyticscol.find_one({ 'apikey': token })
    record = {'apikey': token, 'counter': 1}
    if not analysis:
        analyticscol.insert_one(record)
    else:
        new_count = analysis.get('counter') + 1
        newvalues = { "$set": { "counter": new_count } }
        analyticscol.update_one(analysis, newvalues)
        if new_count >= 5:
            return False
    return True