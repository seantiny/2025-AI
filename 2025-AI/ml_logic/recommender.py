# ml_logic/recommender.py
import random
import json

def generate_outfits(items, weather):
    """
    Generates outfit recommendations based on items and weather.
    """
    outfits = []
    
    tops = [item for item in items if item.category == 'top']
    bottoms = [item for item in items if item.category == 'bottom']
    outerwear = [item for item in items if item.category == 'outerwear']
    shoes = [item for item in items if item.category == 'shoes']

    if not tops or not bottoms or not shoes:
        return []

    is_warm = weather['temp'] > 15
    is_cold = weather['temp'] < 14
    is_rainy = 'rain' in weather['description']

    for _ in range(3):
        outfit = {}
        #TO DO: make ai
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        shoe = random.choice(shoes)
        
        outfit['top'] = top
        outfit['bottom'] = bottom
        outfit['shoes'] = shoe
        
        if is_cold and outerwear:
            outfit['outerwear'] = random.choice(outerwear)
        elif is_rainy and outerwear:
            rain_jackets = [ow for ow in outerwear if 'jacket' in ow.filename]
            if rain_jackets:
                outfit['outerwear'] = random.choice(rain_jackets)
            elif outerwear: # fallback to any outerwear
                outfit['outerwear'] = random.choice(outerwear)
        
        label = "Casual Outfit"
        if is_warm:
            label = "Outfit for Warm Weather"
        if is_cold:
            label = "Outfit for Cold Weather"
        if is_rainy:
            label += " (Don't forget an umbrella!)"
            
        outfit['label'] = label
        outfits.append(outfit)
        
    return outfits