import requests
import time
import json

class TextGenerationWebuiAPI():
    def __init__(self, model_name: str = None, debug=False):
        self.llm_api_host = "http://127.0.0.1:5000"
        self.llm_model_endpoint = "/api/v1/model"
        self.llm_generate_endpoint = "/api/v1/generate"
        self.debug = debug
        self.llm_model_name = self.get_llm_name()
        if model_name is not None and self.llm_model_name != model_name:
            raise Exception(f"Model name mismatch: {self.llm_model_name} != {model_name}")
        self.last_query_time = None

    def get_llm_name(self):
        url = f'{self.llm_api_host}{self.llm_model_endpoint}'
        response = requests.get(url)
        return response.json()['result']

    def get_llm_params(self):
        return {
            "temperature": 0.85,    # Primary factor to control randomness of outputs. 0 = deterministic (only the most likely token is used). Higher value = more randomness.
            "top_p": 0.1,           # If not set to 1, select tokens with probabilities adding up to less than this number. Higher value = higher range of possible random results.
            "top_k": 40,            # Similar to top_p, but select instead only the top_k most likely tokens. Higher value = higher range of possible random results.
            "typical_p": 1.0,       # If not set to 1, select only tokens that are at least this much more likely to appear than random tokens, given the prior text.
            "rep_pen": 1.18,        # Exponential penalty factor for repeating prior tokens. 1 means no penalty, higher value = less repetition, lower value = more repetition.
            "no_repeat_ngram_size": 0,  # If not set to 0, specifies the length of token sets that are completely blocked from repeating at all. 
                                        #      Higher values = blocks larger phrases, lower values = blocks words or letters from repeating. Only 0 or high values are a good idea in most cases.
            "penalty_alpha": 0.0,   # Contrastive Search is enabled by setting this to greater than zero and unchecking "do_sample". It should be used with a low value of top_k, for instance, top_k = 4.


            # "stopping_strings": ['</s>'],

            "max_length": 300,
            "max_new_tokens": 250,
            "do_sample": "True",
            "min_length": 0,
            "num_beams": 1,
            "length_penalty": 1,
            "early_stopping": "False",
            "seed": -1
        }
    
    def query_llm(self, query):
        if self.debug == True:
            print('='*80)
            print(f'QUERY: \n\n{query}\n\n')
        # getting good results withehartford_WizardLM-7B-Uncensored…
        
        # !!! even better results with thebloke_wizard-mega-13B-GPTQ  ( 5.05 perplexity)
        # !!! even, EVEN BETTER results with TheBloke_guanaco-33B-GPTQ
        #
        # Parameters are mirroring LLaMA-Precise 
        body = self.get_llm_params()
        body['prompt'] = query
        start = time.time()
        url = f"{self.llm_api_host}{self.llm_generate_endpoint}"
        r = requests.post(url, json=body)
        # {'results': [{'text': ' #OklahomaCityBombingConspiracyTheories #FBI #ATF #DOJ #CIA #SPLC #NSN #USArmy'}]}
        self.last_query_time = time.time() - start
        print(f"Inferring: {url} - status code: {r.status_code} in {self.last_query_time} seconds") 
        # print(f"Response: {r.json()}")    
        return r.json()['results'][0]['text']
    