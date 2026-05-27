from pydantic import BaseModel, field_validator
from typing import Literal
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import RunUsage


class InputRow(BaseModel):
    id: str
    scenario_id: str
    model: str
    provider: str
    model_settings: dict
    user_message: str
    image: str | None
    metadata: dict


class AgentResult(BaseModel):
    output: str
    all_messages: list[ModelMessage]
    usage: RunUsage


class OutputRow(BaseModel):
    id: str
    output: str | None
    all_messages: list[ModelMessage]
    usage: RunUsage | None
    error: str | None

class EngineInfo(BaseModel):
    minimal_engine_power: float | None = None
    maximal_engine_power: float | None = None
    minimal_engine_RPM: int | None = None
    maximal_engine_RPM: int | None = None
    minimal_engine_torque: float | None = None
    maximal_engine_torque: float | None = None


class BearingInfo(BaseModel):
    min_srednica_wewn_d: int | None = None
    max_srednica_wewn_d: int | None = None
    min_srednica_zewn_D: int | None = None
    max_srednica_zewn_D: int | None = None
    min_szerokosc_B: float | None = None
    max_szerokosc_B: float | None = None
    min_nosnosc_dyn_C: float | None = None
    max_nosnosc_dyn_C: float | None = None
    min_nosnosc_stat_C0: float | None = None
    max_nosnosc_stat_C0: float | None = None
    min_obc_zmecz_Pu: float | None = None
    max_obc_zmecz_Pu: float | None = None
    min_v: float | None = None
    max_v: float | None = None
    min_v_max: float | None = None
    max_v_max: float | None = None
    min_mass: float | None = None
    max_mass: float | None = None
    typ: Literal["Ball", "Angular Contact Ball", "Self-Aligning Ball", "Spherical Roller"]

    @field_validator("*", mode="before")
    @classmethod
    def convert_none_string(cls, value):
        """Convert string 'None' to actual None"""
        if isinstance(value, str) and value.strip().lower() == "none":
            return None
        return value
