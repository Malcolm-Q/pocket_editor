import os
import streamlit as st
import pytube
import requests
from urllib.parse import urlparse
import subprocess
import json
from pedalboard import Pedalboard, Reverb, Distortion, Delay,Phaser, Bitcrush
from pedalboard.io import AudioFile
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
import moviepy.video.fx.all as vfx


PATH = os.environ['PATH']
OUTPUT = os.environ['OUTPUT']
TMP_AUDIO = os.environ['TMP_AUDIO']
AUDIO_OUTPUT = os.environ['AUDIO_OUTPUT']
SAVE_PATH = os.environ['SAVE_PATH']
UNDO_PATH = os.environ['UNDO_PATH']
OUT_PATH = os.environ['OUT_PATH']
AUDIO_REPLACE = os.environ['AUDIO_REPLACE']

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


def render_video(vfx_dict):
    with st.spinner('rendering...'):
        try:
            segmented_clips = []
            if 'segment' in vfx_dict:
                video_clip = VideoFileClip(PATH).subclip(vfx_dict['segment'][0],vfx_dict['segment'][1])

                if vfx_dict['segment'][0] > 0:
                    video_clip_start = VideoFileClip(PATH).subclip(0,vfx_dict['segment'][0])
                    segmented_clips.append(video_clip_start)

                segmented_clips.append(video_clip)

                if vfx_dict['segment'][1] < st.session_state.duration:
                    video_clip_end = VideoFileClip(PATH).subclip(vfx_dict['segment'][1],st.session_state.duration)
                    segmented_clips.append(video_clip_end)

                vfx_dict.pop('segment')
            else:
                video_clip = VideoFileClip(PATH)

            if 'resize' in vfx_dict:
                video_clip = video_clip.resize(vfx_dict['resize'])
                vfx_dict.pop('resize')

            if 'subclip' in vfx_dict:
                video_clip = video_clip.subclip(vfx_dict['subclip'][0],vfx_dict['subclip'][1])
                vfx_dict.pop('subclip')
            
            for fx in vfx_dict.values():
                video_clip = video_clip.fx(fx[0],**fx[1])
            
            if segmented_clips:
                video_clip = concatenate_videoclips(segmented_clips)

            video_clip.write_videofile(OUTPUT)
            st.success(f'Video edited and saved')
        except Exception as e:
            st.error(f'Error editing video: {e}')

        try:
            os.remove(UNDO_PATH)
        except Exception:
            pass
        os.rename(PATH,UNDO_PATH)
        os.rename(OUTPUT, PATH)
        get_video_info()
        


def render_audio(fx_dict):
    with st.spinner('rendering...'):
        if not fx_dict:
            st.error('No fx selected')
            return

        segmented_clips = []
        if 'segment' in fx_dict:
            audio_clip = AudioFileClip(PATH).subclip(fx_dict['segment'][0],fx_dict['segment'][1])
            if fx_dict['segment'][0] > 0:
                audio_clip_start = AudioFileClip(PATH).subclip(0,fx_dict['segment'][0])
                segmented_clips.append(audio_clip_start)
            segmented_clips.append(audio_clip)
            if fx_dict['segment'][1] < st.session_state.duration:
                audio_clip_end = AudioFileClip(PATH).subclip(fx_dict['segment'][1],st.session_state.duration)
                segmented_clips.append(audio_clip_end)
            fx_dict.pop('segment')
        else:
            audio_clip = AudioFileClip(PATH)
        
        if 'replace_audio' in fx_dict:
            if isinstance(fx_dict['replace_audio'][0], str):
                download_or_get(fx_dict['replace_audio'][0],AUDIO_REPLACE.split('/')[0]+'/',AUDIO_REPLACE.split('/')[-1]+'mp4')
            else:
                with open(AUDIO_REPLACE + fx_dict['replace_audio'][1], 'wb') as f:
                    f.write(fx_dict['replace_audio'][0].read())
            duration = audio_clip.duration
            audio_clip = AudioFileClip(AUDIO_REPLACE+fx_dict['replace_audio'][1],duration)
            fx_dict.pop('replace_audio')

        audio_clip.write_audiofile(TMP_AUDIO)
        board = Pedalboard(list(fx_dict.values()))

        with AudioFile(TMP_AUDIO) as f:
            with AudioFile(AUDIO_OUTPUT, 'w', f.samplerate, f.num_channels) as o:
                while f.tell() < f.frames:
                    chunk = f.read(f.samplerate)
                    effected = board(chunk, f.samplerate, reset=False)
                    o.write(effected)

        video = VideoFileClip(PATH)
        if segmented_clips:
            audio = concatenate_audioclips(segmented_clips)
        else:
            audio = AudioFileClip(AUDIO_OUTPUT)

        video = video.set_audio(audio)
        video.write_videofile(OUTPUT)

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


def download_or_get(url,path='pocket_editor_tmp/',filename='CurrentVid.mp4'):
    if not url: return
    with st.spinner('Downloading...'):
        parsed_url = urlparse(url)
        youtube_domains = ['www.youtube.com', "youtu.be"]
        if parsed_url.netloc in youtube_domains or parsed_url.netloc  and parsed_url.path == '/watch':
            # It's a YouTube URL, so download the video using pytube
            yt = pytube.YouTube(url)
            stream = yt.streams.get_highest_resolution()
            
            stream.download(output_path=path,filename=filename)
            st.success('Success!')
        else:
            response = requests.get(url)
            opendir = path if path.endswith('.mp4') else PATH
            
            with open(opendir, 'wb') as file:
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
    concat_clip = concatenate_videoclips([VideoFileClip(SAVE_PATH+vid) for vid in vids])
    concat_clip.write_videofile(OUT_PATH+'temp.mp4')
    if os.path.exists(OUT_PATH+'output.mp4'): os.remove(OUT_PATH+'output.mp4')
    os.rename(OUT_PATH+'temp.mp4',OUT_PATH+'output.mp4')


def delete_files(files):
    for file in files:
        os.remove(PATH+file)
