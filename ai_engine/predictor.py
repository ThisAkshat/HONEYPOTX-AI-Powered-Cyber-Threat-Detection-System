# predictor.py — Hybrid: Rule-based + Gemini for edge cases. 

import re
import google.generativeai as genai
from ai_engine.preprocess import preprocess

GEMINI_API_KEY = "Your Gemini API Key"
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")

RISK_MAP = {
    "sql":        95,
    "cmdinject":  98,
    "xss":        80,
    "bruteforce": 75,
    "traversal":  85,
    "normal":     5,
}

# ── SIGNATURES — clear attack patterns ──
RULES = {
    "xss": [
        r"<script", r"</script>", r"javascript:", r"onerror\s*=",
        r"onload\s*=", r"onmouseover\s*=", r"onfocus\s*=", r"<svg",
        r"<img[^>]+onerror", r"document\.cookie", r"alert\s*\(",
        r"eval\s*\(", r"innerHTML", r"<iframe",
    ],
    "sql": [
        r"'\s*(or|and)\s*'?\d", r"'\s*(or|and)\s+\d+=\d+",
        r"union\s+select", r"drop\s+table", r"drop\s+database",
        r"insert\s+into", r";\s*select", r"--\s*$", r"1=1",
        r"sleep\s*\(\d", r"benchmark\s*\(", r"waitfor\s+delay",
        r"information_schema", r"into\s+outfile", r"load_file\s*\(",
    ],
    "cmdinject": [
        r";\s*(ls|cat|whoami|id|uname|wget|curl|nc|bash|sh|python)",
        r"\|\s*(ls|cat|whoami|id|uname|bash|sh|nc)",
        r"&&\s*(ls|cat|whoami|id|uname|bash|wget)",
        r"/etc/passwd", r"/etc/shadow", r"\/bin\/(sh|bash)",
        r">\&\s*/dev/tcp", r"base64\s+-d",
    ],
    "traversal": [
        r"\.\./", r"\.\.\\", r"%2e%2e%2f", r"%252e%252e",
        r"\.\.%2f", r"\.\.%5c", r"/%2e%2e", r"\.{4,}//",
    ],
    "bruteforce": [
        r"hydra\s+-", r"medusa\s+-", r"rockyou\.txt",
        r"wordlist\.txt", r"failed\s+login\s+attempt",
        r"too\s+many\s+login", r"brute\s*force",
        r"password\s+spray", r"-P\s+\S+\.txt",
    ],
}

def rule_check(text):
    t = text.lower()
    for attack_type, patterns in RULES.items():
        for pattern in patterns:
            if re.search(pattern, t):
                return attack_type
    return None

GEMINI_PROMPT = """You are a cybersecurity expert. Is this input a cyberattack payload or normal text?

Input: {text}

Reply with ONLY one word from: sql, xss, cmdinject, traversal, bruteforce, normal
No explanation."""

def gemini_check(text):
    try:
        response = gemini.generate_content(GEMINI_PROMPT.format(text=text))
        pred = response.text.strip().lower().split()[0]
        return pred if pred in RISK_MAP else "normal"
    except Exception:
        return "normal"

def predict(text):
    text = preprocess(text)

    # Step 1: Rule-based (fast, accurate for clear attacks)
    rule_result = rule_check(text)
    if rule_result:
        return rule_result, RISK_MAP[rule_result]

    # Step 2: Gemini (for ambiguous/edge cases only)
    pred = gemini_check(text)
    return pred, RISK_MAP.get(pred, 5)