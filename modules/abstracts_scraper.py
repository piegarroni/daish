from bs4 import BeautifulSoup
import requests
import re



def retrieve_arxiv(query, number):
    """
    Method to retrieve titles and abstracts from arxiv.com
    """
    
    base_url = "https://arxiv.org/search/?searchtype=all&query=" + query +"&abstracts=show&size=" + str(number) +"&order=" 
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, "html.parser")
    titles=[title.text for title in soup.find_all("p", "title is-5 mathjax")]
    texts=[text.text for text in soup.find_all("span", "abstract-full has-text-grey-dark mathjax")]
    urls=[url.text for url in soup.find_all("p", "list-title is-inline-block")]
    
    """ 
    # if articles are less than 30 unrestrict search and append
    if len(titles) > 30:
        query = query.replace('"', '')
        base_url = "https://arxiv.org/search/?searchtype=all&query=" + query +"&abstracts=show&size=" + number +"&order=" 
        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, "html.parser")
        titles = titles + [title.text for title in soup.find_all("p", "title is-5 mathjax")]
        texts = texts + [text.text for text in soup.find_all("span", "abstract-full has-text-grey-dark mathjax")]
        urls = urls + [url.text for url in soup.find_all("p", "list-title is-inline-block")]
    """
  
    titles=[i.strip() for i in titles]
    texts=[i.strip().replace("\n        △ Less", "") for i in texts if i !='']
    urls=["https://arxiv.org/pdf/" + str(i).replace(":", " ").replace("\'", ' ').split()[1]  + ".pdf" for i in urls]
    
    # retrieve repos from text with regex
    repos=[]
    for text in texts:
        repo = re.findall("(?P<url>https?://[^\s]+)", text)
        if repo != []:        
            repos.append(repo[0].strip("."))
        else:
            repos.append([])
        
    print("number of articles retrieved: ", len(titles))
    return titles, texts, urls, repos


def retrieve_pubmed(query, number): 
    """
    Method to retrieve titles and abstracts from pubmed.ncbi.nlm.nih.gov (medical articles)
    """
    query = query.replace(" ", "%20") 
    query = '"' + query + '"'
    base_url = "https://pubmed.ncbi.nlm.nih.gov/?term=" + query + "&format=abstract&page" + str(1)
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, "html.parser")
    titles=[title.text for title in soup.find_all("h1", "heading-title")]
    texts=[text.text for text in soup.find_all("div", "abstract-content selected")]
    urls=[text.text for text in soup.find_all("span", "identifier doi")]
  
    titles=[i.strip() for i in titles]
    urls=["https://doi.org/" + str(i).replace(" ", "").replace("\n", '').replace("DOI:", "") for i in urls]

    print("number of articles retrieved: ", len(titles))
    return titles, texts, urls


def retrieve_core(query, number): 
    """
    Method to retrieve titles and abstracts from core.ac.uk 
    """
    query = query.replace(" ", "+") 
    query = '"' + query + '"'
    base_url = "https://core.ac.uk/search?q=" + query + "&page=" + str(1) 
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, "html.parser")
    titles=[title.text for title in soup.find_all("h3", "styles-title-1k6Ib")]
    texts=[text.text for text in soup.find_all("div", "styles-content-35LN7")]
    urls=[str(url).split('"') for url in soup.find_all("h3", "styles-title-1k6Ib")]
    
    urls2=[]
    
    for i in urls:
        for j in i:
            if "https" in j:
                urls2.append(j)
    
    print("number of articles retrieved: ", len(titles))
    return titles, texts, urls2



