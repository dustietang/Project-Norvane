import json
import os
import time
from typing import Any

from openai import APIError, OpenAI, RateLimitError

from config import (
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
)

_client = None

DECISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "action": {
            "type": "integer",
            "enum": [0, 1, 2, 3, 4, 5],
        },
        "stance": {
            "type": "string",
            "enum": ["support", "oppose", "neutral"],
        },
        "content": {
            "type": "string",
        },
        "reasoning": {
            "type": "string",
        },
    },
    "required": ["action", "stance", "content", "reasoning"],
    "additionalProperties": False,
}


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set it with: export OPENAI_API_KEY='your-key-here'"
            )
        _client = OpenAI(api_key=api_key)
    return _client


def gen_completion(
    messages: list[dict],
    model: str = LLM_MODEL,
    temperature: float = LLM_TEMPERATURE,
    max_tokens: int = LLM_MAX_TOKENS,
    json_mode: bool = False,
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> str:
    client = _get_client()

    for attempt in range(max_retries + 1):
        try:
            request_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_completion_tokens": max_tokens,
            }

            if json_mode:
                request_kwargs["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "agent_decision",
                        "strict": True,
                        "schema": DECISION_SCHEMA,
                    },
                }

            response = client.chat.completions.create(**request_kwargs)
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Model returned empty content.")
            return content

        except RateLimitError:
            if attempt < max_retries:
                wait = retry_delay * (2**attempt)
                print(f"  Rate limited. Waiting {wait:.0f}s before retry {attempt + 1}...")
                time.sleep(wait)
            else:
                raise

        except (APIError, ValueError) as e:
            if attempt < max_retries:
                wait = retry_delay * (2**attempt)
                print(f"  API/value error: {e}. Retrying in {wait:.0f}s...")
                time.sleep(wait)
            else:
                raise


def parse_json_response(response: str) -> dict | None:
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass

    start = response.find("{")
    end = response.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

    return None


def repair_decision_json(
    raw_response: str,
    model: str = LLM_MODEL,
    max_tokens: int = LLM_MAX_TOKENS,
    max_retries: int = 2,
) -> str:
    repair_messages = [
        {
            "role": "system",
            "content": (
                "Convert the user's malformed output into a valid JSON object. "
                "Return only JSON that matches the required schema exactly."
            ),
        },
        {
            "role": "user",
            "content": raw_response,
        },
    ]

    return gen_completion(
        messages=repair_messages,
        model=model,
        temperature=0,
        max_tokens=max_tokens,
        json_mode=True,
        max_retries=max_retries,
    )
