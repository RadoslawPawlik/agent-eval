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
