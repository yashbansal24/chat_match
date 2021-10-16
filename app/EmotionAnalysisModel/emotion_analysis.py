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
  

vocab_f ='./app/EmotionAnalysisModel/glove.6B.50d.txt'
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


reconstructed_model = keras.models.load_model("./app/EmotionAnalysisModel")


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
