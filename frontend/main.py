from flask import Flask, render_template, request
from modules.GPT3 import *
from modules.twitter_fetcher import *
from modules.abstracts_scraper import *
from modules.visualization import *
from dotenv import load_dotenv
load_dotenv()

app=Flask(__name__, static_folder='./static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def main():
    return render_template('search.html')

content = []    
@app.route('/introduction', methods = ['post'])
def introduction():
    if request.method == 'POST':

        topic = request.form['search']
        domain = request.form['domain']

        content.append(topic)

        # retrieving api keys
        openai_key = os.environ.get("openai_api_token")
        twitter_key = os.environ.get("twitter_api_token")

        # querying gpt3
        query = topic # + " (" + domain + ")"
        quest=f"What is " + query + "?" 
        what = "Natural language processing (NLP) is a subfield of linguistics, computer science, information engineering, and artificial intelligence concerned with the interactions between computers and human (natural) languages, in particular how to program computers to process and analyze large amounts of natural language data."
        #what = str(ask(quest, openai_key)).strip()


        quest=f"What topics are related to " + query + "?" 
        what_topics = "Some topics that are related to NLP include: -How to process and analyze text data -How to extract meaning from text -How to generate text -How to build chatbots -How to build language models -How to do sentiment analysis -How to do topic modeling -How to do text classification"
        what_topics = what_topics.replace("-", "\n")
        #what_topics = str(ask(quest, openai_key)).strip()

        quest=f"What are the latest developments of " + query + "?"
        latest = "Some of the latest developments in the field of NLP include: - the use of deep learning for NLP tasks - the use of reinforcement learning for NLP tasks - the use of transfer learning for NLP tasks - the use of natural language processing for predictive maintenance"
        #latest = str(ask(quest, openai_key)).strip()

        tag = "#" + topic.replace(" ", "")
        # retrieve twitter data
        data = retrieve_data(tag, twitter_key, domain)
        count = counter(data)
        hashtags = extract_tags(data)
        keys, values = count_occurrences(hashtags)


        try:
            network_bytes = visualize_network(keys, values, count) # network visualization
            print("NET")
            message_net=""
        except:
            print("FFF")
            network_bytes=""
            message_net = "network plot not available"

        #trends_bytes = visualize_trends(count) 
        try:  # trends visualization
            trends_bytes = visualize_trends(count) 
            print("TRE")
            message_trend=""
        except:
            print("FFF")
            trends_bytes=""
            message_trend = "trend plot not available"
        
        try:  # world maps
            map_bytes1 =visualize_worldmap(topic)
            print("MAP")
        except:
            print("FFF")
            map_bytes1=""

        try:  # world maps
            map_bytes2 =visualize_worldmap(domain)
            print("MAPs")
        except:
            print("FFF")
            map_bytes2=""

            
        return render_template("introduction.html", topic = topic, domain = domain, what= what, what_topics = what_topics, latest = latest, network_bytes = network_bytes, trends_bytes=trends_bytes, map_bytes_topic=map_bytes1, map_bytes_dom=map_bytes2, message_net = message_net, message_trend = message_trend)
    
        

@app.route('/indepth', methods=['GET', 'POST'])
def indepth():
    f = open('pass&keys/openai.txt','r')
    openai_key = f.read()
    topic = content[-1]

    if request.method=='GET':
        term = topic.replace(" ", "+")
        titles, texts, urls, repos = retrieve_arxiv(term, str(50))  # add number of articles repository
        
        # scraping arxiv 
        articles=[]
        for i, text in enumerate(texts[0:5]):
            #articles.append([["title: ", titles[i]], ["summary: ", "this whould be the summary of the abstract, the maximum number of tokens should be around 50, i need to make the list look better"],  ["pdf url: ", urls[i]], ["repository url: ", repos[i]]])   
            articles.append([["title: ", titles[i]], ["summary: ", str(summarize(text, openai_key).strip())],  ["pdf url: ", urls[i]], ["repository url: ", repos[i]]])    

        message = "We found this articles about {} online, here we present a short summary and some more basic information".format(topic)
        return render_template('indepth.html', topic = topic, articles=articles, message = message) 

    if request.method=='POST':
        #input related topic
        related=request.form['p1']
        
        # querying gpt3
        quest=f"Describe the relation between " + topic + " and " + related 
        #relation = "not available"
        relation = str(ask(quest, openai_key)).strip()

        
        # scraping arxiv on relation 
        term = '"' + topic.replace(" ", "+") + '"' + "+" + '"' + related.replace(" ", "+") + '"' 
        titles, texts, urls, repos = retrieve_arxiv(term, str(50))  # add number of articles repository
        relation_articles=[]

        for i, text in enumerate(texts[0:5]):
            relation_articles.append([["title: ", titles[i]], ["summary: ", "not available"],  ["pdf url: ", urls[i]], ["repository url: ", repos[i]]])    
          #  relation_articles.append([["title: ", titles[i]], ["summary: ", str(summarize(text, openai_key).strip())],  ["pdf url: ", urls[i]], ["repository url: ", repos[i]]])    
        message = "We found this articles about the relation of {} and {} online, here we present a short summary and some more basic information".format(topic, related)

        return render_template("indepth.html", topic = topic, related = related, relation=relation, relation_articles = relation_articles, message = message)



def start():
    app.run(debug=True, host='0.0.0.0', port = 5001)


