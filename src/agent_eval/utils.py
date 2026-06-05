import json
from pathlib import Path

import pandas as pd
from pydantic_core import to_jsonable_python

from agent_eval.schemas import InputRow


def save_json(data: object, path: str | Path) -> None:
    """Utility function to save data as JSON."""
    with open(path, "w") as f:
        json.dump(to_jsonable_python(data), f, indent=2)


def read_first_row(path: str | Path) -> InputRow:
    with open(path) as f:
        return InputRow.model_validate_json(f.readline())


def extract_data(json_file_path):
    """
    Extract key data from a JSONL file and return as a pandas DataFrame.

    Args:
        json_file_path: Path to the JSONL file

    Returns:
        pd.DataFrame: DataFrame with columns: initial_user_message, agent_output,
                     tool_name, input_tokens, cache_read_tokens, output_tokens,
                     reasoning_tokens, requests, tool_calls
    """
    df = pd.read_json(json_file_path, lines=True)

    data = []

    for _, row in df.iterrows():
        initial_user_message = None
        tool_name = None
        tool_calls_count = 0

        all_messages = row.get("all_messages")
        if isinstance(all_messages, list):
            for msg in all_messages:
                if isinstance(msg, dict) and "parts" in msg:
                    for part in msg["parts"]:
                        # Extract initial user message
                        if part.get("part_kind") == "user-prompt" and initial_user_message is None:
                            initial_user_message = part.get("content")

                        # Extract tool name and count tool calls
                        if part.get("part_kind") == "tool-call":
                            if tool_name is None:
                                tool_name = part.get("tool_name")
                            tool_calls_count += 1

        # Extract usage data
        usage = row.get("usage") or {}
        details = usage.get("details", {})

        data.append(
            {
                "initial_user_message": initial_user_message,
                "agent_output": row.get("output"),
                "tool_name": tool_name,
                "input_tokens": usage.get("input_tokens"),
                "cache_read_tokens": usage.get("cache_read_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "reasoning_tokens": details.get("reasoning_tokens"),
                "requests": usage.get("requests"),
                "tool_calls": tool_calls_count,
            }
        )

    return pd.DataFrame(data).to_csv(f"data\\results\\{json_file_path.stem}.csv", index=False)


# Usage
# tools = extract_data(r"data\output\test1_with_tools.jsonl")
# print(tools)  # Output: ['convert_load_to_torque']
# if __name__ == "__main__":
#     extract_data(r"data\output\test1_with_tools.jsonl")
