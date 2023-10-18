import streamlit as st
import os
from lib.video_utils import (
    process_upload,
    download_or_get,
    render_audio,
)
from pedalboard import Pedalboard, Reverb, Distortion, Delay,Phaser, Bitcrush

PATH = os.environ['PATH']

st.title('Pre-Built Pipelines')
st.write('One Click Memes')


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
                st.button('Run Pipeline','b',on_click=render_audio,args=({'a':Phaser(),'b':Bitcrush(0.5)},))
        with col2:
            with st.expander('Disorienting'):
                st.write('Delay + Reverb')
                st.button('Run Pipeline','c',on_click=render_audio,args=({'a':Delay(0.5,0.5),'b':Reverb(1,1,1)},))
            with st.expander('House Special'):
                st.write('Everything. Idk if this will work')
                st.button('Run Pipeline','d',on_click=render_audio,args=({'a':Reverb(1,1,1),'b':Distortion(75),'c':Delay(0.5,0.5),'d':Bitcrush(0.5),'e':Phaser()},))

        st.divider()
        st.write('Meme Templates')
        col2,col3 = st.columns(2)
        with col2:
            with st.expander('Speech Bubble Gif'):
                st.write('Add a speech bubble to a gif')
                st.button('Run Pipeline','e',on_click=render_video,args=({'overlay':['pocket_editor/pipeline_files/images/speech_bubble.png', ('center','top')],'format':'gif'}))

if __name__ == '__main__':
    main()
