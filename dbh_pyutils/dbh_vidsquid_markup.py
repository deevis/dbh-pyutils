import requests
import time
import json
from dbh_pyutils.dbh_text_generation_webui_api import TextGenerationWebuiAPI
from dbh_pyutils.dbh_prompt_builder import PromptBuilder

class VidsquidMarkup():
    def __init__(self, llm_api, 
                 vidsquid_url="http://192.168.0.43:3143",
                 debug=False):
        self.debug = debug
        self.llm_api = llm_api
        self.prompt_builder = PromptBuilder(llm_api)
        self.vidsquid_url = vidsquid_url

    def get_inference_config(self):
        config = {
            'generating_model_name': self.llm_api.get_llm_name(),
            'llm_params': self.llm_api.get_llm_params(),
        }
        for template in self.get_inference_template():
            prompt = getattr(self.prompt_builder, template[1])("{TEXT}", template[2], promptOnly=True)
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
    
    # Will find videos that have no AI markup and generate it
    def do_ai_markup(self, min_whisper_text_length: int = 200):
        generating_model_name = self.llm_api.get_llm_name()
        print(f"Using model: {generating_model_name}")
        endpoint = f'videos/list_no_ai_markup_for_model_videos'
        url = f"{self.vidsquid_url}/{endpoint}?generating_model_name={generating_model_name}&min_whisper_txt_length={min_whisper_text_length}"
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
            if len(whisper_txt) >= min_whisper_text_length:
                timings = {}
                payload = {
                    'generating_model_name': generating_model_name,
                    'timings': timings
                }

                for template in self.get_inference_template():
                    response = getattr(self.prompt_builder, template[1])(whisper_txt, template[2])
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
    
