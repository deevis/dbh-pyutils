import requests
import time
import json

class TextGenerationWebuiAPI():
    def __init__(self, model_name: str = None, debug=False, api_host="http://127.0.0.1:5000"):
        self.llm_api_host = api_host
        self.llm_model_endpoint = "/api/v1/model"
        self.llm_generate_endpoint = "/api/v1/generate"
        self.debug = debug
        self.llm_model_name = self.get_llm_name()
        # output in yellow to make it stand out
        print(f"\033[93m{api_host} - currently loaded model {self.llm_model_name}\033[0m")
        if model_name is not None and self.llm_model_name != model_name:
            # make sure the requested model is available
            models = self.get_llm_models()
            if model_name not in models:
                # dump available models
                print(f"Available models: {models}")
                raise Exception(f"Model {model_name} not available")
            # load the requested model
            self.set_llm_model(model_name)

        self.last_query_time = None

    def get_llm_name(self):
        url = f'{self.llm_api_host}{self.llm_model_endpoint}'
        response = requests.get(url)
        return response.json()['result']

    def set_llm_model(self, model_name):
        url = f'{self.llm_api_host}{self.llm_model_endpoint}'
        payload = {'action': 'load', 'model_name': model_name}
        # display in yellow to make it stand out
        print(f"\033[93mLoading model {model_name}...\033[0m")
        response = requests.post(url, json=payload)
        return response.json()['result']

    def get_llm_models(self):
        url = f'{self.llm_api_host}{self.llm_model_endpoint}'
        response = requests.post(url, json={'action': 'list'})
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
        if self.debug:
            print(f"\nResponse: {r.json()}")    
        return r.json()['results'][0]['text']

if __name__ == "__main__":
    from dbh_pyutils.dbh_prompt_builder import PromptBuilder
    import time

    llm_model_names = [
        "TheBloke_MythoLogic-L2-13B-GPTQ_gptq-8bit-64g-actorder_True",
        "TheBloke_OpenOrca-Platypus2-13B-GPTQ_gptq-8bit-128g-actorder_True",
        "TheBloke_guanaco-13B-SuperHOT-8K-GPTQ",
        "TheBloke_vicuna-13B-v1.5-16K-GPTQ_gptq-8bit-128g-actorder_True",
    ]

    for llm_model_name in llm_model_names:
        tgwa = TextGenerationWebuiAPI(model_name=llm_model_name, debug=True)
        prompt_builder = PromptBuilder(tgwa)
        text = "We were in the middle of our tournament when my friend John said he found a body in the bushes over there I ran over there because I'm a healing monk to try and help but obviously my magic wasn't strong enough because the dude Body was missing a head. So my friend decided to try to use a necromancer spell which didn't work Which I knew it wouldn't and apparently we contaminated the crime scene because that spell uses a lot of glitter"
        prompt_builder.infer_summary(text)
        print("Sleeping for 5 seconds...")
        time.sleep(5)
