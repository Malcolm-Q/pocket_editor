import streamlit as st
import os
from streamlit_sortables import sort_items
from lib.video_utils import (
    process_upload,
    download_or_get,
    delete_files,
    concat_video,
)

def main():
    files_and_directories = os.listdir(st.session_state.PATH)
    files = [f for f in files_and_directories if os.path.isfile(os.path.join(st.session_state.PATH, f))]
    st.session_state.number_of_files = len(files)

    st.title('Video Editor')
    st.write('Clips you edit can be saved in "Clip Manager" by pressing the "save to Clip Manager" button.\n\nAlternatively you can upload/download videos below.')
    url_tab, upload_tab = st.tabs(['Link','Upload'])
    with url_tab:
        url = st.text_input('Youtube/discord/other video',placeholder='Paste link here...')
        _,_,_,col = st.columns(4)

        with col:
            st.button('Download',on_click=download_or_get,args=(url,st.session_state.PATH,f'clip_{len(files)}.mp4'))
    with upload_tab:
        video = st.file_uploader('Upload a video',type=['mp4','mov','webm','avi','mkv','wmv','mpeg','ogv'])
        _,_,_,col = st.columns(4)
        with col:
            st.button('Submit Uploaded Video',on_click=process_upload,args=(video,))
    st.divider()

    if files:
        st.write('Order your videos then render them all as one video.')
        sorted_videos = sort_items(files,direction='vertical')
        for file in sorted_videos:
            with open(st.session_state.PATH+file, 'rb') as f:
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
        if st.button('Render Video',on_click=concat_video,args=(sorted_videos,)):
            st.download_button('Download Video',data=open(st.session_state.OUT_PATH+'output.mp4','rb'))
            with open(OUT_st.session_state.PATH+'output.mp4','rb') as f:
                data = f.read()
            st.video(data)


if __name__ == '__main__':
    if not os.path.exists(st.session_state.PATH):
        os.mkdir(st.session_state.PATH)
    if not os.path.exists(st.session_state.OUT_PATH):
        os.mkdir(st.session_state.OUT_PATH)
    main()
