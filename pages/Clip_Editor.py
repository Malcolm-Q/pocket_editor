import streamlit as st
from lib.video_utils import *
import os
from pedalboard import Pedalboard, Reverb, Distortion, Delay,Phaser, Bitcrush, PitchShift

PATH = os.environ['PATH']

def main():
    with st.expander('Load Video'):
        st.title('Clip Editor')
        st.write('Download a youtube video or anything retrievable with a GET request.\n\nAlternatively you can upload a video.\n\nOnce a video is downloaded/uploaded you can edit it and the audio.')
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

    if not os.path.exists(PATH):
        return
    with st.expander('Video Effects'):
        st.title('Edit Video')
        st.button('Save To Project Manager',on_click=save_video, key='saveVid')
        with open(PATH, 'rb') as f:
            downloaded_video = f.read()
        st.video(downloaded_video)
        st.divider()
        if st.session_state.duration == None:
            col1,_,col2 = st.columns(3)
            with col1:
                clip_start = st.number_input('Clip Start')
            with col2:
                clip_end = st.number_input('Clip End')
        else:
            clip_start, clip_end = st.slider(
                'Clip Video',
                value=(0.0,float(st.session_state.duration))
            )
        speed = st.number_input('Video Speed',value=1.0)
        _,res1,xcol,res2,_ = st.columns(5)
        with res1:
            h_res = st.number_input('Horizontal Resolution',value=st.session_state.resolution[0])
        with xcol:
            st.markdown('<h1 style="text-align: center;">X</h1>', unsafe_allow_html=True)
        with res2:
            v_res = st.number_input('Vertical Resolution',value=st.session_state.resolution[1])

        while h_res % 2 != 0:
            h_res += 1
        while v_res % 2 != 0:
            v_res += 1
        st.session_state.resolution = (h_res,v_res)

        st.divider()
        col1,_,col_mid,_,col2 = st.columns(5)

        with col_mid:
            st.button('Render Video', key='renderVid',on_click=render_video, args=(speed,clip_start,clip_end,h_res,v_res))
            st.button('Undo', on_click=undo)

    with st.expander('Audio Effects'):
        st.title('Add Audio Effects')
        st.button('Save To Project Manager', on_click=save_video, key='saveAud')
        with open(PATH, 'rb') as f:
            downloaded_video = f.read()
        st.video(downloaded_video)
        st.write('Select Effects:')

        fx_dict = {}
        if st.checkbox('Distortion'):
            drive_db = st.number_input('drive db',value=25.0)
            fx_dict['distortion'] = Distortion(drive_db)

        if st.checkbox('Reverb'):
            col1,col2,col3 = st.columns(3)
            with col1:
                room_size = st.number_input('room size',value=0.5)
                damping = st.number_input('damping',value=0.5)
            with col2:
                wet_level = st.number_input('wet level',value=0.33)
                dry_level = st.number_input('dry level',value=0.4)
            with col3:
                width = st.number_input('width',value=1.0)
                freeze_mode = st.number_input('freeze mode',value=0.0)
            reverb = Reverb(room_size,damping,wet_level,dry_level,width,freeze_mode)
            fx_dict['reverb'] = reverb

        if st.checkbox('Delay'):
            col1,col2,col3 = st.columns(3)
            with col1:
                delay_sec = st.number_input('delay seconds', value=0.5)
            with col2:
                feedback = st.number_input('feedback',value=0.0)
            with col3:
                mix = st.number_input('wet/dry mix',value=0.5)
            fx_dict['delay'] = Delay(delay_sec,feedback,mix)

        if st.checkbox('Phaser'):
            col1,col2,col3 = st.columns(3)
            with col1:
                rate_hz = st.number_input('rate hz',value=1.0)
                depth = st.number_input('depth',value=0.5)
            with col2:
                centre_freq = st.number_input('centre freq hz',value=1300.0)
                phaser_feedback = st.number_input('feedback',value=0.0)
            with col3:
                phaser_mix = st.number_input('wet/dry mix',value=0.5)
            fx_dict['phaser']=Phaser(rate_hz,depth,centre_freq,phaser_feedback,phaser_mix)

        if st.checkbox('Bit Crush'):
            bit_depth = st.number_input('bit depth',value=0.8)
            fx_dict['bit_crush'] = Bitcrush(bit_depth)

        if st.checkbox('Pitch Shift'):
            pitch_shift = st.number_input('pitch shift',value=3.0)
            fx_dict['pitch_shift'] = PitchShift(pitch_shift)
        col1,_,col_mid,_,col2 = st.columns(5)
        with col_mid:
            st.button('Render Video', key='renderAud',on_click=render_audio, args=(fx_dict,))
            st.button('undo')




if __name__ == '__main__':
    if 'duration' not in st.session_state:
        st.session_state.duration = None
    if 'resolution' not in st.session_state:
        st.session_state.resolution = (1920,1080)
    main()
