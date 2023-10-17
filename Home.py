import streamlit as st
import os

try:
    os.mkdir('pocket_editor_tmp/')
    os.mkdir('pocket_editor_tmp/concat_files/')
    os.mkdir('pocket_editor_tmp/output/')
except:
    pass


st.session_state.default_negative = 'deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck'

os.environ['PATH'] = 'pocket_editor_tmp/CurrentVid.mp4'
os.environ['OUTPUT'] = 'pocket_editor_tmp/output.mp4'
os.environ['TMP_AUDIO'] = 'pocket_editor_tmp/audio.wav'
os.environ['AUDIO_OUTPUT'] = 'pocket_editor_tmp/audio_output.wav'
os.environ['UNDO_PATH'] = 'pocket_editor_tmp/undoVid.mp4'
os.environ['SAVE_PATH'] = 'pocket_editor_tmp/concat_files/'
os.environ['OUT_PATH'] = 'pocket_editor_tmp/output/'
os.environ['AUDIO_REPLACE'] = 'pocket_editor_tmp/audio_replace.'

st.title('Pocket Editor')
st.write('Use the sidebar to navigate to different pages.')
st.divider()
st.markdown(
'''
```
[ Next Up ]
- More AI Pages
- VFX pipelines and more complex pipelines

[ Update 0.3.5 ]
- Frame Interpolation Model
- Photo Transformation Model
    - Upload an image and enter an instruction of how you want it modified.

[ Update 0.3.0 ]
- Moviepy Migration
    - 13 new vfx
- UI Improvements
- Support to add fx to only a segment of the video
    - For fx that require an effected time to be specified,
    note that the point you segment into is now the 0 second mark.
```

```
[ Update 0.2.0 ]
- Stable Diffusion
- Illusion Diffusion
```

```
[ Update 0.1.0 ]
- Video and audio editing
- Pre-built pipelines
- Clip manager
```
'''
)
