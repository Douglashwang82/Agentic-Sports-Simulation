import re
import json
import time

from google import genai
from google.genai import types
from google.genai.errors import ClientError

class LLMClient:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _extract_json(self, raw: str) -> dict:
        if not raw:
            raise ValueError("Empty response")

        try:
            return json.loads(raw.strip())
        except json.JSONDecodeError:
            pass

        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if fence:
            return json.loads(fence.group(1))

        brace = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
        if brace:
            return json.loads(brace.group(0))

        raise ValueError(f"No JSON found in: {raw[:200]!r}")

    def call(self, system_prompt: str, user_prompt: str, retries: int = 4) -> dict:
        last_exc = None
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.9,
                        max_output_tokens=200,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                data = self._extract_json(response.text)
                
                pts = int(data.get("pts", 0))
                if pts not in (0, 2, 3):
                    pts = 0
                text = str(data.get("text", "")).strip()
                return {"text": text, "pts": pts}

            except ClientError as e:
                last_exc = e
                if e.status_code == 429 and attempt < retries - 1:
                    wait = 65 * (attempt + 1)
                    print(f"[LLMClient] 429 rate-limit — waiting {wait}s (attempt {attempt + 1})")
                    time.sleep(wait)
                else:
                    raise

            except (ValueError, json.JSONDecodeError) as e:
                last_exc = e
                print(f"[LLMClient] JSON parse error attempt {attempt}: {e!r}")
                if attempt < retries - 1:
                    time.sleep(2)

        raise RuntimeError(f"LLM call failed after {retries} attempts: {last_exc}")
