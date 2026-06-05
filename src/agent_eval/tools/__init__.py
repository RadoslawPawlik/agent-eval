from agent_eval.tools.bearing_extraction import find_bearing
from agent_eval.tools.engine_extraction import find_engine
from agent_eval.tools.tools import (
    calculate_actual_gear_ratio,
    calculate_initial_gear_ratio,
    calculate_min_power,
    calculate_shaft_stages_amount,
    convert_linear_speed_to_rpm,
    convert_load_to_torque,
    stage_gear_ratios,
)

tools = (
    find_engine,
    convert_load_to_torque,
    convert_linear_speed_to_rpm,
    calculate_min_power,
    calculate_initial_gear_ratio,
    calculate_shaft_stages_amount,
    calculate_actual_gear_ratio,
    stage_gear_ratios,
    find_bearing,
)

__all__ = ["tools"]
