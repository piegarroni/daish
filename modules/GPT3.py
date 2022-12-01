import openai
import os


def ask(quest, key):
    openai.api_key = key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=quest,
        temperature=0,
        max_tokens=128,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    text = response["choices"][0]["text"]
    return(text)


def summarize(input_text, key):

    openai.api_key = key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt= f"Given a transcript, summarize it: \n\nTranscript: {input_text}",        
        temperature=0,
        max_tokens=80,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    summary = response["choices"][0]["text"]
    return(summary)




def retrieve_keywords(input_text, key): 
    openai.api_key = key
    response = openai.Completion.create(
      model="text-davinci-002",
      prompt= f"Given a transcript, extract keywords: \n\nTranscript: {input_text}",
      temperature=0.3,
      max_tokens=60,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0
    )

    keywords = response["choices"][0]["text"]
    return keywords

    
def clean_keywords(keywords):   
    keywords2 = []
    for i in keywords:
        i=i.strip()
        if "\n" in i:
            i=i.replace("-", "").strip().lower().split("\n")
        else:
            i=i.strip().lower().split(",")
        i = [j.split("(")[0].strip().strip("") for j in i]
        keywords2.append(i)
    
    return keywords2

