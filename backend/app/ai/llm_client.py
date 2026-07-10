import json
import logging
import mimetypes
from pathlib import Path
import re
import time
from typing import Any
import base64

from anthropic import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    Anthropic,
    InternalServerError,
    RateLimitError,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMProviderError(RuntimeError):
    pass


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def enabled(self) -> bool:
        return self.anthropic_enabled() or self.gemini_enabled() or self.openrouter_enabled()

    def anthropic_enabled(self) -> bool:
        return bool(self.settings.anthropic_api_key)

    def gemini_enabled(self) -> bool:
        api_key = getattr(self.settings, "gemini_api_key", None) or ""
        return bool(api_key)

    def openrouter_enabled(self) -> bool:
        api_key = getattr(self.settings, "openrouter_api_key", None) or ""
        return bool(api_key)

    def _parse_json_text(self, text: str, provider: str) -> Any:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE).strip()
            text = re.sub(r"```$", "", text.strip()).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            logger.exception("%s returned malformed JSON: %s", provider, text[:500])
            raise ValueError("LLM returned malformed JSON")

    def _parse_json_response(self, response: Any) -> Any:
        text = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )
        return self._parse_json_text(text, "Anthropic")

    def _parse_gemini_response(self, response: Any) -> Any:
        text = getattr(response, "text", "") or ""
        if not text and getattr(response, "candidates", None):
            parts = response.candidates[0].content.parts
            text = "".join(getattr(part, "text", "") for part in parts)
        return self._parse_json_text(text, "Gemini")

    def _parse_openrouter_response(self, response: Any) -> Any:
        message = response.choices[0].message
        text = getattr(message, "content", "") or ""
        if isinstance(text, list):
            text = "".join(part.get("text", "") for part in text if isinstance(part, dict))
        return self._parse_json_text(str(text), "OpenRouter")

    def _openrouter_client(self) -> Any:
        if not self.openrouter_enabled():
            raise RuntimeError("OpenRouter API key is not configured")

        import httpx
        from openai import OpenAI

        return OpenAI(
            api_key=self.settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30,
            max_retries=0,
            http_client=httpx.Client(trust_env=False, timeout=30),
            default_headers={
                "HTTP-Referer": "http://127.0.0.1:3000",
                "X-OpenRouter-Title": "Reachlytics",
            },
        )

    def _create_openrouter_completion(self, content: str | list[dict[str, Any]]) -> Any:
        try:
            client = self._openrouter_client()
            return client.chat.completions.create(
                model=getattr(self.settings, "openrouter_model", "openrouter/free"),
                temperature=0.4,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            )
        except Exception as exc:
            logger.exception("OpenRouter request failed")
            raise LLMProviderError(
                "OpenRouter request failed; check API key, model access, quota, and network connectivity."
            ) from exc

    def complete_json_openrouter(self, prompt: str) -> Any:
        response = self._create_openrouter_completion(
            f"{prompt}\n\nReturn valid JSON only. No markdown fences, no prose."
        )
        return self._parse_openrouter_response(response)

    def complete_json_with_images_openrouter(self, prompt: str, image_paths: list[str]) -> Any:
        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": f"{prompt}\n\nReturn valid JSON only. No markdown fences, no prose.",
            }
        ]
        for image_path in image_paths:
            path = Path(image_path)
            mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                }
            )

        response = self._create_openrouter_completion(content)
        return self._parse_openrouter_response(response)

    def _create_message(self, content: str | list[dict[str, Any]]) -> Any:
        if not self.anthropic_enabled():
            raise RuntimeError("Anthropic API key is not configured")

        client = Anthropic(api_key=self.settings.anthropic_api_key)
        response = None
        for attempt in range(3):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    temperature=0.4,
                    messages=[
                        {
                            "role": "user",
                            "content": content,
                        }
                    ],
                )
                break
            except (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError):
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)
            except APIStatusError as exc:
                if exc.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                raise

        if response is None:
            raise RuntimeError("LLM request failed")
        return response

    def complete_json(self, prompt: str) -> Any:
        response = self._create_message(
            f"{prompt}\n\nReturn valid JSON only. No markdown fences, no prose."
        )
        return self._parse_json_response(response)

    def complete_json_with_images(self, prompt: str, image_paths: list[str]) -> Any:
        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": f"{prompt}\n\nReturn valid JSON only. No markdown fences, no prose.",
            }
        ]
        for image_path in image_paths:
            path = Path(image_path)
            image_bytes = path.read_bytes()
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64.b64encode(image_bytes).decode("ascii"),
                    },
                }
            )

        response = self._create_message(content)
        return self._parse_json_response(response)

    def _gemini_client(self) -> Any:
        if not self.gemini_enabled():
            raise RuntimeError("Gemini API key is not configured")
        from google import genai
        from google.genai import types

        return genai.Client(
            api_key=self.settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=20000, client_args={"trust_env": False}),
        )

    def _generate_gemini(self, parts: list[Any]) -> Any:
        from google.genai import types

        try:
            client = self._gemini_client()
            return client.models.generate_content(
                model=getattr(self.settings, "gemini_model", "gemini-2.5-flash-lite"),
                contents=parts,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            logger.exception("Gemini request failed")
            raise LLMProviderError(
                "Gemini request failed; check API key, quota, model access, and network connectivity."
            ) from exc

    def complete_json_gemini(self, prompt: str) -> Any:
        response = self._generate_gemini(
            [f"{prompt}\n\nReturn valid JSON only. No markdown fences, no prose."]
        )
        return self._parse_gemini_response(response)

    def complete_json_with_images_gemini(self, prompt: str, image_paths: list[str]) -> Any:
        from google.genai import types

        parts: list[Any] = [f"{prompt}\n\nReturn valid JSON only. No markdown fences, no prose."]
        for image_path in image_paths:
            path = Path(image_path)
            mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            parts.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type))
        response = self._generate_gemini(parts)
        return self._parse_gemini_response(response)

    def transcribe_audio_gemini(self, video_path: str) -> str:
        if not self.gemini_enabled():
            raise RuntimeError("Gemini API key is not configured")

        try:
            uploaded_file = self._gemini_client().files.upload(file=video_path)
        except Exception:
            raise LLMProviderError(
                "Gemini video upload failed; check API key, file support, quota, and network connectivity."
            ) from None
        response = self._generate_gemini(
            [
                uploaded_file,
                (
                    "Transcribe the spoken audio in this video. If there is no speech, summarize the "
                    "visible/audio context cautiously. Return strict JSON only as "
                    '{"text": string, "language": string}.'
                ),
            ]
        )
        payload = self._parse_gemini_response(response)
        if not isinstance(payload, dict):
            raise ValueError("Gemini transcription response must be a JSON object")
        return str(payload.get("text") or "")
