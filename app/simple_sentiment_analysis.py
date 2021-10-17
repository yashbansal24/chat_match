from textblob import TextBlob

def simpleSentimentAnalysis(chats):
    return [TextBlob(chat).sentiment for chat in chats]
        