import whisper
import os
import sys

# _MODELS = {
#     "tiny.en": "https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03/tiny.en.pt",
#     "tiny": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
#     "base.en": "https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/base.en.pt",
#     "base": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
#     "small.en": "https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt",
#     "small": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
#     "medium.en": "https://openaipublic.azureedge.net/main/whisper/models/d7440d1dc186f76616474e0ff0b3b6b879abc9d1a4926b7adfa41db2d497ab4f/medium.en.pt",
#     "medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
#     "large-v1": "https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large-v1.pt",
#     "large-v2": "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
#     "large": "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
# }
def load_whisper_model(whisper_model: str = 'large-v2'):
    print(f"Loading whisper[{whisper_model}] model...")
    model = whisper.load_model(whisper_model)
    print(f"Loaded whisper[{whisper_model}] model.")
    return model

# returns transcribed_text, tsv_text
def transcribe_whisper_video(model, path, message="", translate_to_en=True, force_transcribe=False):
    transcribed_path = f"{path}.txt"
    if not force_transcribe and os.path.exists(transcribed_path):
        print(f"{message}Skipping transcription - already transcribed: - {path}")
        with open(transcribed_path, "r", encoding='utf-8') as file:
            text = file.read()
        tsv_path = f"{path}.tsv"
        with open(tsv_path, "r", encoding='utf-8') as file:
            tsv_text = file.read()
    else:
        if translate_to_en:
            task = "translate"
        else:
            task = "transcribe"
        print(f"{message}Transcribing[{task}] video: - {path}")
        result = model.transcribe(path, task=task)
        text = result["text"].strip()
        print(text)
        with open(transcribed_path, "w", encoding='utf-8') as file:
            file.write(text)
            file.write("\n")
        print(f"     Written to {transcribed_path}")
        tsv_path = f"{path}.tsv"
        tsv_text = ''
        with open(tsv_path, "w", encoding='utf-8') as file:    
            file.write("start\tend\ttext\n")
            # build TSV file (start/tend/ttext)
            tsv_text += "start\tend\ttext\n"
            for segment in result["segments"]:
                start = int(segment['start'] * 1000)
                end = int(segment['end'] * 1000)
                snippet = segment['text'].strip()
                tsv_text += f"{start}\t{end}\t{snippet}\n"
                file.write(f"{start}\t{end}\t{snippet}\n")
    
    return text, tsv_text

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        model = load_whisper_model("large")
        transcribe_whisper_video(model, video_path)
    else:
        print("\nUsage: python dbh_whisper.py <video_path>\n\n")
        

