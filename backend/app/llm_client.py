import json
import logging

from groq import Groq

from app.config import settings

logger = logging.getLogger("llm_client")

_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Calls Groq's chat completion API and expects a strict JSON object back.
    Falls back to a deterministic heuristic result if no API key is configured,
    so the project still runs end-to-end without any paid/free key set up yet.
    """
    print("===== CALLING GROQ LLM =====")
    print("Model:", settings.GROQ_MODEL)
    if _client is None:
        return {
            "_fallback": True,
            "reasoning": "No GROQ_API_KEY configured — using rule-based fallback.",
        }

    try:
        response = _client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt + "\nRespond ONLY with valid JSON. No prose, no markdown fences."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        print("===== RESPONSE RECEIVED =====")
        print(response.choices[0].message.content)
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM call failed, falling back: %s", exc)
        return {"_fallback": True, "reasoning": f"LLM error: {exc}"}
