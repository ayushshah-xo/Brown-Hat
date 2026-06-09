"""
================================================================
  brain/llm.py — Language Model Interface
  Supports Groq (fastest), OpenAI, or offline Mistral GGUF.
  Set AI_MODE in config.py to switch.
================================================================
"""

import logging
import time
from typing import Optional
from config import (AI_MODE, GROQ_API_KEY, OPENAI_API_KEY,
                    LLM_MODEL_GROQ, LLM_MODEL_OAI, LLM_TIMEOUT,
                    LLM_OFFLINE_PATH, LLM_N_THREADS, LLM_MAX_TOKENS,
                    SCHOOL)

logger = logging.getLogger("Robot.LLM")

# ── System prompt ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are Sukuna, the AI assistant robot at Sukuna Secondary School in Nepal.

STRICT LANGUAGE RULE — THIS IS MOST IMPORTANT:
- If user speaks English → respond ONLY in English
- If user speaks Nepali → respond ONLY in Nepali
- If user speaks Hindi → respond ONLY in Hindi
- NEVER mix languages in one response
- NEVER respond in Nepali if the user asked in English

ABOUT YOU:
- Your name is Sukuna
- You were built by Ayush Shah, age 16, Class 11 student at Sukuna Secondary School
- His team members are Yuganshu Rizal and Suprim Ojha
- Head teacher: Hikmat Bahadur Basnet
- School: Sukuna Secondary School, Nepal

RESPONSE RULES:
- Keep answers SHORT — maximum 2 sentences for voice
- Be friendly and helpful
- For school questions, give direct answers
- Do NOT start responses with long introductions
- Do NOT repeat yourself
""".strip()


class LLMBrain:
    """
    Unified LLM interface.
    Tries the configured engine; falls back gracefully if unavailable.
    """

    def __init__(self):
        self._mode = AI_MODE
        self._client = None
        self._offline_model = None
        self._initialize()

    def _initialize(self):
        if self._mode == "groq":
            self._init_groq()
        elif self._mode == "openai":
            self._init_openai()
        elif self._mode == "offline":
            self._init_offline()
        else:
            logger.warning(f"Unknown AI_MODE '{self._mode}' — defaulting to offline")
            self._mode = "offline"
            self._init_offline()

    # ── Groq ──────────────────────────────────────────────────────────────
    def _init_groq(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — falling back to offline")
            self._mode = "offline"
            self._init_offline()
            return
        try:
            import openai
            self._client = openai.OpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
                timeout=LLM_TIMEOUT,
            )
            logger.info("Groq LLM ready (fastest cloud mode)")
        except ImportError:
            logger.error("openai package not installed — run: pip install openai")

    # ── OpenAI ────────────────────────────────────────────────────────────
    def _init_openai(self):
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set — falling back to offline")
            self._mode = "offline"
            self._init_offline()
            return
        try:
            import openai
            self._client = openai.OpenAI(
                api_key=OPENAI_API_KEY,
                timeout=LLM_TIMEOUT,
            )
            logger.info("OpenAI GPT ready")
        except ImportError:
            logger.error("openai package not installed — run: pip install openai")

    # ── Offline ───────────────────────────────────────────────────────────
    def _init_offline(self):
        try:
            from llama_cpp import Llama
            self._offline_model = Llama(
                model_path=LLM_OFFLINE_PATH,
                n_ctx=1024,
                n_threads=LLM_N_THREADS,
                verbose=False,
            )
            logger.info("Offline Mistral GGUF loaded")
        except ImportError:
            logger.error("llama-cpp-python not installed — run: pip install llama-cpp-python")
        except Exception as e:
            logger.error(f"Offline LLM failed to load: {e}")

    # ── Public query interface ─────────────────────────────────────────────
    def query(self, user_input: str, language: str = "ne") -> Optional[str]:
        """
        Ask the LLM a question. Returns a response string, or None.
        """
        lang_hint = {
            "ne": "कृपया नेपालीमा जवाफ दिनुस्।",
            "hi": "कृपया हिंदी में जवाब दें।",
            "en": "Please respond in English.",
        }.get(language, "")

        prompt = f"{user_input}\n\n{lang_hint}"

        t0 = time.time()
        try:
            if self._mode in ("groq", "openai") and self._client:
                answer = self._query_openai_compatible(prompt)
            elif self._mode == "offline" and self._offline_model:
                answer = self._query_offline(prompt)
            else:
                return None
        except Exception as e:
            logger.error(f"LLM query error: {e}")
            return None

        elapsed = time.time() - t0
        logger.info(f"LLM [{self._mode}] responded in {elapsed:.2f}s")
        return answer

    def _query_openai_compatible(self, prompt: str) -> Optional[str]:
        model = LLM_MODEL_GROQ if self._mode == "groq" else LLM_MODEL_OAI
        resp  = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    def _query_offline(self, prompt: str) -> Optional[str]:
        full_prompt = (
            f"[INST] <<SYS>>\n{SYSTEM_PROMPT}\n<</SYS>>\n\n{prompt} [/INST]"
        )
        result = self._offline_model(full_prompt, max_tokens=LLM_MAX_TOKENS)
        return result["choices"][0]["text"].strip()

    def is_ready(self) -> bool:
        return bool(self._client or self._offline_model)
