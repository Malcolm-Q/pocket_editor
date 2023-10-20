import streamlit as st
st.title('Inpainting Pipeline')
st.write('Face Detection, Segmentation, Mask Post-Processing, ControlNetInpatin')
st.divider()

with st.spinner('Importing'):
    import cv2
    from PIL import Image
    import numpy as np
    import torch

    from controlnet_aux import OpenposeDetector
    from diffusers import StableDiffusionInpaintPipeline, ControlNetModel, UniPCMultistepScheduler
    from kornia.filters import gaussian_blur2d

    from kornia.morphology import dilation, closing
    from transformers import SamModel, SamProcessor

    import kornia as K
    from kornia.core import Tensor
    from kornia.contrib import FaceDetector, FaceDetectorResult, FaceKeypoint

    from lib.controlnet_inpaint import *

if 'face_detection' not in st.session_state:
    with st.spinner('Loading Face Detection'):
        st.session_state.face_detection = FaceDetector()

if 'controlnet' not in st.session_state:
    with st.spinner('Loading ControlNet'):
        st.session_state.controlnet = ControlNetModel.from_pretrained(
            "fusing/stable-diffusion-v1-5-controlnet-openpose", torch_dtype=torch.float16
        )

if 'inpaint_pipe' not in st.session_state:
    with st.spinner('Loading Pipeline'):
        st.session_state.inpaint_pipe = StableDiffusionControlNetInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting", controlnet=controlnet, torch_dtype=torch.float16
        ).to('cuda')
        st.session_state.pipe.scheduler = UniPCMultistepScheduler.from_config(st.session_state.pipe.scheduler.config)
    
if 'openpose' not in st.session_state:
    with st.spinner('Loading OpenPose'):
        st.session_state.openpose = OpenposeDetector.from_pretrained('lllyasviel/ControlNet')

if 'sam' not in st.session_state:
    with st.spinner('Loading SAM'):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.session_state.sam = SamModel.from_pretrained("facebook/sam-vit-huge").to(device)
        st.session_state.processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")


def main():
    image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if image is not None:
        st.image(image, caption="Original Image", use_column_width=True)
        prompt = st.text_input("Enter Your Prompt")
        if prompt is not None:
            st.button('Transform Image',on_click=forward,args=(None,Image.open(image),prompt))


def detect_face(input):

    # Preprocessing
    img = K.image_to_tensor(np.array(input), keepdim=False)
    img = K.color.bgr_to_rgb(img.float())
    
    with torch.no_grad():
        dets = st.session_state.face_detection(img)
        
    return [FaceDetectorResult(o) for o in dets[0]]

def process_face(dets):
    vis_threshold = 0.8
    faces = []
    hairs = []
    
    for b in dets:
        if b.score  < vis_threshold:
            continue
    
        reye_kpt=b.get_keypoint(FaceKeypoint.EYE_RIGHT).int().tolist()
        leye_kpt=b.get_keypoint(FaceKeypoint.EYE_LEFT).int().tolist()
        rmou_kpt=b.get_keypoint(FaceKeypoint.MOUTH_RIGHT).int().tolist()
        lmou_kpt=b.get_keypoint(FaceKeypoint.MOUTH_LEFT).int().tolist()
        nose_kpt=b.get_keypoint(FaceKeypoint.NOSE).int().tolist()
    
        faces.append([nose_kpt,
                     rmou_kpt,
                     lmou_kpt,
                     reye_kpt,
                     leye_kpt
                    ])
    
        # point above
        top=((b.top_right + b.top_left)/2).int().tolist()
        bot=((b.bottom_right + b.bottom_left)/2).int().tolist()
        face_h = np.abs(top[1]-bot[1])
        top_margin=[top[0], top[1]-face_h*0.1]
    
        hairs.append([
                          top_margin
                    ])

    return faces, hairs

def build_mask(image, faces, hairs):

    # 1. Segmentation
    input_points = faces  # 2D location of the face
    
    with torch.no_grad():
        inputs = st.session_state.processor(image, input_points=input_points, return_tensors="pt").to(device)
        outputs = st.session_state.sam(**inputs)
        
        masks = st.session_state.processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu()
        )
        scores = outputs.iou_scores
    
    input_points = hairs  # 2D location of the face
    
    with torch.no_grad():
        inputs = st.session_state.processor(image, input_points=input_points, return_tensors="pt").to(device)
        outputs = st.session_state.sam(**inputs)
        
        h_masks = st.session_state.processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu()
        )
        h_scores = outputs.iou_scores

    # 2. Post-processing
    mask=masks[0][0].all(0) | h_masks[0][0].all(0)
    
    # dilation
    tensor = mask[None,None,:,:]
    kernel = torch.ones(3, 3)
    mask = closing(tensor, kernel)[0,0].bool()
    
    return mask

def build_mask_multi(image, faces, hairs):

    all_masks = []
    
    for face,hair in zip(faces,hairs):
        # 1. Segmentation
        input_points = [face]  # 2D location of the face
        
        with torch.no_grad():
            inputs = st.session_state.processor(image, input_points=input_points, return_tensors="pt").to(device)
            outputs = st.session_state.sam(**inputs)
            
            masks = st.session_state.processor.image_processor.post_process_masks(
                outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu()
            )
            scores = outputs.iou_scores
        
        input_points = [hair]  # 2D location of the face
        
        with torch.no_grad():
            inputs = st.session_state.processor(image, input_points=input_points, return_tensors="pt").to(device)
            outputs = st.session_state.sam(**inputs)
            
            h_masks = st.session_state.processor.image_processor.post_process_masks(
                outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu()
            )
            h_scores = outputs.iou_scores
    
        # 2. Post-processing
        mask=masks[0][0].all(0) | h_masks[0][0].all(0)
        
        # dilation
        mask_T = mask[None,None,:,:]
        kernel = torch.ones(3, 3)
        mask = closing(mask_T, kernel)[0,0].bool()

        all_masks.append(mask)

    mask = all_masks[0]
    for next_mask in all_masks[1:]:
        mask = mask | next_mask
    
    return mask


def synthesis(image, mask, prompt="", n_prompt="", num_steps=20, seed=0, remix=True):
    
    # 1. Get pose
    with torch.no_grad():
        pose_image = st.session_state.openpose(image)
        pose_image=pose_image.resize(image.size)
    
    # generate image
    generator = torch.manual_seed(seed)
    new_image = st.session_state.inpaint_pipe(
        prompt,
        negative_prompt = n_prompt,
        generator=generator,
        num_inference_steps=num_steps,
        image=image,
        control_image=pose_image,
        mask_image=(mask==False).float().numpy(),
    ).images
    
    if remix:
        for idx in range(len(new_image)):
            mask =  gaussian_blur2d(1.0*mask[None,None,:,:],
                                    kernel_size=(11, 11),
                                    sigma=(29, 29)
                                   ).squeeze().clip(0,1)
            
            new_image[idx] = (mask[:,:,None]*np.asarray(image) + (1-mask[:,:,None])*np.asarray(new_image[idx].resize(image.size))).int().numpy()
    
    return new_image


def forward(image_cam, image_upload, prompt="", n_prompt=None, num_steps=20, seed=0, original_resolution=False):

    if image_cam is None:
        image = image_upload
    else:
        image = image_cam

    if not original_resolution:
        w,h = image.size
        ratio = 512/h
        new_size = int(w*ratio), int(h*ratio)
        image = image.resize(new_size)
        
    # detect face
    dets = detect_face(image)

    # segment hair and face
    faces, hairs = process_face(dets)

    # build mask
    mask = build_mask_multi(image, faces, hairs)

    # synthesise
    new_image = synthesis(image,mask, prompt, n_prompt, num_steps=num_steps, seed=seed)
    
    return new_image


if __name__ == '__main__':
    main()