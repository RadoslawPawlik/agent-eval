import math

from pydantic_ai import Agent

agent = Agent()



async def convert_load_to_torque(load: float, gear_diam: float, angle: float, friction_coeff: float) -> str:
    """A Function to convert load to torque in Nm based on the gear diameter, angle of the load, and friction coefficient.

    Args:
        load (float): The load in kg applied to the gear vertically.
        gear_diam (float): The diameter of the gear in meters.
        angle (float): The angle of the load in degrees.
        friction_coeff (float): The friction coefficient between the load and the gear.

    Returns:
        torque (float): The resulting torque in Nm.
    """

    def convert_load_to_torque() -> float:
        Q = load * 9.81 * math.sin(math.radians(angle))
        F_T = load * 9.81 * math.cos(math.radians(angle)) * friction_coeff
        F = Q + F_T
        torque = F * (gear_diam / 2) / 1000
        return torque

    torque = convert_load_to_torque()
    return f"The converted load is equal to {torque} Nm of torque."



async def convert_linear_speed_to_rpm(speed_lin: float, gear_diam: float) -> str:
    """A function to convert linear speed to RPM.

    Args:
        speed_lin (float): The linear speed in m/s.
        gear_diam (int): The diameter of the gear in millimeters.
    Returns:
        rpm (float): The resulting RPM.
    """

    def linear_speed_to_rpm() -> float:
        rot_time = (2 * math.pi * gear_diam / (2 * 1000)) / speed_lin  # Time of one rotation
        rpm = 60 / rot_time
        return rpm

    rpm = linear_speed_to_rpm()
    return f"The converted linear speed is equal to {rpm} RPM."



async def calculate_min_power(torque: float, rpm: float) -> str:
    """A function to calculate the minimum power required based on torque and RPM.

    Args:
        torque (float): The torque in Nm.
        rpm (float): The speed in RPM.
    Returns:
        min_power (float): The minimum power in kilowatts.
    """

    def minimal_power() -> float:
        min_power = (torque * rpm) / 9550
        return min_power

    min_power = minimal_power()
    return f"The minimal required power of the engine is {min_power} kW."



async def calculate_initial_gear_ratio(torque: float, motor_torque: float) -> str:
    """A function to calculate the initial gear ratio based on the required torque and motor torque.

    Args:
        torque (float): The required torque in Nm.
        motor_torque (float): The torque provided by the motor in Nm.
    Returns:
        gear_ratio (float): The initial gear ratio.
    """

    def calculate_initial_gear_ratio(torque, motor_torque) -> float:
        gear_ratio = torque / motor_torque
        return gear_ratio

    gear_ratio = calculate_initial_gear_ratio(torque, motor_torque)
    return f"The initial gear ratio is 1:{gear_ratio}."



async def calculate_shaft_stages_amount(gear_ratio: float) -> str:
    """A function to determine the number of shaft stages based on the gear ratio.

    Args:
        gear_ratio (float): The initial gear ratio.
    Returns:
        shaft_stages (int): The number of shaft stages.
    """

    def shaft_stages_amount(gear_ratio) -> int:
        if gear_ratio <= 5:
            shaft_stages = 1
            return shaft_stages
        elif gear_ratio <= 20:
            shaft_stages = 2
            return shaft_stages
        else:
            shaft_stages = 3
            return shaft_stages

    shaft_stages = shaft_stages_amount(gear_ratio)
    return f"The gear transmission has {shaft_stages} stages."



async def calculate_actual_gear_ratio(torque: float, motor_torque: float, shaft_stages: int) -> str:
    """A function to calculate the actual gear ratio considering the efficiency of the gear system.

    Args:
        torque (float): The required torque in Nm.
        motor_torque (float): The torque provided by the motor in Nm.
        shaft_stages (int): The number of shaft stages in the gear system.
    Returns:
        actual_gear_ratio (float): The actual gear ratio considering efficiency.
    """

    def calculate_actual_gear_ratio(torque, motor_torque, shaft_stages) -> float:
        actual_gear_ratio = torque / (motor_torque * (0.98**shaft_stages))
        return actual_gear_ratio

    actual_gear_ratio = calculate_actual_gear_ratio(torque, motor_torque, shaft_stages)
    return f"The actual gear ratio of the transmission is 1:{actual_gear_ratio}"



async def stage_gear_ratios(actual_gear_ratio: float, shaft_stages: int, gear_speed_type: str) -> str:
    """A function to calculate the gear ratio for each stage based on the actual gear ratio and the number of shaft stages.

    Args:
        actual_gear_ratio (float): The actual gear ratio considering efficiency.
        shaft_stages (int): The number of shaft stages in the gear system.
        gear_speed_type (str): The type of gear speed (e.g., "fast").
    Returns:
        list: A list of gear ratios for each stage, formatted as strings.
    """

    def stage_gear_ratios(actual_gear_ratio, shaft_stages, gear_speed_type) -> list:
        STAGES_REFERENCE = [1, 1.25, 1.6, 2, 2.5, 3.15, 4, 5]
        stage_gear_ratio_list = []
        if gear_speed_type == "fast":
            if shaft_stages == 1:
                stage_gear_ratio_list.append(actual_gear_ratio)
            elif shaft_stages == 2:
                stage_gear_ratio_list.append(1.2 * math.sqrt(actual_gear_ratio))  # stage 1
                stage_gear_ratio_list.append(actual_gear_ratio / stage_gear_ratio_list[0])  # stage 2
            elif shaft_stages == 3:
                stage_gear_ratio_list.extend(STAGES_REFERENCE[7 - stage] for stage in range(shaft_stages))
                stage_gear_ratio_list[-1] = actual_gear_ratio / (
                    math.prod(stage_gear_ratio_list[:-1])
                )  # divide by every stage except the last one
                if (
                    stage_gear_ratio_list[-1] < 3.1
                ):  # minimal gear ratio on any stage has to be above 3.1, last stage has always the lowest ratio because of the biggest torque
                    stage_gear_ratio_list = [
                        STAGES_REFERENCE[6 - stage] for stage in range(shaft_stages)
                    ]  # do the same but start with 5 instead of 4
                    stage_gear_ratio_list[-1] = actual_gear_ratio / (math.prod(stage_gear_ratio_list[:-1]))
            stage_gear_ratio_list.sort(reverse=True)  # sorting
            stage_gear_ratio_list = ["%.2f" % gear for gear in stage_gear_ratio_list]  # stolen from stackoverflow :)
        elif gear_speed_type == "slow":
            if shaft_stages == 1:
                stage_gear_ratio_list.append(actual_gear_ratio)
            elif shaft_stages == 2:
                stage_gear_ratio_list.append(1.2 * math.sqrt(actual_gear_ratio))  # stage 1
                stage_gear_ratio_list.append(actual_gear_ratio / stage_gear_ratio_list[0])  # stage 2
            elif shaft_stages == 3:
                stage_gear_ratio_list.extend(STAGES_REFERENCE[6 - stage] for stage in range(shaft_stages))
                stage_gear_ratio_list[-1] = actual_gear_ratio / (math.prod(stage_gear_ratio_list[:-1]))
                if (
                    stage_gear_ratio_list[-1] < 2.5
                ):  # minimal gear ratio on any stage has to above 2.5, last stage has always the lowest ratio because of the biggest torque
                    stage_gear_ratio_list = [
                        STAGES_REFERENCE[5 - stage] for stage in range(shaft_stages)
                    ]  # do the same but start with 5 instead of 4
                    stage_gear_ratio_list[-1] = actual_gear_ratio / (math.prod(stage_gear_ratio_list[:-1]))
            stage_gear_ratio_list.sort(reverse=True)
            stage_gear_ratio_list = ["%.2f" % gear for gear in stage_gear_ratio_list]  # stolen from stackoverflow :)
        return stage_gear_ratio_list

    stage_gear_ratio_list = stage_gear_ratios(actual_gear_ratio, shaft_stages, gear_speed_type)
    return f"The gear ratios for each stage are: {stage_gear_ratio_list}"


# if __name__ == "__main__":
#     # example usage
#     load = 300  # kg
#     gear_diam = 52  # mm
#     angle = 25 # degrees
#     friction_coeff = 0.1
#     motor_torque = 0.88  # Nm
#     speed_lin = 0.125  # m/s
#     gear_speed_type = "fast"    #przekładnia szybkobieżna (fast) lub wolnobieżna (slow)

#     torque = convert_load_to_torque(load, gear_diam, angle, friction_coeff)
#     rpm = convert_linear_speed_to_rpm(speed_lin, gear_diam)
#     min_power = calculate_min_power(torque, rpm)
#     gear_ratio = calculate_initial_gear_ratio(torque, motor_torque)
#     stages = calculate_shaft_stages_amount(gear_ratio)
#     actual_gear_ratio = calculate_actual_gear_ratio(torque, motor_torque, stages)
#     stage_gear_ratio_list = stage_gear_ratios(actual_gear_ratio, stages, gear_speed_type)
#     print(f"Torque: {torque:.2f} Nm\n"
#           f"RPM: {rpm:.2f}\n"
#           f"Minimum Power: {min_power:.2f} kW\n"
#           f"Number of Shaft Stages: {stages}\n"
#           f"Actual Gear Ratio: {actual_gear_ratio:.2f}\n"
#           f"Each Stage Gear Ratio: {stage_gear_ratio_list}")
