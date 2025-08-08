class PromptManager:
    PROMPTS = {
        "AIBOT": "기사의 핵심 내용만 3줄로 간결하게 요약해줘",
        "NEWSLETTER": "카카오톡 뉴스레터용으로 핵심만 1줄로 요약해줘"
    }
    @classmethod
    def get(cls, prompt=None, type_=None) -> str:
        if prompt: return prompt
        if type_ and type_.upper() in cls.PROMPTS:
            return cls.PROMPTS[type_.upper()]
        return cls.PROMPTS["AIBOT"]
