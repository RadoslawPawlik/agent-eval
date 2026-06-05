#!/usr/bin/env python
import sys
sys.path.insert(0, 'src')

from agent_eval.functions.tools import stage_gear_ratios

# Test cases: (actual_gear_ratio, shaft_stages, gear_speed_type)
test_cases = [
    (47, 1, 'fast'),
    (47, 2, 'fast'),
    (97, 3, 'fast'),
    (150, 4, 'fast'),
    (200, 5, 'fast'),
    (97, 3, 'slow'),
    (150, 4, 'slow'),
    (200, 5, 'slow'),
]

print("Testing stage_gear_ratios function with various stage counts:\n")
for actual_ratio, stages, speed_type in test_cases:
    result = stage_gear_ratios(actual_ratio, stages, speed_type)
    print(f"Ratio: {actual_ratio}, Stages: {stages}, Type: {speed_type}")
    print(f"  Result: {result}\n")
