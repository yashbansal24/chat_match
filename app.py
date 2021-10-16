import pandas as pd
pd.set_option("display.max_colwidth", 200)
pd.set_option("display.max_columns", 200)

# from google import files
# uploaded = files.upload()

df = pd.read_csv("./FlirtationDetection/flirting_rated.csv")

# Extra cleaning
df = df.dropna()

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(max_features=4000)
vectors = vectorizer.fit_transform(df.final_messages)
words_df = pd.DataFrame(vectors.toarray(), columns=vectorizer.get_feature_names())
words_df.head()


X = words_df
y = df.polarity


from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB


# Create and train a random forest classifier
forest = RandomForestClassifier(n_estimators=50)
forest.fit(X, y)


# Create and train a linear support vector classifier (LinearSVC)
svc = LinearSVC()
svc.fit(X, y)


# Create and train a multinomial naive bayes classifier (MultinomialNB)
bayes = MultinomialNB()
bayes.fit(X, y)

def predictFlirtationBonus(convos):

    unknown = pd.DataFrame({'content': convos})
    unknown = unknown.dropna()

    unknown_vectors = vectorizer.transform(unknown.content)
    unknown_words_df = pd.DataFrame(unknown_vectors.toarray(), columns=vectorizer.get_feature_names())
    unknown_words_df.head()

    unknown['pred_forest'] = forest.predict(unknown_words_df)
    unknown['pred_forest_proba'] = forest.predict_proba(unknown_words_df)[:,1]

    # SVC predictions (doesn't support probabilities)
    unknown['pred_svc'] = svc.predict(unknown_words_df)

    # Bayes predictions + probabilities
    unknown['pred_bayes'] = bayes.predict(unknown_words_df)
    unknown['pred_bayes_proba'] = bayes.predict_proba(unknown_words_df)[:,1]

    pred1 = unknown['pred_forest_proba'].tolist()
    pred2 = unknown['pred_svc'].tolist()
    pred3 = unknown['pred_bayes_proba'].tolist()
    
    bonus1 = sum(pred1)/len(pred1)
    bonus2 = sum(pred2)/len(pred2)
    bonus3 = sum(pred3)/len(pred3)

    """
        ##Forest##
            Predicted non-flirting	Predicted flirting
            Is non-flirting	0.936317	0.063683
            Is flirting	0.608696	0.391304

        ##SVC##
        	Predicted non-flirting	Predicted flirting
            Is non-flirting	0.974182	0.025818
            Is flirting	0.637681	0.362319

        ##Bayes##
            Predicted non-flirting	Predicted flirting
            Is non-flirting	0.998279	0.001721
            Is flirting	0.782609	0.217391
    """ 
    
    return .5*bonus1 + .1*bonus2+ .4*bonus3

# Importing the required libraries
import keras
import numpy as np
from nltk.tokenize import word_tokenize
from keras.layers import *
import nltk
nltk.download('punkt')


def padd(arr):
    for i in range(100-len(arr)):
        arr.append('<pad>')
    return arr[:100]
  

vocab_f ='./EmotionAnalysisModel/glove.6B.50d.txt'
embeddings_index = {}
with open(vocab_f,encoding='utf8') as f:
    for line in f:
        values = line.rstrip().rsplit(' ')
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs

# call the padd function for each sentence in feel_arr
def prepare_chat(feel_arr):
    feel_arr=[word_tokenize(sent) for sent in feel_arr]

    for i in range(len(feel_arr)):
        feel_arr[i]=padd(feel_arr[i])
    return feel_arr


reconstructed_model = keras.models.load_model("EmotionAnalysisModel")


def find_emotion(chats):
    embedded_feel_arr=[] 
    for each_sentence in prepare_chat(chats):
        embedded_feel_arr.append([])
        for word in each_sentence:
            if word.lower() in embeddings_index:
                embedded_feel_arr[-1].append(embeddings_index[word.lower()])
            else:
                embedded_feel_arr[-1].append(np.float32([0]*50))

    X=np.asarray(embedded_feel_arr)

    map_result = { 0:'anger',  1:'disgust' , 2:'fear', 3:'guilt', 4:'joy', 5:'sadness', 6:'shame' }
    result = reconstructed_model.predict(np.asarray(embedded_feel_arr))
    max_values = [(x.argmax(),x[x.argmax()]) for x in result]
    return [(map_result[maxidx] == 'joy',maxval) for maxidx, maxval in max_values ]



from flask import Flask
from flask import jsonify, request
from flask_cors import CORS, cross_origin
from datetime import datetime
from flask import render_template
from EmotionAnalysisModel import find_emotion
from FlirtationDetection import predictFlirtationBonus
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

if __name__ == "__main__":
    app.run()