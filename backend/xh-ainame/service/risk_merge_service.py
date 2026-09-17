from models import AsyncSession
from models.law_version import LawVersion
from repository.law_repository import LawRepo
from schemas.agent import RiskDetail, RiskFromModel, RiskReason
from errors import TrademarkDataError, ClauseIdHallucinatedError


class RiskMergeService:
    """把规则扫出来的风险和模型判出来的风险，按条款聚合成 RiskDetail 列表。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.law_repo = LawRepo(self.session)

    async def merge_risks(
            self,
            candidate_name: str,
            scan_hits: list[tuple[int, str]],
            version: LawVersion,
            model_risks: list[RiskFromModel],
    ) -> list[RiskDetail]:

        grouped: dict[int, list[RiskReason]] = {}
        for clause_id, text in scan_hits:
            grouped.setdefault(clause_id, []).append(
                RiskReason(judged_by="系统扫描", text=text))
        for r in model_risks:
            grouped.setdefault(r.clause_id, []).append(
                RiskReason(judged_by="AI判断", text=r.reason))

        if not grouped:
            return []

        details: list[RiskDetail] = []
        for clause_id, reasons in grouped.items():
            clause = await self.law_repo.get_law_clause_by_id(clause_id)

            if clause is None:
                if any(x.judged_by == "系统扫描" for x in reasons):
                    raise TrademarkDataError(
                        f"law_clause 表里没有 id={clause_id} 的条款，"
                        f"但名录映射指向了它（候选名『{candidate_name}』）")
                valid = [c.id for c in await self.law_repo.get_clauses_by_version(version.id)]
                raise ClauseIdHallucinatedError(candidate_name, clause_id, valid)

            details.append(RiskDetail(
                clause_number=clause.clause_number,
                clause_original=clause.clause_original,
                risk_grade=clause.risk_grade,
                law_name=version.law_name,
                law_version_name=version.version_name,
                reasons=reasons,
            ))

        return details