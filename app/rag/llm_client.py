import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


def get_llm_model_name() -> str:
    """返回当前配置的大模型名称。"""

    return os.getenv(
        "LLM_MODEL",
        DEFAULT_MODEL,
    )


@lru_cache(maxsize=1)
def get_llm_client() -> OpenAI:
    """创建并缓存大模型客户端。"""

    api_key = os.getenv("LLM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "未配置LLM_API_KEY，请在.env中设置"
        )

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv(
            "LLM_BASE_URL",
            DEFAULT_BASE_URL,
        ),
    )


def generate_text(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """调用大模型生成文本。"""

    response = (
        get_llm_client()
        .chat.completions.create(
            model=get_llm_model_name(),
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.2,
            max_tokens=800,
            stream=False,
            extra_body={
                "thinking": {
                    "type": "disabled",
                }
            },
        )
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("大模型未返回有效内容")

    return content.strip()


if __name__ == "__main__":
    result = generate_text(
        system_prompt="你是企业预算管理助手。",
        user_prompt="请用一句话解释什么是预算执行率。",
    )

    print(result)