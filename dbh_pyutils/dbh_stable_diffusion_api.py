import json
import requests
import io
import base64
import time
from PIL import Image, PngImagePlugin

class StableDiffusionApi():
    def __init__(self, url='http://127.0.0.1:7860', modelCheckpoint=None):
        self.url = url
        self.modelCheckpoint = modelCheckpoint
        if self.modelCheckpoint is not None:
            currentModel = self.get_options()['sd_model_checkpoint']
            if currentModel != modelCheckpoint:
                self.load_model(self.modelCheckpoint)

    def get_options(self):
        response = requests.get(url=f'{self.url}/sdapi/v1/options')
        return response.json()

    def get_available_samplers(self):
        response = requests.get(url=f'{self.url}/sdapi/v1/samplers')
        return response.json()

    def get_available_models(self):
        response = requests.get(url=f'{self.url}/sdapi/v1/models')
        return response.json()
    
    def load_model(self, modelCheckpoint):
        # print message in yellow
        b4 = time.time()
        print('\033[93m' + f'Loading model {modelCheckpoint}' + '\033[0m')
        payload = {"sd_model_checkpoint": modelCheckpoint }
        response = requests.post(url=f'{self.url}/sdapi/v1/options', json=payload)
        # print message in green
        print('\033[92m' + f'Loaded model {modelCheckpoint} in {time.time() - b4} seconds' + '\033[0m')
        time.sleep(0.1)
        return response.json()
    
    # returns an array of generated images
    def generate_image(self,prompt='A very pretty kitty cat', 
                    negative_prompt='',
                    steps=50, 
                    width=512, height=512, batch_size=1, cfg_scale=7,
                    seed=-1, 
                    output_dir='output',
                    sampler='Euler',
                    restore_faces=False):

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "width": width,
            "height": height,
            "batch_size": batch_size,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler": sampler,
            "restore_faces": restore_faces
        }

        response = requests.post(url=f'{self.url}/sdapi/v1/txt2img', json=payload)

        r = response.json()

        generated_images = []
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{self.url}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            pnginfo.add_text("prompt", payload.get("prompt"))
            filename = f'{output_dir}/output-{time.time()}.png'
            generated_images.append(filename)
            image.save(filename, pnginfo=pnginfo)

        return generated_images
