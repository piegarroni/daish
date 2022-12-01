import openai

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





    

