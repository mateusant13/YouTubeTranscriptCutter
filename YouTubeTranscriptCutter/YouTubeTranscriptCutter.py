from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pytube import *
import os
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import time

# Programa que usa Selenium, YoutubeTrasncriptApi, Pytube e MoviePy para cortar vários videos de um canal do Youtube que contenha uma palavra ou frase específica no intervalo de tempo em que elas são ditas. 
# É criada a pasta videos para baixar todos os vídeos em que existem as palavra desejadas. 
# Também é criada a pasta clips para cortar no momento em que elas aparecem dos vídeos.

driver = webdriver.Chrome()

channelId = 'UCLYimOsgmIVf6KNjzXPkUwQ' #Coloque o id do canal 

url = f'https://www.youtube.com/channel/{channelId}/videos' 
driver.get(url)

prev_ht = driver.execute_script("return document.documentElement.scrollHeight;")
while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(1)  
    ht = driver.execute_script("return document.documentElement.scrollHeight;")
    if prev_ht == ht:
        break
    prev_ht = ht

video_links = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="video-title-link"]'))
)

videoId = []

for link in video_links:
    video_href = link.get_attribute('href')
    videoId.append(video_href)

textList = []

for url in videoId:
    partes = url.split("=")
    if len(partes) >=2:
        textoId = partes[1]
        textList.append(textoId)
        print(textoId)

maxVideos = 20 # Número de vídeos que serão usados para checar pelas transcrições

video_transcripts = []
for videoId in textList[:maxVideos-1]:
    try:
        video_transcripts.append(YouTubeTranscriptApi.get_transcript(videoId, languages=['pt'])) # Configuravel: pt = pt-br
    except:
        pass

transcript_data = {}
for index in range(len(video_transcripts)):
    transcript = video_transcripts[index]
    caption = []
    for entry in transcript:
        if 'exemplo' in entry['text']: # Mude o exemplo para palavra ou frase desejada.
            caption.append(entry)
            transcript_data.update({textList[index]: caption})
            
print(transcript_data)

for videoId in transcript_data:
    transcript_data_i = transcript_data[videoId] 
    for clipindex in range(len(transcript_data_i)):
        clipdata = transcript_data_i[clipindex]
        start = clipdata['start']
        duration = clipdata['duration']
        yt = YouTube(f'http://youtube.com/watch?v={videoId}')
        stream = yt.streams.get_by_itag(18) # itag 18 para baixar na resolução 640x360p 30fps 
        path = stream.download(output_path='videos')
        base_name, extension = os.path.splitext(os.path.basename(path))
        clipname =  base_name + '_clip' + str(clipindex) + extension
        ffmpeg_extract_subclip(path, start, start + duration, os.path.join(os.getcwd(), f'clips\{clipname}'))