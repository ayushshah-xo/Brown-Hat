"""
================================================================
  brain/school_brain.py — School Knowledge + Teacher Lookup
  Answers questions about Sukuna Secondary School.
  Uses teachers.json (all 146 staff from your PDF).
================================================================
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional
from config import TEACHERS_JSON, SCHOOL, QA_MIN_SCORE

# Nepali/Hindi spelling variants for common words
_SYNONYMS = {
    "school":    ["school", "विद्यालय", "skul", "sukuna", "सुकुना", "सुकून",
                  "sukunā", "secondary", "माध्यमिक"],
    "location":  ["location", "ठिकाना", "ठेगाना", "kahan", "कहाँ", "कहां",
                  "where", "located", "address", "स्थान", "ठाउँ"],
    "motto":     ["motto", "मोटो", "मोटू", "नारा", "slogan", "empowering",
                  "उद्देश्य", "adarsh", "आदर्श"],
    "email":     ["email", "gmail", "इमेल", "ईमेल", "mail", "contact"],
    "phone":     ["phone", "number", "नम्बर", "नंबर", "फोन", "contact",
                  "mobile", "call"],
    "hours":     ["time", "hour", "समय", "खुल्ने", "open", "working",
                  "बन्द", "close"],
    "head":      ["head", "principal", "प्रधान", "mukhya", "headmaster",
                  "प्रधानाध्यापक", "director"],
    "established": ["established", "founded", "स्थापना", "स्थापित",
                    "started", "शुरु", "सुरु", "kab", "when"],
    "teachers":  ["teacher", "staff", "kati", "कति", "how many",
                  "total", "जम्मा", "सबै"],
}

def _matches(query: str, *keys: str) -> bool:
    """Check if query contains any synonym for any of the given keys."""
    q = query.lower()
    for key in keys:
        for word in _SYNONYMS.get(key, [key]):
            if word in q:
                return True
    return False

logger = logging.getLogger("Robot.SchoolBrain")


class SchoolBrain:
    """
    Fast offline Q&A for school-specific questions.
    Two capabilities:
      1. Teacher lookup: name → phone number (fuzzy match)
      2. School info: address, hours, head teacher, etc.
    """

    def __init__(self):
        self._data = self._load_json()
        self._staff = self._data.get("staff", [])
        self._school = self._data.get("school", SCHOOL)
        logger.info(f"School brain loaded — {len(self._staff)} staff members")

    def _load_json(self) -> dict:
        try:
            with open(TEACHERS_JSON, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load teachers.json: {e}")
            return {"staff": [], "school": {}}

    # ── Public interface ──────────────────────────────────────────────────
    def answer(self, question: str, language: str = "ne") -> Optional[str]:
        q = question.lower().strip()
        # Reject clearly non-school questions immediately
        NON_SCHOOL = [
            "football", "cricket", "goat", "greatest", "sport",
            "news", "movie", "song", "actor", "player", "team",
            "weather", "temperature", "recipe", "cook",
            "capital", "president", "country", "world",
            "who is the best", "top 5", "top 10",
        ]
        if any(w in q for w in NON_SCHOOL):
            return None

        # 1. Designation/role lookup — "who is HOD of science", "who is accountant"
        role_answer = self._find_by_role(q, language)
        if role_answer:
            return role_answer

        # 2. Teacher phone number lookup
        teacher, score = self._find_teacher(q)
        if teacher and score >= QA_MIN_SCORE:
            return self._teacher_response(teacher, language)

        # 3. School info questions
        info = self._school_info(q, language)
        if info:
            return info

        return None  # let the LLM handle it

    # ── Teacher lookup ────────────────────────────────────────────────────
    def _find_teacher(self, query: str) -> tuple:
        """
        Fuzzy-match a teacher name from the query.
        Returns (teacher_dict, score) or (None, 0).
        """
        best      = None
        best_score = 0

        for person in self._staff:
            name_lower = person["name"].lower()
            score = self._name_score(query, name_lower)
            if score > best_score:
                best_score = score
                best = person

        return best, best_score
    
    def _find_by_role(self, query: str, language: str) -> Optional[str]:
        """Match queries like 'who is HOD,OOD,SOD,H O D of science', 'who is accountant'"""
        q = query.lower()

        # Specific department HOD checks — longest match first
        if "hod" in q or "head of department" in q:
            if any(w in q for w in ["science", "विज्ञान"]):
                designation = "HOD Science"
            elif any(w in q for w in ["management", "व्यवस्थापन"]):
                designation = "HOD Management"
            elif any(w in q for w in ["civil", "engineering", "इन्जिनियर"]):
                designation = "HOD Civil Engineering"
            elif any(w in q for w in ["law", "education", "कानून"]):
                designation = "HOD Law and Education"
            else:
                designation = "HOD"   # generic — list all HODs
        elif any(w in q for w in ["accountant", "account officer", "लेखा"]):
            designation = "Account"
        elif any(w in q for w in ["it officer", "it teacher", "computer officer"]):
            designation = "IT Officer"
        elif any(w in q for w in ["lab assistant", "laboratory"]):
            designation = "Lab Assistant"
        elif any(w in q for w in ["assistant head", "asst head"]):
            designation = "Asst Head Teacher"
        elif any(w in q for w in ["exam section", "exam officer"]):
            designation = "Exam Section"
        else:
            return None

        # Find matching staff
        results = [
            p for p in self._staff
            if designation.lower() in p["designation"].lower()
        ]

        if not results:
            return None

        if len(results) == 1:
            p = results[0]
            r = {
                "ne": f"{p['name']} जी {p['designation']} हुनुहुन्छ। उहाँको नम्बर {self._say_number(p['mobile'], 'ne')} हो।",
                "hi": f"{p['name']} जी {p['designation']} हैं। उनका नंबर {self._say_number(p['mobile'], 'hi')} है।",
                "en": f"{p['name']} is the {p['designation']}. Contact: {self._say_number(p['mobile'], 'en')}.",
            }
            return r.get(language, r["ne"])

        # Multiple — list all
        names = ", ".join(f"{p['name']} ({p['designation']})" for p in results)
        r = {
            "ne": f"विभागका प्रमुखहरू: {names}।",
            "hi": f"विभागाध्यक्ष: {names}।",
            "en": f"Heads of Department: {names}.",
        }
        return r.get(language, r["ne"])

    def _name_score(self, query: str, name: str) -> int:
        """
        Score name match in query. Handles both English and Nepali spellings.
        e.g. 'मोनी' matches 'mani', 'लिंबू' matches 'limbu'
        """
        # Transliteration map — Nepali → English approximations
        _NE_EN = {
            "मोनी": "mani",   "मनी": "mani",    "मणि": "mani",
            "राज":  "raj",    "लिंबू": "limbu",  "लिम्बू": "limbu",
            "अनिल": "anil",   "थापा": "thapa",   "कुमार": "kumar",
            "प्रसाद": "prasad", "शर्मा": "sharma", "पौडेल": "poudel",
            "भट्टराई": "bhattarai", "खड्का": "khadka", "श्रेष्ठ": "shrestha",
            "गुरुङ": "gurung", "तामाङ": "tamang", "राउत": "raut",
            "दाहाल": "dahal",  "गिरी": "giri",    "नेपाल": "nepal",
            "सुवेदी": "subedi", "पन्त": "panta",   "रिजाल": "rijal",
            "बस्नेत": "basnet", "कार्की": "karki",  "जोशी": "joshi",
            "ओझा": "ojha",     "घिमिरे": "ghimire", "लुइटेल": "luitel",
            "खतिवडा": "khatiwada", "अधिकारी": "adhikari",
        }
        # Translate Nepali words in query to English
        translated = query
        for ne, en in _NE_EN.items():
            translated = translated.replace(ne, en)

        parts = name.split()
        score = sum(
            1 for part in parts
            if len(part) > 2 and (part in query or part in translated)
        )
        return score

    def _teacher_response(self, teacher: dict, language: str) -> str:
        name   = teacher["name"]
        mobile = teacher["mobile"]
        role   = teacher["designation"]

        responses = {
            "ne": f"{name} जीको मोबाइल नम्बर {self._say_number(mobile, 'ne')} हो। उहाँ {role} हुनुहुन्छ।",
            "hi": f"{name} जी का मोबाइल नंबर {self._say_number(mobile, 'hi')} है। वे {role} हैं।",
            "en": f"{name}'s mobile number is {self._say_number(mobile, 'en')}. They are a {role}.",
        }
        return responses.get(language, responses["ne"])

    def _say_number(self, number: str, language: str) -> str:
        """
        Format a phone number for natural speech.
        E.g. "9842184539" → "984-218-4539" (pauses feel more natural).
        """
        n = number.replace(".0", "").strip()
        if len(n) == 10:
            return f"{n[:4]}-{n[4:7]}-{n[7:]}"
        return n

    # ── School info ───────────────────────────────────────────────────────
    def _school_info(self, query: str, language: str) -> Optional[str]:
        s = self._school

        # Motto
        if _matches(query, "motto"):
            r = {
                "ne": "सुकुना माध्यमिक विद्यालयको आदर्श वाक्य हो — Empowering Minds, Shaping Futures।",
                "hi": "सुकुना माध्यमिक विद्यालय का आदर्श वाक्य है — Empowering Minds, Shaping Futures।",
                "en": "The motto of Sukuna Secondary School is Empowering Minds, Shaping Futures.",
            }
            return r.get(language, r["ne"])

        # Location
        if _matches(query, "location"):
            r = {
                "ne": "Sukuna Secondary School, Mahendra हाईवे रोड, Koshi Haraicha मा अवस्थित छ। सम्पर्क: +977 021-545366",
                "hi": "सुकुना माध्यमिक विद्यालय नेपाल में स्थित है। संपर्क: +977 021-545366",
                "en": "Sukuna Secondary School is located in Mahendra Hwy, Koshi Haraicha. Contact: +977 021-545366",
            }
            return r.get(language, r["ne"])
        
        # Current Nepal PM — hardcoded since LLM training is outdated
        if any(w in query for w in ["prime minister", "pm ", "pradhan mantri",
                             "प्रधानमन्त्री", "प्रधान मन्त्री"]):  
            r = {

                "ne": "नेपालका हालका प्रधानमन्त्री बालेन्द्र शाह हुनुहुन्छ। उहाँ ३५ वर्षका पूर्व काठमाडौं महानगरपालिका मेयर हुनुहुन्थ्यो र २७ मार्च २०२६ मा प्रधानमन्त्री बन्नुभयो।",
                "hi": "नेपाल के वर्तमान प्रधानमंत्री बालेन्द्र शाह हैं। वे 35 वर्षीय पूर्व काठमांडू महापौर हैं और 27 मार्च 2026 को प्रधानमंत्री बने।",
                "en": "The current Prime Minister of Nepal is Balendra Shah, also known as Balen Shah. He is 35 years old, a former mayor of Kathmandu, and was sworn in on 27 March 2026.",
             }
            return r.get(language, r["ne"])   

        # Head teacher
        if _matches(query, "head"):
            ht = s.get("head_teacher", "हिक्मत बहादुर बस्नेत")
            r = {
                "ne": f"सुकुना माध्यमिक विद्यालयका प्रधानाध्यापक {ht} हुनुहुन्छ।",
                "hi": f"सुकुना माध्यमिक विद्यालय के प्रधानाध्यापक {ht} हैं।",
                "en": f"The head teacher of Sukuna Secondary School is {ht}.",
            }
            return r.get(language, r["ne"])

        # Phone
        if _matches(query, "phone") and not _matches(query, "teachers"):
            # Only answer school phone if no teacher name in query
            has_name = any(
                self._name_score(query, p["name"].lower()) >= 2
                for p in self._staff
            )
            if not has_name:
                r = {
                    "ne": f"विद्यालयको फोन नम्बर {s.get('phone', '+977 021-545366')} हो।",
                    "hi": f"विद्यालय का फोन नंबर {s.get('phone', '+977 021-545366')} है।",
                    "en": f"The school phone number is {s.get('phone', '+977 021-545366')}.",
                }
                return r.get(language, r["ne"])

        # Email
        if _matches(query, "email"):
            r = {
                "ne": f"विद्यालयको इमेल {s.get('email', 'schoolsukuna@gmail.com')} हो।",
                "hi": f"विद्यालय का ईमेल {s.get('email', 'schoolsukuna@gmail.com')} है।",
                "en": f"The school email is {s.get('email', 'schoolsukuna@gmail.com')}.",
            }
            return r.get(language, r["ne"])

        # Working hours
        if _matches(query, "hours"):
            r = {
                "ne": "विद्यालय सोमबारदेखि शुक्रबार बिहान ८ देखि बेलुकी ४ बजेसम्म र शनिबार १२ बजेसम्म खुल्छ।",
                "hi": "विद्यालय सोमवार से शुक्रवार 8 से 4 बजे और शनिवार 12 बजे तक खुला रहता है।",
                "en": "School is open Monday–Friday 8AM–4PM and Saturday until 12PM.",
            }
            return r.get(language, r["ne"])

        # Established
        if _matches(query, "established"):
            est = s.get("established", "2029 BS")
            r = {
                "ne": f"सुकुना माध्यमिक विद्यालय {est} मा स्थापना भएको हो।",
                "hi": f"सुकुना माध्यमिक विद्यालय {est} में स्थापित हुआ था।",
                "en": f"Sukuna Secondary School was established in {est}.",
            }
            return r.get(language, r["ne"])

        # Total staff
        if _matches(query, "teachers"):
            count = len(self._staff)
            r = {
                "ne": f"सुकुना माध्यमिक विद्यालयमा जम्मा {count} जना शिक्षक तथा कर्मचारी हुनुहुन्छ।",
                "hi": f"सुकुना माध्यमिक विद्यालय में कुल {count} शिक्षक और कर्मचारी हैं।",
                "en": f"Sukuna Secondary School has {count} teachers and staff members.",
            }
            return r.get(language, r["ne"])

        return None

    def get_staff_list(self) -> list:
        return self._staff

    def get_school_info(self) -> dict:
        return self._school
