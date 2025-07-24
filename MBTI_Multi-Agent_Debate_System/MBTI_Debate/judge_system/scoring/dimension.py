import asyncio
from typing import List, Dict
from ..core.common import SpeechScoreResult, DebaterFinalScore, DebateScoreReport
from ..agents.judge_agent import JudgeAgent
#负责将多个评委对辩手的评分结果进行汇总、加权计算和排名，最终生成辩手的综合评分报告
class ScoreAggregator:
    def __init__(self, dimensions: List[str], weights: Dict[str, float]):
        self.dimensions = dimensions
        self.weights = weights

    async def gen_overall_comment_llm(self, dimension_averages: Dict[str, float], debater_name: str, mbti_type: str, judge_agent: JudgeAgent) -> str:
        prompt = f"请根据以下各项评分为{debater_name}（MBTI类型：{mbti_type}）生成一段简洁、专业的中文综合评语：\n"
        for dim, score in dimension_averages.items():
            prompt += f"{dim}: {score:.2f}\n"
        prompt += "要求：突出优点，指出不足，整体评价自然流畅。"
        comment = await judge_agent.call_deepseek_llm(prompt)
        return comment.strip()

    async def aggregate_speech_scores_async(self, speech_score_results: List[SpeechScoreResult], judge_agent: JudgeAgent) -> Dict[str, DebaterFinalScore]:
        debater_scores = {}
        mbti_map = {}
        for speech_score in speech_score_results:
            name = speech_score.debater_name.strip().lower() if speech_score.debater_name else ""
            if name not in debater_scores:
                debater_scores[name] = {dim: [] for dim in self.dimensions}
            for ds in speech_score.dimension_scores:
                debater_scores[name][ds.dimension].append(ds.score)
            mbti_map[name] = getattr(speech_score, 'mbti_type', '未知')
        #print("聚合分组key：", list(debater_scores.keys()), flush=True)
        #测试是否分组成功，避免评分遗漏
        final_scores = {}
        tasks = []
        for name, dim_scores in debater_scores.items():
            dimension_averages = {dim: (sum(scores)/len(scores) if scores else 0) for dim, scores in dim_scores.items()}
            total_score = sum(dimension_averages[dim] * self.weights.get(dim, 1.0) for dim in self.dimensions)
            mbti_type = mbti_map.get(name, '未知')
            tasks.append(self.gen_overall_comment_llm(dimension_averages, name, mbti_type, judge_agent))
            final_scores[name] = {
                'debater_name': name,
                'mbti_type': mbti_type,
                'dimension_averages': dimension_averages,
                'total_score': total_score,  # 修正字段名
                'rank': 0,  # 排名后再赋值
            }
        comments = await asyncio.gather(*tasks)
        for i, name in enumerate(final_scores):
            final_scores[name]['overall_comment'] = comments[i]
        sorted_scores = sorted(final_scores.values(), key=lambda x: x['total_score'], reverse=True)
        for i, debater in enumerate(sorted_scores):
            debater['rank'] = i + 1
        return {d['debater_name']: DebaterFinalScore(**d) for d in sorted_scores}