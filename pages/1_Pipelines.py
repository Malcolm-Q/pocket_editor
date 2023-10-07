import streamlit as st
import pytube
import requests
from urllib.parse import urlparse
import os
from pedalboard import Pedalboard, Reverb, Distortion, Delay, Bitcrush, Phaser
from pedalboard.io import AudioFile
import ffmpeg

PATH = 'pocket_editor_tmp/CurrentVid.mp4'
OUTPUT = 'pocket_editor_tmp/output.mp4'
TMP_AUDIO = 'pocket_editor_tmp/audio.wav'
AUDIO_OUTPUT = 'pocket_editor_tmp/audio_output.wav'
SAVE_PATH = 'pocket_editor_tmp/concat_files/'
UNDO_PATH = 'pocket_editor_tmp/undoVid.mp4'

st.title('Pre-Built Pipelines')
st.write('One Click Memes')


def process_upload(video):
    if video is not None:
        with open(PATH, 'wb') as f:
            f.write(video.read())

def download_or_get(url):
    if not url: return
    with st.spinner('Downloading...'):
        parsed_url = urlparse(url)
        youtube_domains = ["www.youtube.com", "youtu.be"]
        if parsed_url.netloc in youtube_domains or parsed_url.netloc  and parsed_url.path == "/watch":
            # It's a YouTube URL, so download the video using pytube
            yt = pytube.YouTube(url)
            stream = yt.streams.get_highest_resolution()
            
            stream.download(output_path="C:\\pocket_editor_tmp\\",filename='CurrentVid.mp4')
            st.success("Success!")
        else:
            response = requests.get(url)
            
            with open(PATH, 'wb') as file:
                file.write(response.content)
            st.toast("Success!")


def render_audio(fx_dict):
    with st.spinner('rendering...'):
        if not fx_dict:
            st.error("No fx selected!!!")
            return
        (
        ffmpeg.input(PATH)
        .output(TMP_AUDIO, format='wav')
        .run()
        )
        board = Pedalboard(list(fx_dict.values()))
        with AudioFile(TMP_AUDIO) as f:
            with AudioFile(AUDIO_OUTPUT, 'w', f.samplerate, f.num_channels) as o:
                while f.tell() < f.frames:
                    chunk = f.read(f.samplerate)
                    effected = board(chunk, f.samplerate, reset=False)
                    o.write(effected)

        audio = ffmpeg.input(AUDIO_OUTPUT).audio
        video = ffmpeg.input(PATH).video
        (
            ffmpeg.output(audio,video,OUTPUT)
            .run(overwrite_output=True)
        )
        os.remove(TMP_AUDIO)
        os.remove(AUDIO_OUTPUT)
        try:
            os.remove(UNDO_PATH)
        except Exception:
            pass
        os.rename(PATH,UNDO_PATH)
        os.rename(OUTPUT,PATH)


def main():
    url_tab, upload_tab = st.tabs(['Link','Upload'])
    with url_tab:
        url = st.text_input('Youtube/discord/other video',placeholder='Paste link here...')
        _,_,_,col = st.columns(4)
        with col:
            st.button('Download',on_click=download_or_get,args=(url,))
    with upload_tab:
        video = st.file_uploader('Upload a video',type=['mp4','mov','webm','avi','mkv','wmv','mpeg','ogv'])
        _,_,_,col = st.columns(4)
        with col:
            st.button('Submit Uploaded Video',on_click=process_upload,args=(video,))

    if os.path.exists(PATH):
        st.divider()
        st.write('Your Video:')
        with open(PATH,'rb') as f:
            data = f.read()
        st.video(data)
        col1, col2 = st.columns(2)
        with col1:
            with st.expander('The Keegan Special'):
                st.write('Reverb + Distortion')
                st.button('Run Pipeline','a',on_click=render_audio,args=({'a':Reverb(1,1,1),'b':Distortion(75)},))
            with st.expander('Draftcon'):
                st.write('Phaser + Bitcrush\nInspired by Ethan')
                st.button('Run Pipeline','b',on_click=render_audio,args=({'a':Phaser(),'b':Bitcrush()},))
        with col2:
            with st.expander('Disorienting'):
                st.write('Delay + Reverb')
                st.button('Run Pipeline','c',on_click=render_audio,args=({'a':Delay(0.5,0.5),'b':Reverb(1,1,1)},))
            with st.expander('House Special'):
                st.write('Everything. Idk if this will work')
                st.button('Run Pipeline','d',on_click=render_audio,args=({'a':Reverb(1,1,1),'b':Distortion(75),'c':Delay(0.5,0.5),'d':Bitcrush(),'e':Phaser()},))


if __name__ == '__main__':
    main()
