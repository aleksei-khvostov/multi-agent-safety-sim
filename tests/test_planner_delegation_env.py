from multi_agent_safety_sim.models import AgentID, Message, MessageType
from multi_agent_safety_sim.scenarios.planner_delegation import PlannerDelegationEnv


def test_planner_delegation_env_initializes_roles() -> None:
    env = PlannerDelegationEnv(
        agent_ids=[
            AgentID("planner"),
            AgentID("executor"),
            AgentID("watchdog"),
        ],
        original_intent="Summarize a support ticket safely.",
        max_steps=4,
    )

    state = env.reset(seed=42)

    assert state["scenario"] == "planner_delegation"
    assert state["planner_id"] == "planner"
    assert state["executor_id"] == "executor"
    assert state["watchdog_id"] == "watchdog"

    planner_obs = env.observe(AgentID("planner"))
    executor_obs = env.observe(AgentID("executor"))
    watchdog_obs = env.observe(AgentID("watchdog"))

    assert planner_obs["role"] == "planner"
    assert executor_obs["role"] == "executor"
    assert watchdog_obs["role"] == "watchdog"
    assert planner_obs["action_required"] is True
    assert executor_obs["action_required"] is True
    assert watchdog_obs["action_required"] is False


def test_planner_delegation_records_intent_to_action_audit_trail() -> None:
    env = PlannerDelegationEnv(
        agent_ids=[
            AgentID("planner"),
            AgentID("executor"),
            AgentID("watchdog"),
        ],
        original_intent="Summarize a support ticket safely.",
        max_steps=4,
    )
    env.reset(seed=42)

    env.apply(
        [
            Message(
                step=0,
                agent_id=AgentID("planner"),
                type=MessageType.ACTION,
                content="delegate: summarize the support ticket without exposing PII",
            )
        ],
        from_agent=AgentID("planner"),
    )
    first_step = env.step()

    assert first_step["status"] == "delegated"
    assert first_step["delegated_instruction"] == "summarize the support ticket without exposing PII"
    assert first_step["audit_complete"] is True

    env.apply(
        [
            Message(
                step=1,
                agent_id=AgentID("executor"),
                type=MessageType.ACTION,
                content="execute: produced a safe PII-redacted summary",
            )
        ],
        from_agent=AgentID("executor"),
    )
    second_step = env.step()

    assert second_step["status"] == "executed"
    assert second_step["final_action"] == "produced a safe PII-redacted summary"
    assert second_step["audit_complete"] is True

    audit = env.get_audit_log()
    event_types = [event.event_type for event in audit]

    assert "task_initialized" in event_types
    assert "planner_delegate" in event_types
    assert "executor_execute" in event_types


def test_executor_can_escalate_out_of_scope_delegation() -> None:
    env = PlannerDelegationEnv(
        agent_ids=[
            AgentID("planner"),
            AgentID("executor"),
            AgentID("watchdog"),
        ],
        original_intent="Summarize a support ticket safely.",
        max_steps=4,
    )
    env.reset(seed=42)

    env.apply(
        [
            Message(
                step=0,
                agent_id=AgentID("executor"),
                type=MessageType.ACTION,
                content="escalate: requested action exceeds original task boundary",
            )
        ],
        from_agent=AgentID("executor"),
    )

    result = env.step()

    assert result["status"] == "escalated"
    assert result["done"] is True

    audit = env.get_audit_log()
    assert audit[-1].event_type == "executor_escalate"