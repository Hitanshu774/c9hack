# Valorant Team Strategy Dataset: NRG
**Source:** `nrg_team_strategy_semantic.json`
**Scope:** last_5_matches

---

## Section 1: Tempo & Pacing Profile

This section defines the temporal flow and phase prioritization of the team's gameplay.

| Data Point | Value | Semantic Definition |
| :--- | :--- | :--- |
| **pace** | `slow` | The team prioritizes information gathering, defaults, and late-round execution. |
| **first_contact** | `mid` | First engagement occurs after initial defaults or probing utility. |
| **default_phase** | `mid` | Defaults are used to gather information before mid-round decisions. |
| **late_round_strength** | `high` | The team consistently wins rounds that reach late-game scenarios. |

---

## Section 2: Utility Usage & Site Execution

This section categorizes how ability resources are managed and the team's tendencies regarding site commitment.

| Data Point | Value | Semantic Definition |
| :--- | :--- | :--- |
| **early_utility** | `moderate` | Utility is used selectively for information or light pressure. |
| **utility_impact** | `low` | Utility contributes minimally to damage or round outcomes. |
| **site_hit_frequency** | `high` | The team frequently commits to site executions. |
| **post_plant_success** | `high` | The team reliably wins post-plant scenarios. |

---

## Section 3: Team Coordination & Combat Mechanics

This section outlines the spatial relationships between teammates and effectiveness in trading kills.

| Data Point | Value | Semantic Definition |
| :--- | :--- | :--- |
| **trade_coordination** | `average` | Trades occur but are not always immediate. |
| **first_contact_support** | `tight` | First contacts are regularly supported by teammates or utility. |
| **pistol_conversion** | `high` | Pistol wins are consistently converted into follow-up rounds. |

---

## Section 4: Defensive Protocol

This section describes the team's behavior and positioning when playing on the defensive side of the map.

| Data Point | Value | Semantic Definition |
| :--- | :--- | :--- |
| **defensive_style** | `hold-oriented` | The team prefers anchoring sites and defending initial attacks. |
| **defensive_aggression** | `high` | Frequent early fights, pushes, or proactive defensive plays. |

---

## Section 5: Stability & Round Risk

This section quantifies the volatility of rounds and the level of activity during the middle phase of the round.

| Data Point | Value | Semantic Definition |
| :--- | :--- | :--- |
| **round_stability** | `moderately unstable` | Some advantages are lost mid-round. |
| **mid_round_activity** | `low` | Minimal proactive plays during mid-round. |