from multi_agent_safety_sim.agents.llm_agent import _normalize_json_model_output
from multi_agent_safety_sim.models import LLMResponse


def test_normalize_json_model_output_strips_markdown_fence() -> None:
    raw = """```json
{
  "reasoning": "okay",
  "actions": [{"type": "action", "content": "cooperate"}]
}
```"""

    cleaned = _normalize_json_model_output(raw)
    parsed = LLMResponse.model_validate_json(cleaned)

    assert parsed.reasoning == "okay"
    assert parsed.actions[0].type == "action"
    assert parsed.actions[0].content == "cooperate"


def test_normalize_json_model_output_extracts_json_after_prose() -> None:
    raw = """I need to analyze this situation carefully.

{
  "reasoning": "I will play transparently.",
  "actions": [
    {"type": "speech", "content": "I intend to cooperate."},
    {"type": "action", "content": "cooperate"}
  ]
}
"""

    cleaned = _normalize_json_model_output(raw)
    parsed = LLMResponse.model_validate_json(cleaned)

    assert parsed.reasoning == "I will play transparently."
    assert [action.type for action in parsed.actions] == ["speech", "action"]
    assert parsed.actions[-1].content == "cooperate"


def test_normalize_json_model_output_handles_braces_inside_strings() -> None:
    raw = """Here is the JSON:
{
  "reasoning": "This string contains braces like {not json} safely.",
  "actions": [{"type": "action", "content": "cooperate"}]
}
extra trailing text"""

    cleaned = _normalize_json_model_output(raw)
    parsed = LLMResponse.model_validate_json(cleaned)

    assert parsed.reasoning == "This string contains braces like {not json} safely."
    assert parsed.actions[0].content == "cooperate"