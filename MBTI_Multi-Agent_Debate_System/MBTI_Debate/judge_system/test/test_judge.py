import asyncio
import os

from ..config.dabate_config import DebateConfig
from ..core.common import DifyDebateInput, DifySpeechInput, DebateStage
from ..agents.judge_agent import JudgeAgent
from ..scoring.evaluator import Evaluator
from ..config import dabate_config as config

# 构造测试数据
test_debate = DifyDebateInput(
    motion="人工智能是否会取代人类工作？",
    pro_debaters=[{"name": "张三", "mbti_type": "INTJ"}],
    con_debaters=[{"name": "李四", "mbti_type": "ENFP"}],
    speeches=[
        DifySpeechInput(debater_name="张三", mbti_type="INTJ", stage=DebateStage.OPENING, content="我认为人工智能会取代大量重复性工作，但也会创造新岗位。", speech_id="1"),
        DifySpeechInput(debater_name="李四", mbti_type="ENFP", stage=DebateStage.OPENING, content="我认为人工智能无法完全取代人类，因为创造力和情感是AI无法替代的。", speech_id="2"),
        DifySpeechInput(debater_name="张三", mbti_type="INTJ", stage=DebateStage.CROSS_EXAM, content="请问你认为AI在哪些领域无法替代人类？", speech_id="3"),
        DifySpeechInput(debater_name="李四", mbti_type="ENFP", stage=DebateStage.CROSS_EXAM, content="你如何看待AI对就业结构的影响？", speech_id="4"),
        DifySpeechInput(debater_name="张三", mbti_type="INTJ", stage=DebateStage.FREE_DEBATE, content="AI在医疗、金融等领域已经展现出超越人类的能力。", speech_id="5"),
        DifySpeechInput(debater_name="李四", mbti_type="ENFP", stage=DebateStage.FREE_DEBATE, content="但AI缺乏同理心，无法真正理解患者的需求。", speech_id="6"),
        DifySpeechInput(debater_name="张三", mbti_type="INTJ", stage=DebateStage.FREE_DEBATE, content="AI可以通过大数据分析帮助医生做出更准确的判断。", speech_id="7"),
        DifySpeechInput(debater_name="李四", mbti_type="ENFP", stage=DebateStage.FREE_DEBATE, content="最终决策还是需要人类医生来把关。", speech_id="8"),
        DifySpeechInput(debater_name="张三", mbti_type="INTJ", stage=DebateStage.SUMMARY, content="AI是工具，关键在于如何与人类协作。", speech_id="9"),
        DifySpeechInput(debater_name="李四", mbti_type="ENFP", stage=DebateStage.SUMMARY, content="人类的创造力和情感是AI无法取代的核心。", speech_id="10"),
    ]
)
config = DebateConfig(
    motion="人工智能是否会取代人类工作？",
    pro_debaters=["张三"],
    con_debaters=["李四"],
    mbti_map={"张三": "INTJ", "李四": "ENFP"}
)
# 初始化评委和评估器
judge_agents = [
    JudgeAgent("Judge1", [config.dimensions[0]], prompt_template=config.prompt_template_1),
    JudgeAgent("Judge2", [config.dimensions[1]], prompt_template=config.prompt_template_2),
    JudgeAgent("Judge3", [config.dimensions[2]], prompt_template=config.prompt_template_3),
    JudgeAgent("Judge4", [config.dimensions[3]], prompt_template=config.prompt_template_4),
]
weights = config.weights
evaluator = Evaluator(judge_agents, config.dimensions, weights)

async def main():
    all_results = await evaluator.evaluate_debate(test_debate.speeches)
    final_scores = evaluator.score_aggregator.aggregate_speech_scores(all_results, judge_agents[0])
    for debater, score in final_scores.items():
        print(f"{debater} 总分: {score.weighted_total}，排名: {score.rank}，综合评语: {score.overall_comment}")

    #final_scores = await evaluator.score_aggregator.aggregate_speech_scores_async(all_results, judge_agents[0])
    #for debater, score in final_scores.items():
        #print(f"{debater} 总分: {score.weighted_total}，排名: {score.rank}，综合评语: {score.overall_comment}")

if __name__ == "__main__":
    asyncio.run(main())