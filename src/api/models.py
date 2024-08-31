from pydantic import BaseModel

class OptionTrainning(BaseModel):
    pos_tool: str
    threshold_core_word: float = 0.0
    similarity_calculation_method: str
