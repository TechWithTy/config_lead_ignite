from pydantic import BaseModel, Field

from enum import Enum
from config._data.user.context.ai_config import ViralPostingConfig

# * Enum for supported text LLMs
def _default_text_llm():
    return TextLLMType.POLLINATIONS_TEXT_ADVANCED

class TextLLMType(str, Enum):
    POLLINATIONS_TEXT = "Pollinations_Text"
    POLLINATIONS_TEXT_ADVANCED = "Pollinations_Text_Advanced"
    POLLINATIONS_TEXT_COMPLETION = "Pollinations_Text_Completion"
    OPENAI = "OpenAI"
    HUGGINGFACE = "HuggingFace"
    DEEPSEEK = "DeepSeek"
    CLAUDE = "Claude"
    CUSTOM = "Custom"

# * Enum for supported image LLMs
def _default_image_llm():
    return ImageLLMType.POLLINATIONS_IMAGE_GET

class ImageLLMType(str, Enum):
    POLLINATIONS_IMAGE = "Pollinations_Image"
    POLLINATIONS_IMAGE_GET = "Pollinations_Image_Get"
    OPENAI = "OpenAI"
    HUGGINGFACE = "HuggingFace"
    GIPHY = "Giphy"
    CUSTOM = "Custom"

class GenerateTextConfig(BaseModel):
    enabled: bool = True
    user_description: str = "If true, generates a tailored AI Social Media Post and An Image Or Gif"
    prompt: str = "Create a high-quality AI-generated image relevant to the blog content."
    LLM: TextLLMType = Field(default_factory=_default_text_llm)
    backup: str = ""

class GenerateImageConfig(BaseModel):
    enabled: bool = True
    user_description: str = "If true, generates a fallback image if the prompt fails to create one"
    width: int = 1024
    height: int = 1024
    prompt: str = "Create a high-quality AI-generated image relevant to the blog content."
    LLM: ImageLLMType = Field(default_factory=_default_image_llm)
    backup: str = ""

class FetchCandidConfig(BaseModel):
    enabled: bool = True
    user_description: str = "If true, fetches a candid media from available sources"
    prompt: str = "return atleast 3 candid search terms in the returned object in an array"

class FetchGifConfig(BaseModel):
    enabled: bool = True
    user_description: str = "If true, ai suggests tags from giphy then pick the giph with the most relevant title"
    prompt: str = "return atleast 3 giphy search terms in the returned object in an array"

class GenerateVideoConfig(BaseModel):
    enabled: bool = False
    user_description: str = "If true, includes a video in the LinkedIn post to boost engagement."
    prompt: str = "Generate a video that highlights the key points of the blog post."
    LLM: ImageLLMType = Field(default_factory=_default_image_llm)
    backup: str = ""

class GlobalCreativeConfig(BaseModel):
    generate_image: GenerateImageConfig = GenerateImageConfig()
    fetch_gif: FetchGifConfig = FetchGifConfig()
    generate_video: GenerateVideoConfig = GenerateVideoConfig()
    LLM: ImageLLMType = Field(default_factory=_default_image_llm)
    backup: str = ""


class AIConfig(BaseModel):
    default_response_instructions: str = (
        "Return EITHER a generated JSON image (Creative and ImageAsset) if a creative prompt is provided OR GifSearchTags if not—never both. "
        "Example response: { 'Text': 'Your message here.', 'Creative': '[IMG] A relevant visual description.', "
        "'ImageAsset': 'https://image.pollinations.ai/prompt/{description}?width={width}&height={height}&seed={seed}&model=flux-realistic&nologo=true', "
        "'Hashtags': ['#Relevant', '#Contextual', '#GeneralTopic'] } or { 'Text': 'Message.', 'Hashtags': ['#tag', '#tag', '#tag'], "
        "'GifSearchTags': ['term one', 'term two', 'term three'] }  Respond only with valid JSON. Do not write an introduction or summary."
    )
    custom_system_instructions: str = (
        "Return EITHER a generated JSON image (Creative and ImageAsset) if a creative prompt is provided OR GifSearchTags if not—never both."
    )
    custom_user_instructions: str = (
        "Example response: { 'Text': 'Your message here.', 'Creative': '[IMG] A relevant visual description.', "
        "'ImageAsset': 'https://image.pollinations.ai/prompt/{description}?width={width}&height={height}&seed={seed}&model=flux-realistic&nologo=true', "
        "'Hashtags': ['#Relevant', '#Contextual', '#GeneralTopic'] } or { 'Text': 'Message.', 'Hashtags': ['#tag', '#tag', '#tag'], "
        "'GifSearchTags': ['term one', 'term two', 'term three'] }"
    )
    text: dict = Field(default_factory=lambda: {"generate_text": GenerateTextConfig().dict()})
    creative: GlobalCreativeConfig = GlobalCreativeConfig()
    viral_posting: ViralPostingConfig = ViralPostingConfig()

# Instance for import
ai_config = AIConfig()
