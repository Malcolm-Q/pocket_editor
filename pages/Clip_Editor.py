import streamlit as st
import pytube
import requests
from urllib.parse import urlparse
import ffmpeg
import subprocess
import json
import os
from pedalboard import Pedalboard, Reverb, Distortion, Delay,Phaser, Bitcrush
from pedalboard.io import AudioFile

PATH = 'pocket_editor_tmp/CurrentVid.mp4'
OUTPUT = 'pocket_editor_tmp/output.mp4'
TMP_AUDIO = 'pocket_editor_tmp/audio.wav'
AUDIO_OUTPUT = 'pocket_editor_tmp/audio_output.wav'
SAVE_PATH = 'pocket_editor_tmp/concat_files/'
UNDO_PATH = 'pocket_editor_tmp/undoVid.mp4'

def main():
    if st.session_state.state == 0:
        st.title("Clip Editor")
        st.write("Download a youtube video or anything retrievable with a GET request.\n\nAlternatively you can upload a video.\n\nOnce a video is downloaded/uploaded you can edit it and the audio.")
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

    if st.session_state.state == 1:
        st.title("Edit Video")
        st.button('Save To Project Manager',on_click=save_video)
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
                "Clip Video",
                value=(0.0,float(st.session_state.duration))
            )
        speed = st.number_input('Video Speed',value=1.0)
        _,res1,xcol,res2,_ = st.columns(5)
        with res1:
            h_res = st.number_input('Horizontal Resolution',value=st.session_state.resolution[0])
        with xcol:
            st.markdown("<h1 style='text-align: center;'>X</h1>", unsafe_allow_html=True)
        with res2:
            v_res = st.number_input('Vertical Resolution',value=st.session_state.resolution[1])

        while h_res % 2 != 0:
            h_res += 1
        while v_res % 2 != 0:
            v_res += 1
        st.session_state.resolution = (h_res,v_res)

        st.divider()
        col1,_,col_mid,_,col2 = st.columns(5)

        with col1:
            st.button('Load Video', on_click=reverse_state)
        with col2:
            st.button('Edit Audio', on_click=iterate_state)
        with col_mid:
            st.button('Render Video', on_click=render_video, args=(speed,clip_start,clip_end,h_res,v_res))
            st.button('Undo', on_click=undo)

    if st.session_state.state == 2:
        st.title("Add Audio Effects")
        st.button('Save To Project Manager', on_click=save_video)
        with open(PATH, 'rb') as f:
            downloaded_video = f.read()
        st.video(downloaded_video)
        st.write("Select Effects:")

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
                bit_depth = st.number_input('bit depth',value=8.0)
            fx_dict['bit_crush'] = Bitcrush(bit_depth)

        col1,_,col_mid,_,col2 = st.columns(5)
        with col1:
            st.button('Edit Video', on_click=reverse_state)
        with col2:
            st.button('Next', on_click=iterate_state)
        with col_mid:
            st.button('Render Video', on_click=render_audio, args=(fx_dict,))
            st.button('undo')


def save_video():
    get_number_of_files()
    with open(PATH, 'rb') as source:
        with open(SAVE_PATH+f'clip_{st.session_state.number_of_files}.mp4', 'wb') as destination:
            destination.write(source.read())


def get_number_of_files():
    files_and_directories = os.listdir(SAVE_PATH)
    files = [f for f in files_and_directories if os.path.isfile(os.path.join(PATH, f))]
    st.session_state.number_of_files = len(files)

def process_upload(video):
    if video is not None:
        with open(PATH, 'wb') as f:
            f.write(video.read())
        get_video_info()
        iterate_state()


def render_video(video_speed, start_time, end_time, h_res, v_res):
    with st.spinner('rendering...'):
        try:
            input_stream = ffmpeg.input(PATH, ss=start_time, to=end_time)

            audio = input_stream.audio
            video = input_stream.video

            audio = audio.filter('atempo', video_speed)
            video = video.filter('setpts', f'{1/video_speed}*PTS').filter('scale', h_res, v_res)

            (
                ffmpeg.output(audio, video, OUTPUT)
                .run(overwrite_output=True)
            )
            st.success(f"Video edited and saved")

            try:
                os.remove(UNDO_PATH)
            except Exception:
                pass
            os.rename(PATH,UNDO_PATH)
            os.rename(OUTPUT, PATH)
            st.session_state.duration = end_time - start_time
        except subprocess.CalledProcessError as e:
            st.error(f"Error editing video: {e}")


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


def undo():
    if os.path.exists(UNDO_PATH):
        os.remove(PATH)
        os.rename(UNDO_PATH,PATH)
    else:
        st.error('Cannot undo further...')

def iterate_state():
    st.session_state.state += 1

def reverse_state():
    st.session_state.state -= 1

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
        get_video_info()
        st.session_state.state += 1

def get_video_info():
    try:
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration:stream=width,height',
            '-of', 'json',
            PATH
        ]
        probe_result = subprocess.check_output(probe_cmd, stderr=subprocess.STDOUT)
        probe_data = json.loads(probe_result)
        duration = probe_data['format']['duration']
        st.session_state.duration = float(duration)
        video_stream = probe_data['streams'][0]
        resolution = (video_stream['width'], video_stream['height'])
        st.session_state.resolution = resolution
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error getting video information: {e}")

if __name__ == "__main__":
    if 'state' not in st.session_state:
        st.session_state.state = 0
    if 'duration' not in st.session_state:
        st.session_state.duration = None
    if 'resolution' not in st.session_state:
        st.session_state.resolution = (1920,1080)
    main()
