import streamlit as st
import requests
import pytube
from urllib.parse import urlparse
import os
from streamlit_sortables import sort_items
import ffmpeg
import subprocess
import json

PATH = 'C:\\pocket_editor_tmp\\concat_files\\'
OUT_PATH = 'C:\\pocket_editor_tmp\\output\\'

def main():
    files_and_directories = os.listdir(PATH)
    files = [f for f in files_and_directories if os.path.isfile(os.path.join(PATH, f))]

    st.title('Video Editor')
    st.write('Clips you edit can be saved in "Clip Manager" by pressing the "save to project manager" button.\n\nAlternatively you can upload/download videos below.')
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
    st.divider()

    st.session_state.number_of_files = len(files)
    if files:
        st.write('Order your videos then render them all as one video.')
        sorted_videos = sort_items(files,direction='vertical')
        for file in sorted_videos:
            with open(PATH+file, 'rb') as f:
                vid = f.read()
            st.video(vid)
        st.divider()

        st.write('Delete videos')
        deletions = st.multiselect('Select Clips To Delete:',options=files)
        col1,col2 = st.columns(2)
        with col1:
            st.button('DELETE SELECTED FILES',on_click=delete_files,args=(deletions,))
        with col2:
            st.button('DELETE ALL FILES!',on_click=delete_files,args=(files,))
        st.divider()
        if st.button('Render Video',on_click=render_video,args=(sorted_videos,)):
            st.download_button('Download Video',data=open(OUT_PATH+'output.mp4','rb'))
            with open(OUT_PATH+'output.mp4','rb') as f:
                data = f.read()
            st.video(data)


def render_video(vids):
    ffmpeg_commands = [
        'ffmpeg -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts temp{}.ts'.format(PATH + file, index)
        for index, file in enumerate(vids)
    ]

    concatenation_command = 'ffmpeg -i "concat:{}" -c copy {}temp.mp4'.format('|'.join('temp{}.ts'.format(index) for index, _ in enumerate(vids)), OUT_PATH)

    try:
        for cmd in ffmpeg_commands:
            subprocess.run(cmd, shell=True, check=True)

        subprocess.run(concatenation_command, shell=True, check=True)
        if os.path.exists(OUT_PATH+'output.mp4'): os.remove(OUT_PATH+'output.mp4')
        os.rename(OUT_PATH+'temp.mp4',OUT_PATH+'output.mp4')
    finally:
        for index, _ in enumerate(vids):
            temp_file = 'temp{}.ts'.format(index)
            if os.path.exists(temp_file):
                os.remove(temp_file)



def delete_files(files):
    for file in files:
        os.remove(PATH+file)

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
            yt = pytube.YouTube(url)
            stream = yt.streams.get_highest_resolution()
            
            stream.download(output_path=PATH,filename=f'clip_{st.session_state.number_of_files}.mp4')
            st.success("Success!")
        else:
            response = requests.get(url)
            
            with open(PATH+f'clip_{st.session_state.number_of_files}.mp4', 'wb') as file:
                file.write(response.content)
            st.toast("Success!")


if __name__ == '__main__':
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    if not os.path.exists(OUT_PATH):
        os.mkdir(OUT_PATH)
    main()