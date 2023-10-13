import streamlit as st
import torch
from diffusers import StableDiffusionPipeline
from IPython.display import clear_output

def main():
  model_loader, model_runner = st.tabs(['Load a Model','Run Your Model'])
  with model_loader:
    model_load_interface()

  if st.session_state.stable_diff_pipe is not None:
    with model_runner:
      model_run_interface()

def model_load_interface():
  st.title('Stable Diffusion Model Loader')
  st.markdown('Models can be loaded directly off [HuggingFace](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)')
  st.markdown('Some popular models are:  \n    - stabilityai/stable-diffusion-xl-base-1.0  \n    - nerijs/pixel-art-xl  \n    - prompthero/openjourney')
  st.divider()
  model = st.text_input('Enter the name of a model to load',value='stabilityai/stable-diffusion-2-1')

  if st.button('Load model'):
    with st.spinner('This may take a while...'):
      try:
        st.session_state.stable_diff_pipe = StableDiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16)
        st.sidebar.success('Model Loaded!')
      except Exception:
        st.sidebar.error('ERROR: Unable to load model. Did you enter the name correctly?')
      try:
        st.session_state.stable_diff_pipe = st.session_state.stable_diff_pipe.to("cuda")
      except Exception:
        st.sidebar.error('WARNING: You are not using a GPU.  \nThis will be very slow.\n  Google "Google Colab Use GPU"')

def model_run_interface():
  if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

  prompt = st.text_input('Enter your prompt...',placeholder='A medieval village in Europe...')
  negative_prompt = st.text_input('Enter a negative prompt...',value='unrealistic, cartoon, drawing')

  if st.session_state.generated_image is not None:
    st.image(st.session_state.generated_image)
  else:
    st.markdown('*Your Image Will Go Here...*')
  st.button('Generate...', on_click=generate_image, args=(prompt,negative_prompt))
  if st.button('Delete Model and Free Memory'):
    del st.session_state.stable_diff_pipe
    


def generate_image(prompt, negative_prompt):
  st.session_state.generated_image = st.session_state.stable_diff_pipe(prompt = prompt, negative_prompt = negative_prompt).images[0]


if __name__ == '__main__':
  if 'stable_diff_pipe' not in st.session_state:
    st.session_state.stable_diff_pipe = None
  main()