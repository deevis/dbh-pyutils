import sys
from pytube import YouTube
from youtube_search import YoutubeSearch
import json
import requests
import os

def searchYouTube(query):
    results = YoutubeSearch(query, max_results=50).to_json()
    results = json.loads(results)
    return results['videos']

# Uses google API's
# https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas?project=youtube-expert-395001
def searchYouTubeAPI(query: str, max_results: int = 20):
    endpoint = "https://www.googleapis.com/youtube/v3/search"
    api_key = os.getenv('YOUTUBE_API_KEY')
    part = 'snippet' # search only supports 'snippet,id' - statistics,contentDetails,topicDetails
    url = f'{endpoint}?key={api_key}&q={query}&part={part}&type=video&maxResults={max_results}'
    response = requests.get(url)

    results = []
    if response.status_code == 200:
        videos = json.loads(response.text)
        for video in videos['items']:
            # result = {
            #     'title': video['snippet']['title'],
            #     'video_id': video['id']['videoId'],
            #     'description': video['snippet']['description'],
            #     'channel': video['snippet']['channelTitle'],
            #     'published_at': video['snippet']['publishedAt']               
            # }
            # print formatted video
            video_id = video['id']['videoId']
            result = getYouTubeVideoInfo(video_id)
            results.append(result)
    else:
        print('An error occurred:', response.text)
    
    return results

def getYouTubeVideoInfo(video_id):
    endpoint = "https://www.googleapis.com/youtube/v3/videos"
    api_key = os.getenv('YOUTUBE_API_KEY')
    part = 'snippet,statistics,contentDetails,topicDetails'
    url = f'{endpoint}?key={api_key}&id={video_id}&part={part}'
    response = requests.get(url)
    # pretty print json results
    # print(json.dumps(response.json(), indent=4, sort_keys=True))
    return response.json()['items'][0]



def downloadYouTube(videourl, save_path):

    yt = YouTube(videourl)
    streams = yt.streams.filter(progressive = True, file_extension='mp4').order_by('resolution').desc()
    # print(f'\nstreams: {streams}')
    stream = streams.first()
    # stream = streams.get_highest_resolution()
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    download_path = stream.download(save_path, skip_existing=True)
    print(f'YouTube download_path: {download_path}')
    return download_path

if __name__ == '__main__':
    # results = searchYouTube('brics currency')
    # results = searchYouTubeAPI('brics currency')
    # pretty print json results
    # print(json.dumps(results, indent=4, sort_keys=True))
    # raise SystemExit(0)
    # print('\nvideo_url:')
    # video_url = input()
    # print('\nsave_path:')
    # save_path = input()
    save_path = f'e:/yt_videos/test'
    video_url = 'https://www.youtube.com/watch?v=n2CFEXpEeWo'
    downloadYouTube(video_url, save_path)
