import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import pycountry 
import geopandas
import pycountry 
import geopandas
import io
import base64
from bs4 import BeautifulSoup
import requests
from pytrends.request import TrendReq
import time
    
def retrieve_google(query):
    """
    Method to retrieve urls from medium.com through google crawl
    """
    headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    url="https://www.google.com/search?q=" + query
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, "lxml")
    try:
        return soup.find_all("a", "gL9Hy")[0].text
    except IndexError:
        return query


def visualize_network(keys, values, count):
    keys=keys[-50:]
    values=values[-50:]
    plt.figure(figsize=(13, 10))
    # add nodes
    G = nx.Graph() # Create a graph object called G
    node_list = keys  # the nodes are the hashtags

    dimension={}

    for i in node_list: # create dictionary that contains the recurrence of every hashtag, which will define the dimension of the node
        for j in i:
            dimension[j]=count[j]  


    for i in node_list:  # for loop to add nodes to plot
        for j in i:
            G.add_node(j, size=dimension[j]*5)

    pos=nx.spring_layout(G, seed=7) # define layout
    max_dim = max(dimension.values())
    node_size=[(i*100/max_dim)*80 for i in dimension.values()] 
    color= [i for i in sns.color_palette()]*4
    nx.draw_networkx_nodes(G, pos, node_color=color[:len(G)], node_size=node_size, alpha=0.7)  # draw the nodes
    labels = {}
    for i in node_list:
        for j in i:
            labels[str(j)] =str(j)
    nx.draw_networkx_labels(G,pos,labels,font_size=16)
    #edges
    for i, el in enumerate(keys):
        G.add_edge(el[0],el[1], weight=values[i])
    all_weights = []
    #  gather all the weights
    for (node1,node2,data) in G.edges(data=True):
        all_weights.append(data['weight']) #we'll use this when determining edge thickness

    # get unique weights
    unique_weights = list(set(all_weights))

    # plot the edges - one by one
    for weight in unique_weights:
        # Form a filtered list with just the weight you want to draw
        weighted_edges = [(node1,node2) for (node1,node2,edge_attr) in G.edges(data=True) if edge_attr['weight']==weight]
        #4 e. I think multiplying by [num_nodes/sum(all_weights)] makes the graphs edges look cleaner
        width = weight*len(node_list)*8.0/sum(all_weights)
        nx.draw_networkx_edges(G,pos,edgelist=weighted_edges,width=width, alpha=0.3)
    #Plot the graph
    plt.axis('off')
    plt.title('trend relationships')
    plt.style.use('seaborn-dark')

    # return bytes to decode in the html template
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data


def visualize_trends(count):
    dictio = {k: v for k, v in sorted(count.items(), key=lambda item: item[1])}

    # extract 4 most relevant topics and correct them
    topics =list(dictio.keys())[-4:]
    topics = [retrieve_google(i) for i in topics]


    # retrieve trends data
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([topics[0]], timeframe='all') 
    trends_norm = pytrends.interest_over_time()
    trends_norm = pd.DataFrame(trends_norm)
    

    for i in topics[1:]:
        pytrends.build_payload([i], timeframe='all') 
        trend = pytrends.interest_over_time()

        try:
            trends_norm[i] = trend[i]    
        except:
            pass  
 

    # trends plot

    fig, ax = plt.subplots(2, figsize=(13, 10))
    for i in list(set(topics)):
        try:
            ax[0].plot(trends_norm[i], label = i)
        except:
            pass
    ax[0].set_ylabel("Relative score (%)")
    ax[0].set_title("Relative trends")

    # magnitude plot    
    pytrends.build_payload(kw_list=topics, timeframe='all') 
    trends = pytrends.interest_over_time()
    for i in list(set(topics)):
        try:
            ax[1].plot(trends[i], label = i)
        except:
            pass
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('Absolute score (%)')
    ax[1].legend()
    ax[1].set_title("Absolute trends")
    plt.style.use('ggplot')

    # return bytes to decode in the html template

    buf_trends = io.BytesIO()
    fig.savefig(buf_trends, format="png")
    data = base64.b64encode(buf_trends.getbuffer()).decode("ascii")
    return data


def visualize_worldmap(topic):
    """
    Visualize the popularity of the search term on a world map
    """
    #provide your search terms
    time.sleep(1)
    kw_list=[topic]#, domain]
    pytrends = TrendReq()

    #search interest per region
    pytrends.build_payload(kw_list, timeframe='all')
    regiondf = pytrends.interest_by_region()

    df = pd.DataFrame(regiondf[topic])#, domain]]
    df['country'] = df.index
    df = df.reset_index().drop(['geoName'], axis=1)

    # generate country code  based on country name 
    plt.style.use('seaborn-dark')
    plt.figure(figsize=(13, 10))

    def alpha3code(column):
        CODE=[]
        for country in column:
            try:
                code=pycountry.countries.get(name=country).alpha_3
                CODE.append(code)
            except:
                CODE.append('None')
        return CODE

    # create a column for code 
    df['CODE']=alpha3code(df['country'])

    # first let us merge geopandas data with our data
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

    # rename the columns so that we can merge with our data
    world.columns=['pop_est', 'continent', 'name', 'CODE', 'gdp_md_est', 'geometry']
    
    # then merge with our data 
    merge=pd.merge(world,df,on='CODE')

    # last thing we need to do is - merge again with our location data which contains each country’s latitude and longitude
    location=pd.read_csv('https://raw.githubusercontent.com/melanieshi0120/COVID-19_global_time_series_panel_data/master/data/countries_latitude_longitude.csv')
    merge=merge.merge(location,on='name').sort_values(by=topic,ascending=False).reset_index()
    merge.plot(column=topic, scheme="quantiles",
            figsize=(25, 20),
            legend=True,cmap='PuBu')

    plt.title('World map for search term {}'.format(topic),fontsize=25)
    plt.xticks([]),plt.yticks([])

    # return bytes to decode in the html template
    buf_map = io.BytesIO()
    plt.savefig(buf_map, format="png")
    data = base64.b64encode(buf_map.getbuffer()).decode("ascii")
    return data
   
