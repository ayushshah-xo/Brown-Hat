"""
brain/web_search.py — Web Search for News and General Questions
"""
import logging
import re
from typing import Optional

logger = logging.getLogger("Robot.WebSearch")

NEWS_KEYWORDS = [
    "news", "खबर", "समाचार", "khabar", "samachar",
    "top 5", "top 10", "latest", "recent", "today",
    "viral", "trending", "अहिले", "आज", "headline",
]

SEARCH_KEYWORDS = [
    "who is", "what is", "where is", "when did",
    "football", "cricket", "sport", "weather",
    "greatest", "best player", "score", "tell me about",
]

def needs_search(query: str) -> bool:
    q = query.lower()
    return any(w in q for w in NEWS_KEYWORDS + SEARCH_KEYWORDS)

def search(query: str, language: str = "en") -> Optional[str]:
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.error("Search package not installed")
            return None

    is_news = any(w in query.lower() for w in NEWS_KEYWORDS)

    try:
        ddgs = DDGS()

        if is_news:
            results = []
            try:
                results = list(ddgs.news(
                    "Nepal news",
                    max_results=10,
                    region="in-en",
                ))
                logger.info(f"DDG news: {len(results)} results")
            except Exception as e:
                logger.warning(f"DDG news failed: {e}")

            if len(results) < 3:
                try:
                    results = list(ddgs.text(
                        "Nepal news today 2026",
                        max_results=10,
                        region="in-en",
                    ))
                    logger.info(f"Text fallback: {len(results)} results")
                except Exception as e:
                    logger.warning(f"Text fallback: {e}")

            if not results:
                return None

            # Build news — NO filtering, just take raw titles
            lines = []
            seen = set()
            for r in results:
                raw = r.get("title", "").strip()
                if not raw or raw in seen:
                    continue
                # Skip generic useless titles
                if raw.lower() in ["nepal news", "news", "india nepal ties news"]:
                    continue
                # Trim long titles to 15 words
                words = raw.split()
                title = " ".join(words[:15]) if len(words) > 15 else raw
                seen.add(raw)
                lines.append(title)
                if len(lines) >= 5:
                    break

            logger.info(f"Final lines: {lines}")

            if not lines:
                return None

            numbered = ". ".join(
                f"Number {i}, {t}" for i, t in enumerate(lines, 1)
            )
            return f"Here are today's top news from Nepal. {numbered}"

        else:
            # General knowledge
            results = list(ddgs.text(
                query,
                max_results=3,
                region="wt-wt",
            ))
            if not results:
                return None
            body = results[0].get("body", "").strip()
            if body:
                sentences = re.split(r'(?<=[.!?])\s+', body)
                clean = " ".join(sentences[:2])
                words = clean.split()
                if len(words) > 25:
                    clean = " ".join(words[:25]) + "."
                return clean
            return results[0].get("title", "").strip()

    except Exception as e:
        logger.error(f"Web search error: {e}")
        return None