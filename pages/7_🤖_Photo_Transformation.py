import streamlit as st
import math
import random

import torch
from PIL import Image, ImageOps
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

example_instructions = [
    "Make it a picasso painting",
    "as if it were by modigliani",
    "convert to a bronze statue",
    "Turn it into an anime.",
    "have it look like a graphic novel",
    "make him gain weight",
    "what would he look like bald?",
    "Have him smile",
    "Put him in a cocktail party.",
    "move him at the beach.",
    "add dramatic lighting",
    "Convert to black and white",
    "What if it were snowing?",
    "Give him a leather jacket",
    "Turn him into a cyborg!",
    "make him wear a beanie",
]

def main():
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None
    st.title("Photo Transformation")
    if 'pix2pix' not in st.session_state:
        st.toast('Loading model...')
        st.session_state.pix2pix = StableDiffusionInstructPix2PixPipeline.from_pretrained("timbrooks/instruct-pix2pix", torch_dtype=torch.float16, safety_checker=None).to("cuda")
        st.session_state.pix2pix.scheduler = EulerAncestralDiscreteScheduler.from_config(st.session_state.pix2pix.scheduler.config)
    st.write('Photoshop images with text instructions.')
    st.divider()
    if st.session_state.edited_image is not None:
        st.image(st.session_state.edited_image, caption="Edited Image", use_column_width=True)
        with st.exapnder('Image doesn\'t look right?'):
            st.write(
                'If the image isn\'t changing enough, try increasing the text cfg and lowering the image cfg. '
                'If the image is changing too much, try decreasing the text cfg and increasing the image cfg.'
            )
        st.divider()

    input_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if input_image is not None:
        image = Image.open(input_image)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        st.image(image, caption="Original Image", use_column_width=True)
        instruct = st.text_input("Instructions",value=random.choice(example_instructions))
        col1,col2 = st.columns(2)
        with col1:
            text_cfg = st.number_input('Text CFG', min_value=2.0,max_value=10.0,step=0.5,value=7.5,help='Increase if image isn\'t changing enough')
        with col2:
            image_cfg = st.number_input('Image CFG', min_value=0.5,max_value=4.0,step=0.1,value=1.5,help='Decrease if image isn\'t changing enough')
        if instruct is not None:
            st.button("Generate", on_click=generate, args=(image, instruct, 50, True, 0, True, text_cfg, image_cfg))

def generate(
    input_image: Image.Image,
    instruction: str,
    steps: int,
    randomize_seed: bool,
    seed: int,
    randomize_cfg: bool,
    text_cfg_scale: float,
    image_cfg_scale: float,
):
    seed = random.randint(0, 100000) if randomize_seed else seed
    text_cfg_scale = round(random.uniform(6.0, 9.0), ndigits=2) if randomize_cfg else text_cfg_scale
    image_cfg_scale = round(random.uniform(1.2, 1.8), ndigits=2) if randomize_cfg else image_cfg_scale

    width, height = input_image.size
    factor = 512 / max(width, height)
    factor = math.ceil(min(width, height) * factor / 64) * 64 / min(width, height)
    width = int((width * factor) // 64) * 64
    height = int((height * factor) // 64) * 64
    input_image = ImageOps.fit(input_image, (width, height), method=Image.Resampling.LANCZOS)
    st.write('Done Processing')

    if instruction == "":
        return [input_image, seed]

    generator = torch.manual_seed(seed)
    st.session_state.edited_image = st.session_state.pix2pix(
        instruction, image=input_image,
        guidance_scale=text_cfg_scale, image_guidance_scale=image_cfg_scale,
        num_inference_steps=steps, generator=generator,
    ).images[0]

if __name__ == '__main__':
    main()