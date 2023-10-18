import streamlit as st
import os

try:
    os.mkdir('pocket_editor_tmp/')
    os.mkdir('pocket_editor_tmp/concat_files/')
    os.mkdir('pocket_editor_tmp/output/')
except:
    pass


st.session_state.default_negative = 'deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck'

st.session_state.PATH = 'pocket_editor_tmp/CurrentVid.mp4'
st.session_state.OUTPUT = 'pocket_editor_tmp/output.mp4'
st.session_state.TMP_AUDIO = 'pocket_editor_tmp/audio.wav'
st.session_state.AUDIO_OUTPUT = 'pocket_editor_tmp/audio_output.wav'
st.session_state.UNDO_PATH = 'pocket_editor_tmp/undoVid.mp4'
st.session_state.SAVE_PATH = 'pocket_editor_tmp/concat_files/'
st.session_state.OUT_PATH = 'pocket_editor_tmp/output/'
st.session_state.AUDIO_REPLACE = 'pocket_editor_tmp/audio_replace.'
st.session_state.GIF = 'pocket_editor_tmp/gif.gif'

st.title('Pocket Editor')
st.write('Use the sidebar to navigate to different pages.')
st.divider()
st.markdown(
'''
```
[ Update 0.4.0 ]
- Replace audio option in clip editor.
- Migration Fixes.
```

```
[ Update 0.3.5 ]
- Frame Interpolation Model.
- Photo Transformation Model.
    - Upload an image and enter an instruction of how you want it modified.
```

```
[ Update 0.3.0 ]
- Moviepy Migration.
    - 13 new vfx.
- UI Improvements.
- Support to add fx to only a segment of the video.
    - For fx that require an effected time to be specified,
    note that the point you segment into is now the 0 second mark.
```

```
[ Update 0.2.0 ]
- Stable Diffusion.
- Illusion Diffusion.
```

```
[ Update 0.1.0 ]
- Video and audio editing.
- Pre-built pipelines.
- Clip manager.
```
'''
)
