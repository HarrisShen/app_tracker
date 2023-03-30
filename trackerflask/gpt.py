'''
Code for interacting with GPT-3 in Python.

To run this you need to 
* first visit openai.com and get an APIkey, 
* which you export into the environment as shown in the shell code below.
* next create a folder and put this file in the folder as gpt.py
* finally run the following commands in that folder

On Mac
% pip3 install openai
% export APIKEY="......."  # in bash
% python3 gpt.py

On Windows
% pip install openai
% $env:APIKEY="....." # in powershell
% python gpt.py
'''
import openai
import tiktoken

class GPT():
    ''' make queries to gpt from a given API '''

    def __init__(self, apikey, model_engine="text-davinci-003", temperature=0.5):
        ''' store the apikey in an instance variable '''
        self.apikey = apikey
        # Set up the OpenAI API client
        openai.api_key = apikey

        # Set up the model and prompt
        self.model_engine = model_engine

        self.temperature = temperature

    def get_response(self, prompt):
        ''' Generate a GPT response '''
        for chunk in self.split_prompt(prompt):
            completion = openai.Completion.create(
                engine=self.model_engine,
                prompt=chunk,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=self.temperature,
            )
        response = completion.choices[0].text
        return response
    
    def split_prompt(self, prompt, chunk_size=2048, overlap=128):
        ''' Split a prompt into chunks of a given size '''
        encoding = tiktoken.get_encoding("p50k_base")
        tokens = encoding.encode(prompt)

        for i in range(0, len(tokens), chunk_size - overlap):
            yield encoding.decode(tokens[i: i + chunk_size])
