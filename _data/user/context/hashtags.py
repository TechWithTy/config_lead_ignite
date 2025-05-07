# Hashtags context data for the bot
from pydantic import BaseModel
from typing import List

class Hashtags(BaseModel):
    default_tags: List[str] = [
        "#AI",
        "#MachineLearning",
        "#DataScience",
        "#Automation",
        "#Technology",
    ]
    custom_tags: List[str] = []

hashtags = Hashtags()
