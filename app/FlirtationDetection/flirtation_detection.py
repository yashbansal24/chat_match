import pandas as pd
pd.set_option("display.max_colwidth", 200)
pd.set_option("display.max_columns", 200)

# from google import files
# uploaded = files.upload()

df = pd.read_csv("./app/FlirtationDetection/flirting_rated.csv")

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
