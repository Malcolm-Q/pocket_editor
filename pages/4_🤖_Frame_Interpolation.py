import os
import streamlit as st
st.title("Frame Interpolation")
st.write('Blends two frames together to create a smooth transition between them.')
st.divider()

with st.spinner('Importing'):
    import sys

    import numpy as np
    import tensorflow as tf
    from moviepy.editor import concatenate_videoclips, ImageClip
    from PIL import Image
    from interp.eval import interpolator, util

    from huggingface_hub import snapshot_download

    from image_tools.sizes import resize_and_crop


if 'interp_model' not in st.session_state:
    with st.spinner('Loading model'):
        st.session_state.interp_model = interpolator.Interpolator(snapshot_download(repo_id="akhaliq/frame-interpolation-film-style"), None)


def main():
    
    st.write('Upload two images below.')
    col1, col2 = st.columns(2)
    with col1:
        frame1 = st.file_uploader('Frame 1')
        if frame1:
            st.image(frame1)
    with col2:
        frame2 = st.file_uploader('Frame 2')
        if frame2:
            st.image(frame2)
    
    if frame1 and frame2:
        times_to_interpolate = st.slider('Interpolation Amount', 1, 7, 4,help='The higher the number, the longer and smoother the output will be.')
        st.button('Interpolate', on_click=lambda: st.video(predict(frame1, frame2, times_to_interpolate)))


def resize(width, img):
    basewidth = width
    img = Image.open(img)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    return img


def resize_img(img1, img2):
    img_target_size = Image.open(img1)
    img_to_resize = resize_and_crop(
        img2,
        (img_target_size.size[0], img_target_size.size[1]),
        crop_origin="middle"
    )
    img_to_resize.save('resized_img2.png')


def predict(frame1, frame2, times_to_interpolate):
    frame1 = resize(256, frame1)
    frame2 = resize(256, frame2)

    frame1.save("test1.png")
    frame2.save("test2.png")

    resize_img("test1.png", "test2.png")
    input_frames = ["test1.png", "resized_img2.png"]

    frames = list(
        util.interpolate_recursively_from_files(
            input_frames, times_to_interpolate, st.session_state.interp_model))
    disk_frames = []
    for i, frame in enumerate(frames):
        Image.fromarray((frame*255).astype(np.uint8)).save(f"frame{i}.png")
        disk_frames.append(f"frame{i}.png")
    frames = [ImageClip(frame).set_duration(1/30) for frame in disk_frames]
    concat_clip = concatenate_videoclips(frames, method="compose")
    concat_clip.write_videofile("out.mp4", fps=30)
    return "out.mp4"

if __name__ == "__main__":
    main()