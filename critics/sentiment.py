import requests
from textblob import TextBlob

#polarità calcolata con API
def polarity_subjectivity(sentence):
    # Create a TextBlob object
    blob = TextBlob(sentence)

    # Get polarity and subjectivity
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Return the polarity and subjectivity as floats
    return polarity, subjectivity


