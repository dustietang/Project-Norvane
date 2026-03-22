import json

from config import (
    LLM_DECISION_TEMPERATURE,
    LLM_INTERNALIZATION_TEMPERATURE,
    VALID_STANCES,
)
from src.incidents.incident import get_decision_prompt, get_internalization_prompt
from src.utils.llm_utils import (
    gen_completion,
    parse_json_response,
    repair_decision_json,
)


class Agent:
    def __init__(self, agent_id: int, persona_type: str):
        self.agent_id = agent_id
        self.persona_type = persona_type
        self.conversation_history: list[dict] = []
        self.action_history: list[dict] = []
        self.internalization_response: str = ""

    def internalize(self) -> str:
        prompt = get_internalization_prompt(self.persona_type)
        self.conversation_history = [{"role": "user", "content": prompt}]

        response = gen_completion(
            self.conversation_history,
            temperature=LLM_INTERNALIZATION_TEMPERATURE,
        )

        self.conversation_history.append({"role": "assistant", "content": response})
        self.internalization_response = response
        return response

    def decide_action(self, round_num: int, feed_summary: str = "") -> dict:
        prompt = get_decision_prompt(round_num, feed_summary)
        self.conversation_history.append({"role": "user", "content": prompt})

        max_retries = 2
        decision = None
        last_error = "unknown"

        for attempt in range(max_retries + 1):
            response = gen_completion(
                self.conversation_history,
                temperature=LLM_DECISION_TEMPERATURE,
                json_mode=True,
            )
            parsed = parse_json_response(response)

            if parsed and self._validate_decision(parsed):
                decision = parsed
                self.conversation_history.append({"role": "assistant", "content": response})
                break

            last_error = f"invalid primary response on attempt {attempt + 1}"

            try:
                repaired = repair_decision_json(response)
                repaired_parsed = parse_json_response(repaired)
                if repaired_parsed and self._validate_decision(repaired_parsed):
                    decision = repaired_parsed
                    self.conversation_history.append({"role": "assistant", "content": repaired})
                    break
                last_error = f"repair failed on attempt {attempt + 1}"
            except Exception as e:
                last_error = f"repair exception: {e}"

        if decision is None:
            decision = self._default_decision(last_error)
            self.conversation_history.append(
                {"role": "assistant", "content": json.dumps(decision, ensure_ascii=False)}
            )

        decision["round"] = round_num
        decision["agent_id"] = self.agent_id
        decision["persona_type"] = self.persona_type
        self.action_history.append(decision)
        return decision

    def _validate_decision(self, parsed: dict) -> bool:
        required_keys = {"action", "stance", "content", "reasoning"}
        if not isinstance(parsed, dict):
            return False
        if set(parsed.keys()) != required_keys:
            return False
        if not isinstance(parsed.get("action"), int):
            return False
        if parsed["action"] < 0 or parsed["action"] > 5:
            return False
        if parsed.get("stance") not in VALID_STANCES:
            return False
        if not isinstance(parsed.get("content"), str):
            return False
        if not isinstance(parsed.get("reasoning"), str):
            return False
        if parsed["action"] in (0, 1, 2) and parsed["content"].strip():
            return False
        if parsed["action"] in (3, 4, 5) and not parsed["content"].strip():
            return False
        if parsed["action"] == 1 and any(d["action"] == 1 for d in self.action_history):
            return False
        return True

    def _default_decision(self, error: str = "unknown") -> dict:
        return {
            "action": 0,
            "stance": "neutral",
            "content": "",
            "reasoning": (
                "DEFAULT_DECISION: response parsing/validation failed. "
                f"Error={error}"
            ),
        }

