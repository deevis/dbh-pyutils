import requests
import time
import json
from dbh_pyutils.dbh_text_generation_webui_api import TextGenerationWebuiAPI
from dbh_pyutils.dbh_prompt_builder import PromptBuilder

class VidsquidMarkup():
    def __init__(self, llm_model_name: str, 
                 vidsquid_url: str ="http://192.168.0.43:3143",
                 min_whisper_text_length: int = 200,
                 debug=False):
        self.llm_model_name = llm_model_name
        self.vidsquid_url = vidsquid_url
        self.min_whisper_text_length = min_whisper_text_length
        self.debug = debug
        self.llm_api = None # defer until we know there is work to do
        self.prompt_builder = None # defer until we know there is work to do

    def get_llm_api(self):
        if self.llm_api is None:
            self.llm_api = TextGenerationWebuiAPI(self.llm_model_name, debug=self.debug)
        return self.llm_api

    def get_prompt_builder(self):
        if self.prompt_builder is None:
            self.prompt_builder = PromptBuilder(self.get_llm_api(), debug=self.debug)
        return self.prompt_builder
    
    def get_inference_config(self):
        config = {
            'generating_model_name': self.get_llm_api().get_llm_name(),
            'llm_params': self.get_llm_api().get_llm_params(),
        }
        for template in self.get_inference_template():
            prompt = getattr(self.get_prompt_builder(), template[1])("{TEXT}", template[2], promptOnly=True)
            config[template[0]] = {
                'prompt': prompt,
                'sub_type': template[2]
            }
        return config    
    
    def get_inference_template(self):
        return [
            ['summary_1', 'infer_summary', 'interesting'],
            ['summary_2', 'infer_summary', 'high-level'],
            ['summary_3', 'infer_summary', '5th-grade'],
            ['title_1', 'infer_title', 'imaginative'],
            ['title_2', 'infer_title', 'concise'],
            ['title_3', 'infer_title', 'evocative'],
            ['hashtags_1', 'infer_hashtags', None],
        ]
    
    def is_work_for_model(self):
        endpoint = f'videos/list_no_ai_markup_for_model_videos'
        url = f"{self.vidsquid_url}/{endpoint}?generating_model_name={self.llm_model_name}&min_whisper_txt_length={self.min_whisper_text_length}"
        print(f"Checking for work at: {url}")
        r = requests.get(url)
        result = r.json()
        return result['count'] > 0

    # Will find videos that have no AI markup and generate it
    def do_ai_markup(self):
        print(f"Using model: {self.llm_model_name}")
        endpoint = f'videos/list_no_ai_markup_for_model_videos'
        url = f"{self.vidsquid_url}/{endpoint}?generating_model_name={self.llm_model_name}&min_whisper_txt_length={self.min_whisper_text_length}"
        print(f"Getting videos needing tagging from: {url}")
        r = requests.get(url)
        result = r.json()
        # {
        # count: 3912,
        # min_whisper_txt_length: 200,
        # video_ids: [
        # 6,
        # 7,
        print(f"Got {result['count']} videos needing tagging")
        count = 0
        for video_id in result['video_ids']:
            count += 1
            # if count > 1:
            #     break
            print("="*80)
            print(f"\n\n{count}/{result['count']} - Video[{video_id}]")
            r = requests.get(f"{self.vidsquid_url}/videos/{video_id}.json")
            # print(f"Status code: {r.status_code}")
            data = r.json()
            whisper_txt = data['whisper_txt']
            print(f'Whisper text[{len(whisper_txt)} chars]: {whisper_txt}')
            if len(whisper_txt) >= self.min_whisper_text_length:
                timings = {}
                payload = {
                    'generating_model_name': self.llm_model_name,
                    'timings': timings
                }

                for template in self.get_inference_template():
                    response = getattr(self.get_prompt_builder(), template[1])(whisper_txt, template[2])
                    payload[template[0]] = response
                    timings[template[0]] = self.llm_api.last_query_time
                    print(f"{template[0]}[{self.llm_api.last_query_time}]: {response}")

                # payload = {
                #     'generating_model_name': generating_model_name,
                #     'summary_1': interesting_summary,
                #     'summary_2': high_level_summary,
                #     'summary_3': fifth_grade_summary,
                #     'title_1': title_samples[0],
                #     'title_2': title_samples[1],
                #     'title_3': title_samples[2],
                #     'hashtags_1': hashtag_strings[0],
                #     'hashtags_2': hashtag_strings[1],
                #     'hashtags_3': hashtag_strings[2],
                #     'timings': {    
                #         'summary_1': summary_1_time,
                #         'summary_2': summary_2_time,
                #         'summary_3': summary_3_time,
                #         'title_1': title_1_time,
                #         'title_2': title_2_time,
                #         'title_3': title_3_time,
                #         'hashtags_1': hashtag_times[0],
                #         'hashtags_2': hashtag_times[1],
                #         'hashtags_3': hashtag_times[2],
                #     }                        
                #     # 'people_identified': people,
                #     # 'places_identified': places
                # }
                # pretty print the payload
                print(json.dumps(payload, indent=4))
                # post our payload to populate_ai_markup endpoint in vidsquid
                populate_ai_markup_url = f"{self.vidsquid_url}/videos/{video_id}/populate_ai_markup"
                # raise SystemExit
                print(f"Posting to: {populate_ai_markup_url}")
                r = requests.post(populate_ai_markup_url, json=payload)
                print(f"Status code: {r.status_code}")
                print(f"Response: {r.json()}")

                time.sleep(0.25)
            else:
                print(f'Skipping as whisper text is too short   {len(whisper_txt)} chars\n\n')
    
