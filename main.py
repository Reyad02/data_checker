from fastapi import FastAPI, HTTPException
from dotenv import dotenv_values
import requests

app = FastAPI(title="Hive AI Text Moderation API")

env_vars = dotenv_values(".env")
HIVE_API_KEY = env_vars.get("HIVE_API_KEY")

HIVE_TEXT_URL = "https://api.thehive.ai/api/v3/hive/text-moderation"
HIVE_VISUAL_URL = "https://api.thehive.ai/api/v3/hive/visual-moderation"

THRESHOLD_FOR_TEXT = 2 
# 2 FOR WARNING
# 3 FOR EXTREME

THRESHOLD_FOR_VISUAL = 1

BAD_TAGS_FOR_VISUAL_CONTENT = [
    "general_nsfw",
    "yes_sex_toy",
    "yes_female_nudity",
    "yes_male_nudity",
    "yes_sexual_activity",
    "yes_breast",
    "yes_genitals",
    "yes_butt",
    "yes_sexual_intent",
    "yes_undressed",
    "yes_realistic_nsfw",
    "animated_gun",
    "gun_in_hand",
    "gun_not_in_hand",
    "knife_in_hand",
    "knife_not_in_hand",
    "a_little_bloody",
    "other_blood",
    "very_bloody",
    "yes_fight",
    "yes_pills",
    "illicit_injectables",
    "yes_nazi",
    "yes_kkk",
    "yes_confederate",
    "yes_middle_finger",
    "yes_terrorist",
    "hanging",
    "noose",
    "animated_corpse",
    "human_corpse",
    "yes_self_harm",
    "yes_emaciated_body",
    "animal_genitalia_and_human",
    "animal_genitalia_only",
    "animated_animal_genitalia",
    "yes_animal_abuse"
]



@app.post("/moderate-text")
def moderate_text(text: str):
    payload = {
        "input": [
            {
                "text": text
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {HIVE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(HIVE_TEXT_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    classes = data["output"][0]["classes"]
    
    bad_classes = []
    for cls in classes:
        if cls["value"] >= THRESHOLD_FOR_TEXT:
            bad_classes.append(cls)
            
            
    return {
        "status": "bad" if bad_classes else "good",
        "bad_categories": bad_classes,
        "all_categories": classes
    }
    
    

@app.post("/moderate-visual")
def moderate_visual(media_url: str):
    """
    Supports image OR video URLs
    Example:
    media_url = https://d24edro6ichpbm.thehive.ai/demo_static_media/nsfw/nsfw_4.jpg
    """

    payload = {
        "input": [
            {
                "media_url": media_url
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {HIVE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        HIVE_VISUAL_URL,
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
        
    data = response.json()
    classes = data["output"][0]["classes"]
    
    classes_more_than_threshold_value = []
    for cls in classes:
        if cls["value"] >= THRESHOLD_FOR_VISUAL:
            classes_more_than_threshold_value.append(cls)
    
    bad_classes = []
    for cls in classes_more_than_threshold_value:
        if cls["class"] in BAD_TAGS_FOR_VISUAL_CONTENT:
            bad_classes.append(cls)
            
        
    return {
        "status": "bad" if bad_classes else "good",
        "bad_categories": bad_classes,
        "all_categories": classes
    }