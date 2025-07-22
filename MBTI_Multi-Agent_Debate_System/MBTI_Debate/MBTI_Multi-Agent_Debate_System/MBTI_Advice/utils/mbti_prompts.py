from ..config.settings import get_prompt_template

def get_prompt_for_mbti(mbti_type: str, user_query: str) -> str:
    """获取特定MBTI类型的提示词"""
    template = get_prompt_template(mbti_type)
    return template.format(user_query=user_query)