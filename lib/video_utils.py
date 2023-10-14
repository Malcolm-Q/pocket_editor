import os
import streamlit as st
import pytube
import requests
from urllib.parse import urlparse
import subprocess
import json
from pedalboard import Pedalboard, Reverb, Distortion, Delay,Phaser, Bitcrush
from pedalboard.io import AudioFile
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips


PATH = os.environ['PATH']
OUTPUT = os.environ['OUTPUT']
TMP_AUDIO = os.environ['TMP_AUDIO']
AUDIO_OUTPUT = os.environ['AUDIO_OUTPUT']
SAVE_PATH = os.environ['SAVE_PATH']
UNDO_PATH = os.environ['UNDO_PATH']
OUT_PATH = os.environ['OUT_PATH']

def save_video():
    get_number_of_files()
    with open(PATH, 'rb') as source:
        with open(SAVE_PATH+f'clip_{st.session_state.number_of_files}.mp4', 'wb') as destination:
            destination.write(source.read())


def get_number_of_files():
    files_and_directories = os.listdir(SAVE_PATH)
    files = [f for f in files_and_directories if os.path.isfile(os.path.join(SAVE_PATH, f))]
    st.session_state.number_of_files = len(files)

def process_upload(video):
    if video is not None:
        with open(PATH, 'wb') as f:
            f.write(video.read())
        get_video_info()


def render_video(video_speed, start_time, end_time, h_res, v_res):
    with st.spinner('rendering...'):
        try:
            video_clip = VideoFileClip(PATH).subclip(start_time, end_time)

            audio_clip = video_clip.fx(audio_speedx, video_speed)

            video_clip = video_clip.fx(speedx, video_speed).fx(resize, (h_res, v_res))

            final_clip = video_clip.set_audio(audio_clip)

            final_clip.write_videofile(OUTPUT)
            st.success(f'Video edited and saved')

            try:
                os.remove(UNDO_PATH)
            except Exception:
                pass
            os.rename(PATH,UNDO_PATH)
            os.rename(OUTPUT, PATH)
            get_video_info()
        except Exception as e:
            st.error(f'Error editing video: {e}')


def render_audio(fx_dict):
    with st.spinner('rendering...'):
        if not fx_dict:
            st.error('No fx selected')
            return

        AudioFileClip(PATH).write_audiofile(TMP_AUDIO)
        board = Pedalboard(list(fx_dict.values()))

        with AudioFile(TMP_AUDIO) as f:
            with AudioFile(AUDIO_OUTPUT, 'w', f.samplerate, f.num_channels) as o:
                while f.tell() < f.frames:
                    chunk = f.read(f.samplerate)
                    effected = board(chunk, f.samplerate, reset=False)
                    o.write(effected)

        audio = AudioFileClip(AUDIO_OUTPUT)
        video = VideoFileClip(PATH)

        video = video.set_audio(audio)

        os.remove(TMP_AUDIO)
        os.remove(AUDIO_OUTPUT)
        try:
            os.remove(UNDO_PATH)
        except Exception:
            pass
        os.rename(PATH,UNDO_PATH)
        os.rename(OUTPUT,PATH)
        get_video_info()


def undo():
    if os.path.exists(UNDO_PATH):
        os.remove(PATH)
        os.rename(UNDO_PATH,PATH)
    else:
        st.error('Cannot undo further...')


def download_or_get(url):
    if not url: return
    with st.spinner('Downloading...'):
        parsed_url = urlparse(url)
        youtube_domains = ['www.youtube.com', "youtu.be"]
        if parsed_url.netloc in youtube_domains or parsed_url.netloc  and parsed_url.path == '/watch':
            # It's a YouTube URL, so download the video using pytube
            yt = pytube.YouTube(url)
            stream = yt.streams.get_highest_resolution()
            
            stream.download(output_path='pocket_editor_tmp/',filename='CurrentVid.mp4')
            st.success('Success!')
        else:
            response = requests.get(url)
            
            with open(PATH, 'wb') as file:
                file.write(response.content)
            st.toast('Success!')
        get_video_info()

def get_video_info():
    try:
        clip = VideoFileClip(PATH)
    except Exception as e:
        print(f'Error loading video: {e}')
        return
    try:
        st.session_state.duration = clip.duration
    except Exception as e:
        print(e)
    try:
        st.session_state.resolution = clip.size
    except Exception as e:
        print(e)


def concat_video(vids):
    concat_clip = concatenate_videoclips([VideoFileClip(OUT_PATH+vid) for vid in vids])
    concat_clip.write_videofile(OUT_PATH+'temp.mp4')
    if os.path.exists(OUT_PATH+'output.mp4'): os.remove(OUT_PATH+'output.mp4')
    os.rename(OUT_PATH+'temp.mp4',OUT_PATH+'output.mp4')


def delete_files(files):
    for file in files:
        os.remove(PATH+file)