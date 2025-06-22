import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import cv2
from sklearn.cluster import KMeans
import json

print("Loading CLIP model...")
model_name = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)
print("CLIP model loaded.")

CLOTHING_CATEGORIES = [
    "t-shirt", "shirt", "blouse", "sweater", "cardigan", "hoodie", # Tops
    "jeans", "pants", "shorts", "skirt", # Bottoms
    "dress", "jumpsuit", # One-piece
    "jacket", "coat", "blazer", # Outerwear
    "sneakers", "boots", "sandals", "heels" # Shoes
]

def classify_image_with_clip(image: Image.Image):
    """
    Classifies an image into one of the predefined clothing categories using CLIP.
    """
    texts = [f"a photo of a {label}" for label in CLOTHING_CATEGORIES]
    
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
    
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    
    best_prob_index = torch.argmax(probs).item()
    best_category = CLOTHING_CATEGORIES[best_prob_index]
    
    if best_category in ["t-shirt", "shirt", "blouse", "sweater", "cardigan", "hoodie"]:
        return "top"
    elif best_category in ["jeans", "pants", "shorts", "skirt"]:
        return "bottom"
    elif best_category in ["jacket", "coat", "blazer"]:
        return "outerwear"
    elif best_category in ["sneakers", "boots", "sandals", "heels"]:
        return "shoes"
    else:
        return "one-piece"

def get_image_embedding(image: Image.Image):
    """
    Gets the CLIP image embedding (vector) for style analysis.
    """
    with torch.no_grad():
        inputs = processor(images=image, return_tensors="pt")
        image_features = model.get_image_features(**inputs)
    return image_features.cpu().numpy().tolist()[0]


def extract_dominant_colors(image_path, k=5):
    """
    Extracts k dominant colors from an image using K-Means clustering.
    """
    try:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        pixels = img.reshape((-1, 3))
        pixels = np.float32(pixels)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        centers = np.uint8(centers)
        hex_colors = [f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}' for c in centers]
        
        return json.dumps(hex_colors)
    except Exception as e:
        print(f"Color extraction failed: {e}")
        return json.dumps(['#ffffff', '#000000'])