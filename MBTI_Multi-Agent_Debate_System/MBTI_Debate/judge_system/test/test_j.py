from MBTI_Debate.core.debate_engine import DebateEngine
from MBTI_Debate.core.debate_manager import DebateManager
from MBTI_Debate.judge_system.core.common import DifySpeechInput
from MBTI_Debate.judge_system.config.dabate_config import DebateConfig
from MBTI_Debate.judge_system.agents.judge_agent import JudgeAgent
from MBTI_Debate.judge_system.scoring.evaluator import Evaluator
from MBTI_Debate.judge_system.scoring.dimension import ScoreAggregator
import asyncio

if __name__ == "__main__":
    topic = "选大城床还是小城房"
    mbti_config = {
        "pro1": "INTJ", "pro2": "ENTJ", "pro3": "ENFP", "pro4": "INTP",
        "opp1": "ISTJ", "opp2": "ESTJ", "opp3": "ESFP", "opp4": "INFJ"
    }
    # 1. 生成辩论历史
    manager = DebateManager(topic)
    for speaker_id, mbti in mbti_config.items():
        manager.state.set_mbti(speaker_id, mbti)
    engine = DebateEngine(manager)
    history = list(engine.run_full_debate(free_debate_rounds=1))
    print("\n=== 辩论内容 ===")
    for speech in history:
        print(f"{speech['agent_id']}（{speech['stage']}）: {speech['content']}")

    # 2. 转为评分输入
    speech_inputs = [
        DifySpeechInput(
            debater_name=sp["agent_id"],
            mbti_type=manager.state.mbti_map.get(sp["agent_id"], "未知"),
            stage=sp["stage"],
            content=sp["content"],
            speech_id=f"{sp['agent_id']}_{sp['round']}"
        ) for sp in history
    ]
    # 3. 构造评分配置
    config = DebateConfig(
        motion=topic,
        pro_debaters=[k for k in mbti_config if k.startswith("pro")],
        con_debaters=[k for k in mbti_config if k.startswith("opp")],
        mbti_map=mbti_config
    )
    judge_agents = [
        JudgeAgent(f"Judge-{dim}", [dim], prompt_template=config.prompt_template) for dim in config.dimensions
    ]
    evaluator = Evaluator(judge_agents, config.dimensions, config.weights)
    async def score_all():
        speech_scores = await evaluator.evaluate_debate(speech_inputs)
        aggregator = ScoreAggregator(config.dimensions, config.weights)
        final_scores = await aggregator.aggregate_speech_scores_async(speech_scores, judge_agents[0])
        print("\n=== 评分结果 ===")
        for score in final_scores.values():
            print(f"选手: {score.debater_name} | MBTI: {score.mbti_type} | 总分: {score.total_score:.2f} | 综合评语: {score.overall_comment}")
    asyncio.run(score_all())