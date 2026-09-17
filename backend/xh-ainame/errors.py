
class TrademarkDataError(Exception):
    """名录或法条数据对不上：系统故障，不是业务结果"""

class ClauseIdHallucinatedError(Exception):
    """模型给的 clause_id 不在当前版本里：模型幻觉，不是数据故障。
    上层（agent 循环）接住它，把 valid_ids 喂回模型让它重判一次。"""

    def __init__(self, candidate_name: str, bad_clause_id: int, valid_ids: list[int]):
        self.candidate_name = candidate_name
        self.bad_clause_id = bad_clause_id
        self.valid_ids = valid_ids
        super().__init__(
            f"候选名『{candidate_name}』：模型给的 clause_id={bad_clause_id} 不在当前版本里，"
            f"可选的是 {valid_ids}")