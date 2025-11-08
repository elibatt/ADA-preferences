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

polarity, subjectivity = polarity_subjectivity("Splintered as the story is between its two extreme settings, The Midnight Sky is an enjoyable Friday-night viewing experience, but misses the potential to expand on its themes of isolation and optimism in a memorable way.")
print(subjectivity)