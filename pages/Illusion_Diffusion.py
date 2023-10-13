import streamlit as st

import torch
from PIL import Image
import random
from diffusers import (
    DiffusionPipeline,
    AutoencoderKL,
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    StableDiffusionLatentUpscalePipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionControlNetImg2ImgPipeline,
    DPMSolverMultistepScheduler,
    EulerDiscreteScheduler
)
import time

st.session_state.default_negative = 'deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck'

def center_crop_resize(img, output_size=(512, 512)):
    width, height = img.size

    new_dimension = min(width, height)
    left = (width - new_dimension)/2
    top = (height - new_dimension)/2
    right = (width + new_dimension)/2
    bottom = (height + new_dimension)/2

    img = img.crop((left, top, right, bottom))
    img = img.resize(output_size)

    return img

def common_upscale(samples, width, height, upscale_method, crop=False):
        if crop == "center":
            old_width = samples.shape[3]
            old_height = samples.shape[2]
            old_aspect = old_width / old_height
            new_aspect = width / height
            x = 0
            y = 0
            if old_aspect > new_aspect:
                x = round((old_width - old_width * (new_aspect / old_aspect)) / 2)
            elif old_aspect < new_aspect:
                y = round((old_height - old_height * (old_aspect / new_aspect)) / 2)
            s = samples[:,:,y:old_height-y,x:old_width-x]
        else:
            s = samples

        return torch.nn.functional.interpolate(s, size=(height, width), mode=upscale_method)

def upscale(samples, upscale_method, scale_by):
        width = round(samples["images"].shape[3] * scale_by)
        height = round(samples["images"].shape[2] * scale_by)
        s = common_upscale(samples["images"], width, height, upscale_method, "disabled")
        return (s)

# Inference function
def inference(
    control_image: Image.Image,
    prompt: str,
    negative_prompt: str,
    guidance_scale: float = 7.5,
    controlnet_conditioning_scale: float = 0.4,
    control_guidance_start: float = 0,    
    control_guidance_end: float = 1,
    upscaler_strength: float = 1,
    seed: int = -1,
    sampler = "DPM++ Karras SDE",
):
    control_image_small = center_crop_resize(control_image)
    control_image_large = center_crop_resize(control_image, (1024, 1024))

    st.session_state.main_pipe.scheduler = st.session_state.SAMPLER_MAP[sampler](st.session_state.main_pipe.scheduler.config)
    my_seed = random.randint(0, 2**32 - 1) if seed == -1 else seed
    generator = torch.Generator(device="cuda").manual_seed(my_seed)
    
    out = st.session_state.main_pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=control_image_small,
        guidance_scale=float(guidance_scale),
        controlnet_conditioning_scale=float(controlnet_conditioning_scale),
        generator=generator,
        control_guidance_start=float(control_guidance_start),
        control_guidance_end=float(control_guidance_end),
        num_inference_steps=15,
        output_type="latent"
    )
    upscaled_latents = upscale(out, "nearest-exact", 2)
    out_image = st.session_state.image_pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        control_image=control_image_large,        
        image=upscaled_latents,
        guidance_scale=float(guidance_scale),
        generator=generator,
        num_inference_steps=20,
        strength=upscaler_strength,
        control_guidance_start=float(control_guidance_start),
        control_guidance_end=float(control_guidance_end),
        controlnet_conditioning_scale=float(controlnet_conditioning_scale)
    )

    return out_image["images"][0]

def make_inference(img, prompt, neg, ill_strength):
  st.session_state.generated_image = inference(img, prompt, st.session_state.default_negative, controlnet_conditioning_scale=ill_strength)

def main():
  st.title('Illusion Diffusion Model')
  if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
  if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
  if not st.session_state.model_loaded:
    st.write('This may take a while to load...')
    with st.spinner():
      st.session_state.BASE_MODEL = "SG161222/Realistic_Vision_V5.1_noVAE"

      st.session_state.vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float16)
      st.session_state.controlnet = ControlNetModel.from_pretrained("monster-labs/control_v1p_sd15_qrcode_monster", torch_dtype=torch.float16)
      st.session_state.main_pipe = StableDiffusionControlNetPipeline.from_pretrained(
          st.session_state.BASE_MODEL,
          controlnet=st.session_state.controlnet,
          vae=st.session_state.vae,
          safety_checker=None,
          torch_dtype=torch.float16,
      ).to("cuda")

      st.session_state.image_pipe = StableDiffusionControlNetImg2ImgPipeline(**st.session_state.main_pipe.components)

      st.session_state.SAMPLER_MAP = {
          "DPM++ Karras SDE": lambda config: DPMSolverMultistepScheduler.from_config(config, use_karras=True, algorithm_type="sde-dpmsolver++"),
          "Euler": lambda config: EulerDiscreteScheduler.from_config(config),
      }
      st.session_state.model_loaded = True
      st.rerun()
  else:
      uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

      if uploaded_image is not None:
          pil_image = Image.open(uploaded_image)
          st.image(pil_image, caption="Uploaded Image", use_column_width=True)
      prompt = st.text_input('Prompt...',help='The image you uploaded will look like this.')
      illusion_strength = st.slider('Illusion Strength',min_value=0.0,max_value=4.0,value=1.0)
      if st.session_state.generated_image is not None:
        st.image(st.session_state.generated_image)
      if uploaded_image is not None:
        st.button('Submit',on_click=make_inference,args=(pil_image,prompt,'low quality',illusion_strength))

if __name__ == '__main__':
  main()
