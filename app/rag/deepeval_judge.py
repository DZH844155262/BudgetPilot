import json
import os
from pathlib import Path
from typing import Any

from deepeval.models.base_model import DeepEvalBaseLLM
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(
    PROJECT_ROOT / ".env",
    override=True,
)


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_JUDGE_MODEL = "deepseek-v4-flash"


class DeepSeekEvaluationModel(DeepEvalBaseLLM):
    """供DeepEval调用的DeepSeek评测模型。"""

    def __init__(self) -> None:
        api_key = (
    os.getenv("DEEPSEEK_API_KEY")
    or os.getenv("LLM_API_KEY")
)
        if not api_key:
         raise RuntimeError(
        "未配置DEEPSEEK_API_KEY或LLM_API_KEY，"
        "请检查项目根目录下的.env文件"
    )

        self.model_name = os.getenv(
            "DEEPEVAL_MODEL",
            DEFAULT_JUDGE_MODEL,
        )

        base_url = os.getenv(
            "LLM_BASE_URL",
            DEFAULT_BASE_URL,
        )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0,
            max_retries=2,
        )

        self.async_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0,
            max_retries=2,
        )

    def load_model(self) -> OpenAI:
        """返回同步API客户端。"""

        return self.client

    def get_model_name(self) -> str:
        """返回DeepEval展示的Judge名称。"""

        return self.model_name

    @staticmethod
    def _build_prompt(
        prompt: str,
        schema: type[BaseModel] | None,
    ) -> str:
        """在结构化评测时补充JSON Schema要求。"""

        if schema is None:
            return prompt

        schema_text = json.dumps(
            schema.model_json_schema(),
            ensure_ascii=False,
            indent=2,
        )

        return f"""
{prompt}

请严格以JSON对象返回，不要使用Markdown代码块，
不要输出JSON之外的任何文字。

输出必须符合以下JSON Schema：

{schema_text}
""".strip()

    @staticmethod
    def _parse_schema_output(
        content: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """将Judge返回的JSON转换成DeepEval要求的Schema。"""

        cleaned_content = content.strip()

        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content.strip("`")

            if cleaned_content.startswith("json"):
                cleaned_content = cleaned_content[4:].strip()

        try:
            return schema.model_validate_json(
                cleaned_content
            )
        except Exception as exc:
            raise RuntimeError(
                "DeepSeek Judge未返回符合Schema的JSON："
                f"{cleaned_content[:500]}"
            ) from exc

    def generate(
        self,
        prompt: str,
        schema: type[BaseModel] | None = None,
    ) -> str | BaseModel:
        """同步生成DeepEval评测结果。"""

        final_prompt = self._build_prompt(
            prompt,
            schema,
        )

        request_arguments: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是严谨的LLM评测器。"
                        "必须按照给定标准客观评分。"
                    ),
                },
                {
                    "role": "user",
                    "content": final_prompt,
                },
            ],
            "temperature": 0,
            "max_tokens": 2000,
            "stream": False,
            "extra_body": {
                "thinking": {
                    "type": "disabled",
                }
            },
        }

        if schema is not None:
            request_arguments["response_format"] = {
                "type": "json_object"
            }

        response = (
            self.client
            .chat.completions
            .create(**request_arguments)
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "DeepSeek Judge未返回有效内容"
            )

        if schema is not None:
            return self._parse_schema_output(
                content,
                schema,
            )

        return content.strip()

    async def a_generate(
        self,
        prompt: str,
        schema: type[BaseModel] | None = None,
    ) -> str | BaseModel:
        """异步生成DeepEval评测结果。"""

        final_prompt = self._build_prompt(
            prompt,
            schema,
        )

        request_arguments: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是严谨的LLM评测器。"
                        "必须按照给定标准客观评分。"
                    ),
                },
                {
                    "role": "user",
                    "content": final_prompt,
                },
            ],
            "temperature": 0,
            "max_tokens": 2000,
            "stream": False,
            "extra_body": {
                "thinking": {
                    "type": "disabled",
                }
            },
        }

        if schema is not None:
            request_arguments["response_format"] = {
                "type": "json_object"
            }

        response = (
            await self.async_client
            .chat.completions
            .create(**request_arguments)
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "DeepSeek Judge未返回有效内容"
            )

        if schema is not None:
            return self._parse_schema_output(
                content,
                schema,
            )

        return content.strip()


def test_judge_connection() -> None:
    """测试DeepEval Judge连接及Schema输出。"""

    class JudgeTestOutput(BaseModel):
        passed: bool
        reason: str

    judge = DeepSeekEvaluationModel()

    result = judge.generate(
        prompt=(
            "请判断数字20000是否大于10000，"
            "并返回JSON结果。"
        ),
        schema=JudgeTestOutput,
    )

    print(f"Judge模型：{judge.get_model_name()}")
    print(f"结构化输出：{result}")


if __name__ == "__main__":
    test_judge_connection()