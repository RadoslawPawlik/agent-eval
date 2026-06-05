import math


def convert_load_to_torque(load: float, gear_diam: float, angle: float, friction_coeff: float) -> float:
    Q = load * 9.81 * math.sin(math.radians(angle))
    F_T = load * 9.81 * math.cos(math.radians(angle)) * friction_coeff
    F = Q + F_T
    return F * (gear_diam / 2) / 1000


def linear_speed_to_rpm(speed_lin: float, gear_diam: float) -> float:
    rot_time = (2 * math.pi * gear_diam / (2 * 1000)) / speed_lin  # Time of one rotation
    return 60 / rot_time


def minimal_power(torque: float, rpm: float) -> float:
    min_power = (torque * rpm) / 9550
    return min_power


def shaft_stages_amount(gear_ratio: float) -> int:
    if gear_ratio <= 5:
        shaft_stages = 1
        return shaft_stages
    elif gear_ratio <= 20:
        shaft_stages = 2
        return shaft_stages
    else:
        shaft_stages = 3
        return shaft_stages


def calculate_actual_gear_ratio(output_torque: float, motor_torque: float, shaft_stages: int) -> float:
    """A function to calculate the actual gear ratio considering the efficiency of the gear system.

    Args:
        output_torque (float): The output torque in Nm.
        motor_torque (float): The torque provided by the motor in Nm.
        shaft_stages (int): The number of shaft stages in the gear system.
    Returns:
        actual_gear_ratio (float): The actual gear ratio considering efficiency.
    """
    return output_torque / (motor_torque * (0.98**shaft_stages))


def stage_gear_ratios(actual_gear_ratio, shaft_stages, gear_speed_type="fast") -> list:
    STAGES_REFERENCE = [1, 1.25, 1.6, 2, 2.5, 3.15, 4, 5]
    stage_gear_ratio_list = []

    if gear_speed_type == "fast":
        min_ratio_threshold = 3.1
        start_index = 7
    elif gear_speed_type == "slow":
        min_ratio_threshold = 2.5
        start_index = 6
    else:
        return []

    if shaft_stages == 1:
        stage_gear_ratio_list.append(actual_gear_ratio)
    elif shaft_stages == 2:
        stage_gear_ratio_list.append(1.2 * math.sqrt(actual_gear_ratio))  # stage 1
        stage_gear_ratio_list.append(actual_gear_ratio / stage_gear_ratio_list[0])  # stage 2
    else:  # 3 or more stages
        stage_gear_ratio_list.extend(STAGES_REFERENCE[start_index - stage] for stage in range(shaft_stages))
        stage_gear_ratio_list[-1] = actual_gear_ratio / (math.prod(stage_gear_ratio_list[:-1]))

        if stage_gear_ratio_list[-1] < min_ratio_threshold:
            stage_gear_ratio_list = [STAGES_REFERENCE[start_index - 1 - stage] for stage in range(shaft_stages)]
            stage_gear_ratio_list[-1] = actual_gear_ratio / (math.prod(stage_gear_ratio_list[:-1]))

    stage_gear_ratio_list.sort(reverse=True)
    stage_gear_ratio_list = ["%.2f" % gear for gear in stage_gear_ratio_list]
    return stage_gear_ratio_list


if __name__ == "__main__":
    print(f"1-4: torque is {convert_load_to_torque(150, 200, 30, 0.15)}")
    print(f"5-8: torque is {convert_load_to_torque(500, 120, 45, 0.2)}")
    print(f"9-12: rpm is {linear_speed_to_rpm(2, 80)}")
    print(f"13-16: rpm is {linear_speed_to_rpm(1, 100)}")
    print(f"17-20: power is {minimal_power(350, 2500)}")
    print(f"21-24: power is {minimal_power(40, 1000)}")
    print(f"25-28: there are {shaft_stages_amount(10)} stages")
    print(f"29-32: there are {shaft_stages_amount(67)} stages")
    print(f"33-36: actual gear ratio is 1:{calculate_actual_gear_ratio(50, 0.88, 3)}")
    print(f"37-40: actual gear ratio is 1:{calculate_actual_gear_ratio(200, 1.5, 4)}")
    print(f"41-44: stage gear ratios are {stage_gear_ratios(47, 3)}")
    print(f"45-48: stage gear ratios are {stage_gear_ratios(97, 4, 'slow')}")
