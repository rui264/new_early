from typing import List, Dict, Any
from ..agents.judge_agent import JudgeAgent
from ..core.common import Speech, DebateInfo, DifySpeechInput, SingleScore, SpeechScoreResult, DebateStage, FreeDebateSummaryInput
from ..scoring.dimension import ScoreAggregator
import asyncio
#负责协调多个 JudgeAgent 对辩论发言进行评分，并根据指定的维度和权重进行聚合计算
class Evaluator:
    def __init__(self, judge_agents: List[JudgeAgent], dimensions: List[str], weights: Dict[str, float]):
        self.judge_agents = judge_agents
        self.dimensions = dimensions
        self.weights = weights
        self.score_aggregator = ScoreAggregator(dimensions, weights)

    async def evaluate_single_speech(self, speech_input: DifySpeechInput) -> SpeechScoreResult:
        speech = Speech(
            debater=speech_input.debater_name,
            stage=speech_input.stage,
            content=speech_input.content
        )
        debate_info = DebateInfo("", [], [], [])
        # 并发所有judge.score_speech
        judge_tasks = [judge.score_speech(speech, debate_info) for judge in self.judge_agents]
        judge_results = await asyncio.gather(*judge_tasks)
        dimension_scores = []
        for score_dict in judge_results:
            for dim, score in score_dict.items():
                dimension_scores.append(SingleScore(dimension=dim, score=score, comment=""))
        total_score = sum(ds.score for ds in dimension_scores)
        average_score = total_score / len(dimension_scores)
        mbti_type = getattr(speech_input, 'mbti_type', None) or getattr(speech, 'mbti_type', None) or "未知"
        return SpeechScoreResult(
            speech_id=speech_input.speech_id,
            debater_name=speech_input.debater_name,
            mbti_type=mbti_type,
            stage=speech_input.stage,
            dimension_scores=dimension_scores,
            total_score=total_score,
            average_score=average_score
        )

    async def evaluate_stage(self, speeches: List[DifySpeechInput], stage: DebateStage) -> List[SpeechScoreResult]:
        # 普通环节：对每条发言评分（并发）
        stage_speeches = [s for s in speeches if s.stage == stage]
        tasks = [self.evaluate_single_speech(s) for s in stage_speeches]
        return await asyncio.gather(*tasks)

    async def evaluate_free_debate(self, speeches: List[DifySpeechInput]) -> List[SpeechScoreResult]:
        # 自由辩论：按辩手整体评分（并发）
        free_speeches = [s for s in speeches if s.stage == DebateStage.FREE_DEBATE]
        debater_map: Dict[str, List[str]] = {}
        mbti_map: Dict[str, str] = {}
        for s in free_speeches:
            debater_map.setdefault(s.debater_name, []).append(s.content)
            mbti_map[s.debater_name] = s.mbti_type
        async def score_debater(debater, all_speeches):
            summary_input = FreeDebateSummaryInput(
                debater_name=debater,
                mbti_type=mbti_map.get(debater, "未知"),
                all_speeches=all_speeches
            )
            speech = Speech(
                debater=debater,
                stage=DebateStage.FREE_DEBATE,
                content="\n".join(all_speeches)
            )
            debate_info = DebateInfo("", [], [], [])
            judge_tasks = [judge.score_speech(speech, debate_info) for judge in self.judge_agents]
            judge_results = await asyncio.gather(*judge_tasks)
            dimension_scores = []
            for score_dict in judge_results:
                for dim, score in score_dict.items():
                    dimension_scores.append(SingleScore(dimension=dim, score=score, comment=""))
            total_score = sum(ds.score for ds in dimension_scores)
            average_score = total_score / len(dimension_scores)
            mbti_type = mbti_map.get(debater, "未知")
            return SpeechScoreResult(
                speech_id=f"free_{debater}",
                debater_name=debater,
                mbti_type=mbti_type,
                stage=DebateStage.FREE_DEBATE,
                dimension_scores=dimension_scores,
                total_score=total_score,
                average_score=average_score
            )
        tasks = [score_debater(debater, all_speeches) for debater, all_speeches in debater_map.items()]
        return await asyncio.gather(*tasks)

    async def evaluate_debate(self, speeches: List[DifySpeechInput]) -> List[SpeechScoreResult]:
        # 所有阶段并发评分
        stages = [DebateStage.OPENING, DebateStage.CROSS_EXAM, DebateStage.SUMMARY]
        tasks = [self.evaluate_stage(speeches, stage) for stage in stages]
        results = []
        stage_results = await asyncio.gather(*tasks)
        for r in stage_results:
            results.extend(r)
        # 自由辩论特殊处理
        free_results = await self.evaluate_free_debate(speeches)
        results.extend(free_results)
        return results
