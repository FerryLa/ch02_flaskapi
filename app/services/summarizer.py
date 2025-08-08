# app/services/summarizer.py
from openai import OpenAI
from ..config import Config

_client = OpenAI(api_key=Config.OPENAI_API_KEY)

def summarize(text: str, prompt: str) -> str:
    resp = _client.chat.completions.create(
        model=Config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "당신은 뉴스 요약 전문가입니다."},
            {"role": "user", "content": f"{prompt}\n\n{text}"},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
