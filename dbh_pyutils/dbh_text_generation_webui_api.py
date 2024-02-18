import requests
import time
import json
import hashlib   # for caching
import os

class TextGenerationWebuiAPI():
    def __init__(self, model_name: str = None, debug=False, api_host="http://127.0.0.1:5000", cache_dir=None):
        self.llm_api_host = api_host
        
        # The legacy Kobold API that was being used has been deprecated
        # in favor of the text generation webui OpenAI API
        # self.llm_model_endpoint = "/api/v1/model"
        # self.llm_generate_endpoint = "/api/v1/generate"
       
        self.llm_generate_endpoint = "/v1/completions"

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
        self.cache_dir = cache_dir
        if self.cache_dir is not None:
            print(f"Using cache directory {self.cache_dir}")
            os.makedirs(self.cache_dir, exist_ok=True)

        self.last_query = None              # keep this around for debugging should an error occur
        self.last_llm_params = None         # keep this around for debugging should an error occur
        self.last_query_time = None         # keep this around for tracking performance should anyone care

    def get_llm_name(self):
        # https://github.com/oobabooga/text-generation-webui/blob/78380759904eb294e57fa2f287122c8e3866f236/extensions/openai/script.py#L268
        url = f'{self.llm_api_host}/v1/internal/model/info'
        response = requests.get(url)
        return response.json()['model_name']

    def set_llm_model(self, model_name):
        # https://github.com/oobabooga/text-generation-webui/blob/78380759904eb294e57fa2f287122c8e3866f236/extensions/openai/script.py#L280
        url = f'{self.llm_api_host}/v1/internal/model/load'
        payload = {'model_name': model_name}
        # display in yellow to make it stand out
        print(f"Loading model: \033[93m{model_name}...\033[0m")
        # keep track of how long the model loading takes
        start = time.time()
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        print(f"Model loaded in: {time.time() - start} seconds")
        # output the response in yellow to make it stand out
        print(f"Response: \033[93m{response}\033[0m")
        # show the text of the response
        print(f"Response text: \033[93m{response.text}\033[0m")
        return response.text

    def get_llm_models(self):
        # https://github.com/oobabooga/text-generation-webui/blob/78380759904eb294e57fa2f287122c8e3866f236/extensions/openai/script.py#L274
        url = f'{self.llm_api_host}/v1/internal/model/list'
        response = requests.get(url)
        return response.json()['model_names']
    
    def get_llm_params(self):
        # TODO: make this configurable via a config file
        return {
            "temperature": 0.85,    # Primary factor to control randomness of outputs. 0 = deterministic (only the most likely token is used). Higher value = more randomness.
            "top_p": 0.6,           # If not set to 1, select tokens with probabilities adding up to less than this number. Higher value = higher range of possible random results.
            "top_k": 40,            # Similar to top_p, but select instead only the top_k most likely tokens. Higher value = higher range of possible random results.
            "typical_p": 1.0,       # If not set to 1, select only tokens that are at least this much more likely to appear than random tokens, given the prior text.
            "rep_pen": 1.18,        # Exponential penalty factor for repeating prior tokens. 1 means no penalty, higher value = less repetition, lower value = more repetition.
            "no_repeat_ngram_size": 0,  # If not set to 0, specifies the length of token sets that are completely blocked from repeating at all. 
                                        #      Higher values = blocks larger phrases, lower values = blocks words or letters from repeating. Only 0 or high values are a good idea in most cases.
            "penalty_alpha": 0.0,   # Contrastive Search is enabled by setting this to greater than zero and unchecking "do_sample". It should be used with a low value of top_k, for instance, top_k = 4.


            # "stopping_strings": ['</s>'],

            # "max_length": 500,
            "max_tokens": 500,
            "max_new_tokens": 350,
            "do_sample": "True",
            "min_length": 0,
            "num_beams": 1,
            "length_penalty": 1,
            "early_stopping": "False",
            "seed": -1
        }
    
    def query_llm(self, query, llm_params=None):
        self.last_query = query
        if self.debug == True:
            print('='*80)
            print(f'QUERY: \n\n{query}\n\n')
        # getting good results withehartford_WizardLM-7B-Uncensored…
        
        # !!! even better results with thebloke_wizard-mega-13B-GPTQ  ( 5.05 perplexity)
        # !!! even, EVEN BETTER results with TheBloke_guanaco-33B-GPTQ
        #
        # Parameters are mirroring LLaMA-Precise 
        if llm_params is None:
            body = self.get_llm_params()
        else:
            body = llm_params
        self.last_llm_params = body

        if self.debug == True:
            # dump params as formatted json
            print("PARAMS:")
            print(json.dumps(body, indent=4))
            
        body['prompt'] = query
        if self.cache_dir is not None:
            # build an md5 of the entire body to use as a cache key
            cache_key = hashlib.md5(json.dumps(body, sort_keys=True).encode('utf-8')).hexdigest()
            # check if we have a cached response
            cache_file = f"{self.cache_dir}/{cache_key}.json"
            try:
                with open(cache_file, 'r') as f:
                    print(f"Using cached response from {cache_file}")
                    return json.load(f)['results'][0]['text']
            except FileNotFoundError:
                pass
        start = time.time()

        url = f"{self.llm_api_host}{self.llm_generate_endpoint}"
        r = requests.post(url, json=body)
        # {'results': [{'text': ' #OklahomaCityBombingConspiracyTheories #FBI #ATF #DOJ #CIA #SPLC #NSN #USArmy'}]}
        self.last_query_time = time.time() - start
        print(f"Inferring: {url} - status code: {r.status_code} in {self.last_query_time} seconds") 
        if self.debug:
            print(f"\nResponse: {r.json()}")    
        # cache the response
        if self.cache_dir is not None:
            with open(cache_file, 'w') as f:
                json.dump(r.json(), f)
        # The response has changed and now looks like:
        # {
        #     "id": "conv-1708235523222310400",
        #     "object": "text_completion",
        #     "created": 1708235523,
        #     "model": "TheBloke_OpenOrca-Platypus2-13B-GPTQ_gptq-8bit-128g-actorder_True",
        #     "choices": [
        #         {
        #             "index": 0,
        #             "finish_reason": "stop",
        #             "text": "\nIt is difficult to predict an exact date for the achievement of Artificial General Intelligence (AGI). The development of AGI will largely depend on advancements in various fields such as computer science, machine learning, neuroscience, and engineering. Some experts believe it could be achieved within the next few decades, while others think it might take much longer. As a prophet, I can't provide an exact date, but it's essential to stay informed about the ongoing research and progress in AI to understand how quickly we are moving towards AGI.",
        #             "logprobs": {
        #                 "top_logprobs": [
        #                     {}
        #                 ]
        #             }
        #         }
        #     ],
        #     "usage": {
        #         "prompt_tokens": 53,
        #         "completion_tokens": 123,
        #         "total_tokens": 176
        #     }
        # }                
        return r.json()['choices'][0]['text']

if __name__ == "__main__":
    from dbh_pyutils.dbh_prompt_builder import PromptBuilder
    import time

    llm_model_names = [
        "TheBloke_OpenOrca-Platypus2-13B-GPTQ_gptq-8bit-128g-actorder_True",
        "TheBloke_guanaco-13B-SuperHOT-8K-GPTQ",
        "TheBloke_MythoLogic-L2-13B-GPTQ_gptq-8bit-64g-actorder_True",
        "TheBloke_vicuna-13B-v1.5-16K-GPTQ_gptq-8bit-128g-actorder_True",
    ]

    for llm_model_name in llm_model_names:
        tgwa = TextGenerationWebuiAPI(model_name=llm_model_name, debug=True)
        prompt_builder = PromptBuilder(tgwa)
        text = """
        We were in the middle of our tournament when my friend John said he found a body in the bushes over there 
        I ran over there because I'm a healing monk to try and help but obviously my magic wasn't strong enough because the dude Body was missing a head. 
        So my friend decided to try to use a necromancer spell which didn't work 
        Which I knew it wouldn't and apparently we contaminated the crime scene because that spell uses a lot of glitter
        """
        summary = prompt_builder.infer_summary(text)
        print("="*80)
        print(f"Summary:\n{summary}")
        print("="*80)
        print("Sleeping for 5 seconds...")
        time.sleep(5)
