import streamlit as st
import os

os.mkdir('pocket_editor_tmp/')
os.mkdir('pocket_editor_tmp/concat_files/')
os.mkdir('pocket_editor_tmp/output/')

st.title('Pocket Editor')
st.divider()
st.markdown(
    """
### Pipeline:
Upload/download a video and select a preset modification option.
Right now there are 4 options.
- The Keegan Special
    - Distortion
    - Reverb
- The House Special
    - Everything
- Draftcon
    - Bitcrush
    - Phaser
- Disorienting
    - Delay
    - Reverb
### Clip Editor:
Use the Clip Manager to edit audio and video components of downloaded or uploaded videos.
You can download videos off youtube or any link that will provide the video to a simple GET request
EX: right click a video in discord, click copy link, then paste.  You can hit the undo button to undo
your most recent change but you can only go one step back. You can download the video any time by right clicking it 
and hitting save video as. You can also hit the "save to project manager" button
\n\n
### Video Editor:
The project manager allows you to 
organize and render multiple clips into one video. Simply drag and drop the file names and the videos will display in 
the order that they will be joined together. Once you are satisfied with the order you can hit render at the very bottom.\n
You can also hit the delete all files button or select files to delete at the bottom of the page.\n\nThe Pipeline page 
allows you to quickly create videos in a familiar format. EX: If you want to add reverb and distortion to a video you can 
quickly do it in one click\n\nTODO: user created pipelines. Right now just message me if you want anything.
"""
)
