import tweepy
import itertools
from collections import Counter


class TwitterScraper():
    def __init__(self, twitter_key, keyword:str, domain:str = ""):
        self.keyword = keyword
        self.domain = domain
        self.twitter_key = twitter_key
            
    def retrieve_data(self):
        """
        Method to retrieve 1000 tweets from twitter with tweepy
        """

        # preprocess query
        if self.domain != "":
            query = self.keyword + " " + self.domain
        else:
            query = self.keyword

        # retrieve tweets with tweepy   
        client = tweepy.Client(bearer_token=self.twitter_key)
        tweets_lst = tweepy.Paginator(client.search_recent_tweets, query=query,
                                    max_results=100).flatten(limit=1000)  

        # extract the text
        tweets_text=[tweet.text for tweet in tweets_lst]
        print("number of tweets retrieved: ", len(tweets_text)) 
        print(type(self.extract_tags(tweets = tweets_text)))

        extract_tags_var = self.extract_tags(tweets = tweets_text)
        return self.counter(tweets_text), extract_tags_var[0], extract_tags_var[1]


    def counter(tweets):
        """
        Method to count hasthags in tweets
        """
        hashtags=[]

        # for every tweet extract the words the contain "#" and append them to hashtags
        for tweet in tweets:
            for word in tweet.split():
                if "#" in word and "..." not in word: # append only hashtags that are not truncated
                    hashtags.append(word.lower().strip("#").strip(","))
                    
        print("number of hastags: ", len(hashtags))
        return Counter(hashtags)


    def extract_tags(self, tweets):
        """
        Method to create list of lists of hashatgs (for each tweet)
        """

        hashtags=[]

        # for every tweet create a list containing only the hashtags and append it to hashtags
        for tweet in tweets:
            tweet_hashtags=[]
            for word in tweet.split():
                if "#" in word:
                    tweet_hashtags.append(word.lower().strip("#").strip(",").strip(":").strip("/"))
            hashtags.append(tweet_hashtags)
    
        return self.count_occurrences(hashtags)


    def count_occurrences(self, hashtags):
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





