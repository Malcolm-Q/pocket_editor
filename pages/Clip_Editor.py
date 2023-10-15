import streamlit as st
from lib.video_utils import *
import os
from pedalboard import Pedalboard, Reverb, Distortion, Delay,Phaser, Bitcrush, PitchShift
import moviepy.video.fx.all as vfx

PATH = os.environ['PATH']

def main():
    if not os.path.exists(PATH):
        st.session_state.state = 1
    if st.session_state.state == 1:
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
        _,_,col = st.columns(3)
        with col:
            if os.path.exists(PATH):
                st.button('Edit Video', on_click=iterate_state)

    if st.session_state.state == 2:
        st.title('Edit Video')
        st.button('Save To Project Manager',on_click=save_video, key='saveVid')
        with open(PATH, 'rb') as f:
            downloaded_video = f.read()
        st.video(downloaded_video)
        st.divider()
        vfx_dict = {}
        if st.checkbox('Subclip'):
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
            vfx_dict['subclip'] = (clip_start,clip_end)
        
        if st.checkbox('Apply Changes to Segment'):
            if st.session_state.duration == None:
                col1,_,col2 = st.columns(3)
                with col1:
                    clip_start = st.number_input('Segment Start')
                with col2:
                    clip_end = st.number_input('Segment End')
            else:
                clip_start, clip_end = st.slider(
                    'Segment Video',
                    value=(0.0,float(st.session_state.duration))
                )
            vfx_dict['segment'] = (clip_start,clip_end)

        if st.checkbox('Change Speed'):
            speed = st.number_input('Video Speed',value=1.0)
            vfx_dict['speed'] = (vfx.speedx,{'factor':speed})

        if st.checkbox('Resize'):
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
            vfx_dict['resize'] = (h_res,v_res)
        
        if st.checkbox('Color intensity'):
            st.write('(Enter 0 for black and white)')
            intensity = st.number_input('Color intensity',value=1.0)
            vfx_dict['color'] = (vfx.colorx,{'factor':intensity})
        
        if st.checkbox('Freeze Frame'):
            freeze_time_static = st.number_input('Time Frame Will Freeze',value=0.0)
            freeze_duration = st.number_input('Duration of Freeze',value=0.0)
            vfx_dict['freeze'] = (vfx.freeze,{'t':freeze_time_static,'freeze_duration':freeze_duration})
        
        if st.checkbox('Freeze Region'):
            col1,col2 = st.columns(2)
            freeze_time = st.number_input('Time Region Freeze Will Occur',value=0.0)
            with col1:
                x1 = st.number_input('x1',value=0)
                y1 = st.number_input('y1',value=0)
            with col2:
                x2 = st.number_input('x2',value=st.session_state.resolution[0])
                y2 = st.number_input('y2',value=st.session_state.resolution[1])
            vfx_dict['freeze_region'] = (vfx.freeze_region,{'t':freeze_time,'region':(x1,y1,x2,y2)})
        
        if st.checkbox('Fade In'):
            fade_duration = st.number_input('Fade In Duration',value=1.0)
            fade_color = st.number_input('Fade Color',max_value=1,min_value=0)
            vfx_dict['fadein'] = (vfx.fadein,{'duration':fade_duration,'initial_color':fade_color})
        
        if st.checkbox('Fade Out'):
            fade_duration = st.number_input('Fade Out Duration',value=1.0)
            fade_color = st.number_input('Fade Color',max_value=1,min_value=0)
            vfx_dict['fadeout'] = (vfx.fadeout,{'duration':fade_duration,'initial_color':fade_color})
        
        if st.checkbox('Gamma Correction'):
            gamma = st.number_input('Gamma',value=1.0)
            vfx_dict['gamma'] = (vfx.gamma_corr,{'gamma':gamma})
        
        if st.checkbox('Invert Colors'):
            vfx_dict['invert'] = (vfx.invert_colors,{})
        
        if st.checkbox('Mirror x'):
            vfx_dict['mirror'] = (vfx.mirror_x,{})
        
        if st.checkbox('Mirror y'):
            vfx_dict['mirror'] = (vfx.mirror_y,{})
        
        if st.checkbox('Loop'):
            loop_duration = st.number_input('Loop Duration',value=st.session_state.duration)
            vfx_dict['loop'] = (vfx.loop,{'n':loop_duration})
        
        if st.checkbox('Time Symmetrize'):
            st.write('This effect will play the video forwards and then backwards')
            vfx_dict['symmetrize'] = (vfx.time_symmetrize,{})
        
        if st.checkbox('Supersample'):
            st.write('Motion Blur Type Effect\nThis can take a while to render.\nNot recommended for long videos.')
            d = st.number_input('d',value=3)
            n_frames = st.number_input('n_frames',value=5)
            vfx_dict['supersample'] = (vfx.supersample,{'d':d,'nframes':n_frames})
        
        if st.checkbox('Contrast Correction'):
            luminosity = st.number_input('Luminosity',value=0.0)
            contrast = st.number_input('Contrast',value=0.0)
            vfx_dict['contrast'] = (vfx.lum_contrast,{'lum':luminosity,'contrast':contrast})

        st.divider()
        col1,_,col_mid,_,col2 = st.columns(5)

        with col_mid:
            st.button('Render Video', key='renderVid',on_click=render_video, args=(vfx_dict,))
            st.button('Undo', on_click=undo)
        with col1:
            st.button('Load Video', on_click=deiterate_state)
        with col2:
            st.button('Add Audio Effects', on_click=iterate_state)

    if st.session_state.state == 3:
        st.title('Add Audio Effects')
        st.button('Save To Project Manager', on_click=save_video, key='saveAud')
        with open(PATH, 'rb') as f:
            downloaded_video = f.read()
        st.video(downloaded_video)
        st.write('Select Effects:')

        fx_dict = {}
        if st.checkbox('Distortion'):
            with st.expander('Settings'):
                drive_db = st.number_input('drive db',value=25.0)
            fx_dict['distortion'] = Distortion(drive_db)

        if st.checkbox('Reverb'):
            with st.expander('Settings'):
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
            with st.expander('Settings'):
                col1,col2,col3 = st.columns(3)
                with col1:
                    delay_sec = st.number_input('delay seconds', value=0.5)
                with col2:
                    feedback = st.number_input('feedback',value=0.0)
                with col3:
                    mix = st.number_input('wet/dry mix',value=0.5)
            fx_dict['delay'] = Delay(delay_sec,feedback,mix)

        if st.checkbox('Phaser'):
            with st.expander('Settings'):
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
            with st.expander('Settings'):
                bit_depth = st.number_input('bit depth',value=0.8)
            fx_dict['bit_crush'] = Bitcrush(bit_depth)

        col1,_,col_mid,_,col2 = st.columns(5)
        with col_mid:
            st.button('Render Video', key='renderAud',on_click=render_audio, args=(fx_dict,))
            st.button('undo')
        with col1:
            st.button('Edit Video', on_click=deiterate_state)

def iterate_state():
    st.session_state.state +=1

def deiterate_state():
    st.session_state.state -=1


if __name__ == '__main__':
    if 'state' not in st.session_state:
        st.session_state.state = 1
    if 'duration' not in st.session_state:
        st.session_state.duration = None
    if 'resolution' not in st.session_state:
        st.session_state.resolution = (1920,1080)
    main()
