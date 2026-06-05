import asyncio

from pydantic_ai import Agent

import agent_eval.functions.tools as tool_functions

agent = Agent()


async def convert_load_to_torque(load: float, gear_diam: float, angle: float = 0, friction_coeff: float = 0.1) -> str:
    """A Function to convert load to torque in Nm based on the gear diameter, angle of the load, and friction coefficient.

    Args:
        load (float): The load in kg applied to the gear vertically.
        gear_diam (float): The diameter of the gear in millimeters.
        angle (float): The angle of the load in degrees, defaults to 0 (vertical load).
        friction_coeff (float): The friction coefficient between the load and the gear, defaults to 0.1.

    Returns:
        torque (float): The resulting torque in Nm.
    """
    torque = tool_functions.convert_load_to_torque(load, gear_diam, angle, friction_coeff)
    return f"The converted load is equal to {torque:.2f} Nm of torque."


async def convert_linear_speed_to_rpm(speed_lin: float, gear_diam: float) -> str:
    """A function to convert linear speed to RPM.

    Args:
        speed_lin (float): The linear speed in m/s.
        gear_diam (float): The diameter of the gear in millimeters.
    Returns:
        rpm (float): The resulting RPM.
    """
    rpm = tool_functions.linear_speed_to_rpm(speed_lin, gear_diam)
    return f"The converted linear speed is equal to {rpm:.2f} RPM."


async def calculate_min_power(torque: float, rpm: float) -> str:
    """A function to calculate the minimum power required based on torque and RPM.

    Args:
        torque (float): The torque in Nm.
        rpm (float): The speed in RPM.
    Returns:
        min_power (float): The minimum power in kilowatts.
    """
    min_power = tool_functions.minimal_power(torque, rpm)
    return f"The minimal required power of the engine is {min_power:.2f} kW."


async def calculate_initial_gear_ratio(torque: float, motor_torque: float) -> str:
    """A function to calculate the initial gear ratio based on the required torque and motor torque.

    Args:
        torque (float): The required torque in Nm.
        motor_torque (float): The torque provided by the motor in Nm.
    Returns:
        gear_ratio (float): The initial gear ratio.
    """
    return f"The initial gear ratio is 1:{torque / motor_torque:.2f}."


async def calculate_shaft_stages_amount(gear_ratio: float) -> str:
    """A function to determine the number of shaft stages based on the gear ratio.

    Args:
        gear_ratio (float): The initial gear ratio.
    Returns:
        shaft_stages (int): The number of shaft stages.
    """
    shaft_stages = tool_functions.shaft_stages_amount(gear_ratio)
    return f"The gear transmission has {shaft_stages} stages."


async def calculate_actual_gear_ratio(output_torque: float, motor_torque: float, shaft_stages: int) -> str:
    """A function to calculate the actual gear ratio considering the efficiency of the gear system.

    Args:
        output_torque (float): The output torque in Nm.
        motor_torque (float): The torque provided by the motor in Nm.
        shaft_stages (int): The number of shaft stages in the gear system.
    Returns:
        actual_gear_ratio (float): The actual gear ratio considering efficiency.
    """
    actual_gear_ratio = tool_functions.calculate_actual_gear_ratio(output_torque, motor_torque, shaft_stages)
    return f"The actual gear ratio of the transmission is 1:{actual_gear_ratio:.2f}."


async def stage_gear_ratios(actual_gear_ratio: float, shaft_stages: int, gear_speed_type: str) -> str:
    """A function to calculate the gear ratio for each stage based on the actual gear ratio of the whole gear transmission and the number of shaft stages.

    Args:
        actual_gear_ratio (float): The actual gear ratio considering efficiency.
        shaft_stages (int): The number of shaft stages in the gear transmission.
        gear_speed_type (str): The type of gear speed (e.g., "fast").
    Returns:
        list: A list of gear ratios for each stage, formatted as strings.

    If the gear speed type is not defined, assume "fast" as the default type.
    """
    stage_gear_ratio_list = tool_functions.stage_gear_ratios(actual_gear_ratio, shaft_stages, gear_speed_type)
    result = []
    for shaft_stage in range(shaft_stages):
        stage_gear_ratio = stage_gear_ratio_list[shaft_stage]
        result.append(f"Stage {shaft_stage + 1} gear ratio: 1:{stage_gear_ratio}")
    return "\n".join(result)


if __name__ == "__main__":
    # example usage
    load = 300  # kg
    gear_diam = 52  # mm
    angle = 25  # degrees
    friction_coeff = 0.1
    motor_torque = 0.88  # Nm
    speed_lin = 0.125  # m/s
    gear_speed_type = "slow"  # przekładnia szybkobieżna (fast) lub wolnobieżna (slow)

    # torque = convert_load_to_torque(load, gear_diam, angle, friction_coeff)
    # rpm = convert_linear_speed_to_rpm(speed_lin, gear_diam)
    # min_power = calculate_min_power(torque, rpm)
    # gear_ratio = calculate_initial_gear_ratio(torque, motor_torque)
    # stages = calculate_shaft_stages_amount(gear_ratio)
    # actual_gear_ratio = calculate_actual_gear_ratio(torque, motor_torque, stages)
    # stage_gear_ratio_list = stage_gear_ratios(actual_gear_ratio, stages, gear_speed_type)
    # print(f"Torque: {torque:.2f} Nm\n"
    #       f"RPM: {rpm:.2f}\n"
    #       f"Minimum Power: {min_power:.2f} kW\n"
    #       f"Number of Shaft Stages: {stages}\n"
    #       f"Actual Gear Ratio: {actual_gear_ratio:.2f}\n"
    #       f"Each Stage Gear Ratio: {stage_gear_ratio_list}")
    print(asyncio.run(stage_gear_ratios(58, 4, "fast")))
