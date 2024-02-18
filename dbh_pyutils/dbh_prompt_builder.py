class PromptBuilder():
    def __init__(self, llm_api, debug=False):
        self.llm_api = llm_api
        self.debug = debug
        if llm_api is not None:
            self.llm_model_name = self.llm_api.get_llm_name()

    def infer_hashtags(self, text, sub_type=None, promptOnly=False, count: int = 5):
        prompt = self.build_prompt(text, "What are the 5 most appropriate hashtags for the provided content?  Please return only the 5 best hashtags starting with # and each word capitalized.", "Opinionated answer:")
        if promptOnly == True:
            return prompt
        response = self.llm_api.query_llm(prompt)
        # cleanup response
        response = response.replace(",", "")
        response = response.replace(".", "")
        response = response.replace("</s>","")
        hashtags = self.extract_hashtags(response)
        hashtags_string = ", ".join(hashtags[:count])
        return hashtags_string

    def infer_people(self, text, sub_type=None, promptOnly=False):
        prompt = self.build_prompt(text, "What are the full names of people mentioned in the provided content?  Names must have both first name and last name please.", "Answer:")
        if promptOnly == True:
            return prompt

        response = self.llm_api.query_llm(prompt)
        return response

    def infer_places(self, text, sub_type=None, promptOnly=False):
        prompt = self.build_prompt(text, "What famous locations are mentioned in the provided content?", "Answer:")
        if promptOnly == True:
            return prompt
        response = self.llm_api.query_llm(prompt)
        return response

    def infer_title(self, text, sub_type = 'clever', promptOnly=False):
        prompt = self.build_prompt(text, f"What would a {sub_type} title of the provided content be?  Please only tell me the title.", "Answer:")
        if promptOnly == True:
            return prompt        
        response = self.llm_api.query_llm(prompt)
        return response

    def infer_summary(self, text, sub_type = 'concise', promptOnly=False):
        prompt = self.build_prompt(text, f"What would a {sub_type} summary of the provided content be?", "Answer:")
        if promptOnly == True:
            return prompt
        response = self.llm_api.query_llm(prompt)
        return response

    # Based on query results, extract the hashtags into a list
    def extract_hashtags(self, text):
        # initializing hashtag_list variable
        hashtag_list = []

        # if we have a bunch of lines, each with a numbered hashtag, we need to split the text into lines
        if "\n" in text and "#" not in text:
            text = text.split("\n")
            for line in text:
                # if the line starts with a number and a space, we can assume it's a hashtag
                if len(line) > 2 and line[0].isdigit() and line[1] == ' ':
                    # adding the word to the hashtag_list
                    hashtag_list.append(line[2:])

        else:
            # splitting the text into words
            for word in text.split():
                # checking the first character of every word
                if word[0] == '#' and len(word) > 2:
                    # adding the word to the hashtag_list
                    hashtag_list.append(word[1:])
        return hashtag_list

    def build_prompt(self, context, question, response_type = 'Factual answer:'):
        # Original template
        # template = f"""Consider: {context}

        # Question: {question}
        # {response_type}"""
        # return template
        
        if self.llm_model_name == 'TheBloke_MythoLogic-L2-13B-GPTQ_gptq-8bit-64g-actorder_True':
            # alpaca template
            # Good for: TheBloke_MythoLogic-L2-13B-GPTQ_gptq-8bit-64g-actorder_True
            template = f"""You are an expert at summarizing text precisely as instructed.  Below is a transcript from a media file. Please consider it when evaluating instructions:
{context}
###Instruction:
{question}

###Response: """
        elif self.llm_model_name.startswith('TheBloke_guanaco'):
            # 'TheBloke_guanaco-33B-GPTQ' 
            # 'TheBloke_guanaco-13B-SuperHOT-8K-GPTQ'
            # guanaco template - not working very well :()
            template = f"""
You are an expert at summarizing text precisely as instructed.  Below is a transcript from a media file. Please consider it when evaluating instructions:
<content>
{context}
</content>

Human: {question}
Assistant:
"""
        elif self.llm_model_name == 'TheBloke_manticore-13b-chat-pyg-GPTQ':
            template = f"""USER: 
You are an expert at summarizing text precisely as instructed.  Below is a transcript from a media file. Please consider it when evaluating instructions: 

<content>
{context}
</content>

{question}

ASSISTANT: """
        elif self.llm_model_name.startswith('TheBloke_vicuna'):
            template = f"""### Instruction:
You are an expert at summarizing text precisely as instructed.  Below is a transcript from a media file. Please consider it when evaluating instructions:

<content>
{context}
</content>

{question}

### Response:"""
        elif self.llm_model_name.startswith('TheBloke_OpenOrca'):
            template = f"""### Instruction:
You are an expert at summarizing text precisely as instructed.  
Consider this content:  
<content>
{context}
</content>

{question}

End your response with <|end_of_turn|>

### Response:"""
        else:
            raise "Cannot find template for this model: {self.llm_model_name}"    

        if self.debug:
            print("-"*80)
            print(template)      
            print("-"*80)
        
        return template
    
        # Vicuna template
        # template = f"""{whisper_txt}

        # USER: What would be the 5 most appropriate hashtags for the provided content?
        # ASSISTANT:"""

        # alpaca-with-input
        # template = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
        
        # ### Instruction:
        # Please find the 5 most appropriate hashtags for the provided content?
        
        # ### Input:
        # {whisper_txt}

        # ### Response:
        # """
if __name__ == "__main__":
    pb = PromptBuilder(None, debug=True)
    for hashtags in ["\n1 paraprosdokians\n2 mitchhedberg\n3 stephenking\n4 homersimpson\n5 groucho_marx",
                     "\n1. #Paraprosdokians\n2. #MitchHedberg\n3. #StephenKing\n4. #HomerSimpson\n5. #GrouchoMarx",
                     "\n#paraprosdokians\n#mitchhedberg\n#stephenking\n#homersimpson\n#grouchomarx"]:
        extracted = pb.extract_hashtags(hashtags)
        print(extracted)

