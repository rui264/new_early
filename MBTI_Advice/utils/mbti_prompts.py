from config.settings import get_prompt_template

def get_prompt_for_mbti(mbti_type: str, user_query: str) -> str:
    template = get_prompt_template(mbti_type)
    return template.format(question=user_query)  # 将 user_query 赋值给 question