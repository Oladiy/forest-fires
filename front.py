import streamlit as st
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import segmentation_models_pytorch as smp
import torch.nn.functional as F

PATH_WEIGHTS = "models/best_model.pth"


def load_image(image_file):
    image = Image.open(image_file).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),

    ])
    image = transform(image).unsqueeze(0)
    return image, image_file

def overlay_mask(image, mask, alpha=0.5):
    image = np.array(image).astype(np.float32) / 255.0
    mask = mask.cpu().numpy().squeeze()
    
    mask = np.stack([mask, mask, mask], axis=-1)
    
    overlay = (1 - alpha) * image + alpha * mask
    
    return overlay

def infer_and_plot(image, model, alpha):

    with torch.no_grad():
        output = model(image)

    mask = output.argmax(dim=1)

    orig_image = Image.fromarray((image.squeeze().permute(1, 2, 0).cpu().numpy()*255.0).astype(np.uint8))

    mask_result = np.stack([mask, mask, mask], axis=-1)
    print(mask_result.shape)
    mask_result = Image.fromarray((mask_result.squeeze()*255.0).astype(np.uint8))
    result_image = overlay_mask(orig_image, mask, alpha)

    return result_image, mask_result

st.title("Детекция пожаров")

alpha = st.slider("Прозрачность маски", 0.0, 1.0, 0.5)

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
st.success("Модель загружена!")

image_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])
if image_file:
    image, orig_image_file = load_image(image_file)

    result_image, mask_result = infer_and_plot(image, model, alpha)

    st.image(mask_result)
    
    st.image(result_image, caption="Overlay", use_column_width=True)



    st.image(Image.fromarray((image.squeeze().permute(1, 2, 0).cpu().numpy()*255.0).astype(np.uint8)), caption="Оригинальное изображение", use_column_width=True)
