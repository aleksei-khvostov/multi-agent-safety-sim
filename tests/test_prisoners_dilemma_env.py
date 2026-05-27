from multi_agent_safety_sim.models import AgentID, Message, MessageType
from multi_agent_safety_sim.scenarios.prisoners_dilemma import PrisonersDilemmaEnv


def test_pending_agents_excludes_watchdog_observer() -> None:
    env = PrisonersDilemmaEnv(
        agent_ids=[
            AgentID("player_0"),
            AgentID("player_1"),
            AgentID("player_2"),
        ],
        max_rounds=3,
        seed=42,
    )
    env.reset(seed=42)

    env.apply(
        [
            Message(
                step=0,
                agent_id=AgentID("player_1"),
                type=MessageType.ACTION,
                content="cooperate",
            )
        ],
        from_agent=AgentID("player_1"),
    )

    result = env.step()

    assert result["status"] == "waiting_for_actions"
    assert result["pending_agents"] == ["player_0"]
    assert "player_2" not in result["pending_agents"]