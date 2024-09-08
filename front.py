import streamlit as st
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import segmentation_models_pytorch as smp
import torch.nn.functional as F

PATH_WEIGHTS = "best_model_rgb.pth"

def load_image(image_file):
    image = Image.open(image_file).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])
    image = transform(image).unsqueeze(0)
    return image, image_file

def overlay_mask(image, mask, alpha=0.5):
    image = np.array(image).astype(np.float32) / 255.0
    mask = mask.cpu().numpy().squeeze()
    
    mask = np.stack([mask, mask, mask], axis=-1)
    
    overlay = (1 - alpha) * image + alpha * mask
    
    return overlay

def infer_and_plot(image, model, alpha, confidence_threshold):
    with torch.no_grad():
        output = model(image)
    
    probabilities = torch.sigmoid(output)
    mask = (probabilities > confidence_threshold).float().squeeze(0)
    
    orig_image = Image.fromarray((image.squeeze().permute(1, 2, 0).cpu().numpy() * 255.0).astype(np.uint8))
    
    mask_result = Image.fromarray((mask.cpu().numpy().squeeze() * 255.0).astype(np.uint8))
    
    result_image = overlay_mask(orig_image, mask, alpha)

    return result_image, mask_result

st.title("Детекция пожаров")

alpha = st.slider("Прозрачность маски", 0.0, 1.0, 0.5)
confidence_threshold = st.slider("Порог модели", 0.0, 1.0, 0.5)

@st.cache_resource
def load_model():
    model = smp.Unet(
        encoder_name="efficientnet-b3",
        encoder_weights="imagenet",
        in_channels=3,
        classes=1
    )
    
    checkpoint = torch.load(PATH_WEIGHTS, map_location=torch.device('cpu'))
    
    model.load_state_dict(checkpoint["model_state_dict"])
    
    model.eval()
    return model

model = load_model()
st.success("Модель загружена")

image_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])
if image_file:
    image, orig_image_file = load_image(image_file)

    result_image, mask_result = infer_and_plot(image, model, alpha, confidence_threshold)

    st.image(mask_result, caption="Маска", use_column_width=True)
    st.image(result_image, caption="Overlay", use_column_width=True)
    st.image(Image.fromarray((image.squeeze().permute(1, 2, 0).cpu().numpy() * 255.0).astype(np.uint8)), caption="Оригинальное изображение", use_column_width=True)
