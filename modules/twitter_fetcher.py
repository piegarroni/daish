import tweepy
import itertools
from collections import Counter
import os
import openai
import pytrends
from pytrends.request import TrendReq
import matplotlib.pyplot as plt


def retrieve_data(keyword, key, domain = ""):
    """
    Method to retrieve 1000 tweets from twitter with tweepy
    """
    if domain != "":
        query = keyword + " " + domain
    else:
        query = keyword
        
        
    client = tweepy.Client(bearer_token=key)
    tweets = tweepy.Paginator(client.search_recent_tweets, query=query,
                                max_results=100).flatten(limit=1000)    

    tweets_lst=[tweet.text for tweet in tweets]
    print("number of tweets retrieved: ", len(tweets_lst)) 
    
    return tweets_lst


def counter(tweets):
    """
    Method to count hasthags in tweets
    """
    hashtags=[]
    for tweet in tweets:
        for word in tweet.split():
            if "#" in word:
                hashtags.append(word.lower().strip("#").strip(","))
                
    print("number of hastags: ", len(hashtags))
    return Counter(hashtags)



def extract_tags(tweets):
    """
    Method to create list of lists of hashatgs (for each tweet)
    """

    hashtags=[]
    for tweet in tweets:
        tweet_hashtags=[]
        for word in tweet.split():
            if "#" in word:
                tweet_hashtags.append(word.lower().strip("#").strip(",").strip(":").strip("/"))
        hashtags.append(tweet_hashtags)
 
    return hashtags


def count_occurrences(hashtags):
    """
    Method to count the co-occorrunces of each tag, and sort them
    """

    combinations_count=[list(itertools.combinations(tags_tweet, 2)) for tags_tweet in hashtags]
 
    flat = [x for sublist in combinations_count for x in sublist] #flatten list to 1 dimension

    occurrences = Counter(flat)

    sorted_dict = {}
    sorted_keys = sorted(occurrences, key=occurrences.get)  

    for w in sorted_keys:
        sorted_dict[w] = occurrences[w]

    keys=list(sorted_dict.keys())
    values=list(sorted_dict.values())
    
    return keys, values




def extract_topics(topics, key):
    """
    Method to extract most co-occurring topics 
    """
    openai.api_key = key    
    words=[i.strip("#").lower() for i in topics]
            
    words2=[]
    for i in words:
        #if len(i)>2:
        if len(i)>3:
            response = openai.Completion.create(
              model="text-davinci-002",
              prompt="Given a string, insert spaces: \n\n" + i,
              temperature=0.3,
              max_tokens=15,
              top_p=1.0,
              frequency_penalty=0.8,
              presence_penalty=0.0
            )

            words2.append(response["choices"][0]["text"])
        else:
            words2.append(i)
            
    words2=[i.replace('\n\n', '') for i in words2]

    return list(set(words2))


