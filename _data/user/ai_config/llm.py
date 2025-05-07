# LLM configuration data as Pydantic model
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class OpenAICompatibleConfig(BaseModel):
    endpoint: str
    model: str
    prompt: str
    suffix: Optional[str] = None
    best_of: int
    echo: bool
    frequency_penalty: float
    presence_penalty: float
    logit_bias: Dict[str, Any]
    logprobs: Optional[int] = None
    max_tokens: int
    n: int
    seed: int
    stop: Optional[str] = None
    stream: bool
    stream_options: Optional[Any] = None
    temperature: float
    top_p: float

class PollinationsConfig(BaseModel):
    default_model: str
    seed: int
    temperature: float
    jsonMode: bool
    private: bool
    openai_compatible: OpenAICompatibleConfig

class DeepSeekConfig(BaseModel):
    text_model: str
    presence_penalty: float
    frequency_penalty: float
    response_format: str
    temperature: float
    max_tokens: int
    tools: str
    tool_choice: str
    top_p: float
    logprobs: bool
    top_logprobs: int
    available_models: list[str]

class AnthropicConfig(BaseModel):
    text_model: str
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop_sequences: list[str]
    system: str
    available_models: list[str]
    message_format: list[dict]

class HuggingFaceConfig(BaseModel):
    text_model: str
    image_model: str
    video_model: str
    temperature: float
    max_tokens: int
    available_models: list[str]
    available_tools: list[str]

class CustomConfig(BaseModel):
    enabled: bool
    text_model: str
    temperature: float
    max_tokens: int
    url: str
    headers: dict[str, str]

class LLMConfig(BaseModel):
    Pollinations: PollinationsConfig
    DeepSeek: DeepSeekConfig
    Anthropic: AnthropicConfig
    HuggingFace: HuggingFaceConfig
    Custom: CustomConfig

llm_config = LLMConfig(
    Pollinations=PollinationsConfig(
        default_model="openai",
        seed=42,
        temperature=0.7,
        jsonMode=True,
        private=True,
        openai_compatible=OpenAICompatibleConfig(
            endpoint="/v1/chat/completions",
            model="text-davinci-003",
            prompt="Your custom prompt",
            suffix=None,
            best_of=1,
            echo=False,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            logit_bias={},
            logprobs=None,
            max_tokens=256,
            n=1,
            seed=42,
            stop=None,
            stream=False,
            stream_options=None,
            temperature=0.7,
            top_p=1.0
        )
    ),
    DeepSeek=DeepSeekConfig(
        text_model="deepseek-chat",
        presence_penalty=0.0,
        frequency_penalty=0.0,
        response_format="json_object",
        temperature=0.7,
        max_tokens=500,
        tools="function",
        tool_choice="auto",
        top_p=0.95,
        logprobs=False,
        top_logprobs=5,
        available_models=[
            "deepseek-chat",
            "deepseek-reasoner"
        ]
    ),
    Anthropic=AnthropicConfig(
        text_model="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=500,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop_sequences=[],
        system=(
            "You're a professional copywriter helping turn blog posts into viral\n"
            "LinkedIn content."
        ),
        available_models=[
            "claude-3-7-sonnet-20250219",
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        message_format=[
            {"role": "user", "content": "Hello, world"}
        ]
    ),
    HuggingFace=HuggingFaceConfig(
        text_model="mistralai/Mistral-7B-Instruct-v0.1",
        image_model="runwayml/stable-diffusion-v1-5",
        video_model="runwayml/stable-diffusion-v1-5",
        temperature=0.7,
        max_tokens=500,
        available_models=[
            "meta-llama/Meta-Llama-3-8B",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "tiiuae/falcon-7b-instruct"
        ],
        available_tools=[
            "Audio Classification",
            "Automatic Speech Recognition",
            "Chat Completion",
            "Feature Extraction",
            "Fill Mask",
            "Image Classification",
            "Image Segmentation",
            "Image to Image",
            "Image-Text to Text",
            "Object Detection",
            "Question Answering",
            "Summarization",
            "Table Question Answering",
            "Text Classification",
            "Text Generation",
            "Text to Image",
            "Token Classification",
            "Translation",
            "Zero Shot Classification"
        ]
    ),
    Custom=CustomConfig(
        enabled=False,
        text_model="your-custom-text_model",
        temperature=0.7,
        max_tokens=500,
        url="https://your-custom-api.com/v1/completions",
        headers={
            "Authorization": "Bearer your_api_key",
            "Content-Type": "application/json"
        }
    )
)
