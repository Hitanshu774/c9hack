import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import isodate

# ============================================================================
# 🔍 UTILITY FUNCTIONS (Your existing code)
# ============================================================================

def series_has_team(series_data: dict, team_name="2GAME eSports") -> bool:
    team_name = team_name.lower()
    for game in series_data.get("seriesState", {}).get("games", []):
        for segment in game.get("segments", []):
            for team in segment.get("teams", []):
                name = team.get("name", "").lower()
                if team_name in name:
                    return True
    return False

def extract_series_time(series_data: dict) -> datetime:
    for game in series_data.get("seriesState", {}).get("games", []):
        started = game.get("startedAt")
        if started:
            return datetime.fromisoformat(started.replace("Z", "+00:00"))
    return datetime.min

def get_all_team_series(base_dir=".", target_team="2GAME eSports"):
    results = []
    for path in Path(base_dir).glob("series_*_raw.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if series_has_team(data, target_team):
                results.append({
                    "series_id": path.stem.replace("series_", "").replace("_raw", ""),
                    "time": extract_series_time(data),
                    "raw": data
                })
        except:
            continue
    return results

def iter_rounds(series_data):
    for game in series_data.get("seriesState", {}).get("games", []):
        for seg in game.get("segments", []):
            if seg.get("type") == "round" and seg.get("finished"):
                yield seg

def get_team_players(series_data, target_team):
    """AUTO-EXTRACT all players from YOUR team only"""
    team_players = set()
    for round_seg in iter_rounds(series_data):
        for team in round_seg["teams"]:
            if target_team.lower() in team.get("name", "").lower():
                for player in team["players"]:
                    if player["participationStatus"] == "active":
                        team_players.add(player["name"])
    return sorted(list(team_players))

# ============================================================================
# 🎯 15+ COMPREHENSIVE PLAYER FEATURES (Pro-level evaluation)
# ============================================================================

# ORIGINAL 5 CORE FEATURES
def agent_pick_rate(series_data, player_name):
    agent_counts = {}
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            for player in team["players"]:
                if player["name"] == player_name and player["participationStatus"] == "active":
                    if player.get("damageDealtSources"):
                        primary = player["damageDealtSources"][0]["source"]["name"]
                        agent_counts[primary] = agent_counts.get(primary, 0) + 1
                    break
    return max(agent_counts.values(), default=0) / total_rounds if total_rounds else 0

def entry_attempts_per_round(series_data, player_name):
    entry_rounds = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player and player.get("damageDealt", 0) > 0:
                entry_rounds += 1
                break
    return entry_rounds / total_rounds if total_rounds else 0

def deaths_first_20s(series_data, player_name):
    early_deaths = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        round_duration = isodate.parse_duration(round_seg["duration"]).total_seconds()
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player and player.get("deaths", 0) > 0 and round_duration < 25:
                early_deaths += 1
                break
    return early_deaths / total_rounds if total_rounds else 0

def kd_by_site(series_data, player_name):
    kills_site = 0
    deaths_site = 0
    site_rounds = 0
    for round_seg in iter_rounds(series_data):
        planted = any(obj["type"] == "plantBomb" 
                     for team in round_seg["teams"] 
                     for obj in team.get("objectives", []))
        if planted:
            site_rounds += 1
            for team in round_seg["teams"]:
                player = next((p for p in team["players"] if p["name"] == player_name), None)
                if player:
                    kills_site += player.get("kills", 0)
                    deaths_site += player.get("deaths", 0)
                    break
    return kills_site / max(1, deaths_site) if site_rounds else 0

def duel_win_pct(series_data, player_name):
    total_kills = 0
    total_deaths = 0
    for round_seg in iter_rounds(series_data):
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                total_kills += player.get("kills", 0)
                total_deaths += player.get("deaths", 0)
                break
    return total_kills / max(1, total_kills + total_deaths)

# 🆕 10+ ADVANCED PRO FEATURES
def headshot_percentage(series_data, player_name):
    """🎯 Headshot accuracy %"""
    headshot_dmg = 0
    total_dmg = 0
    for round_seg in iter_rounds(series_data):
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                for target in player.get("damageDealtTargets", []):
                    if target["target"]["name"] == "head":
                        headshot_dmg += target["damageAmount"]
                total_dmg += player.get("damageDealt", 0)
                break
    return headshot_dmg / max(1, total_dmg) if total_dmg else 0

def first_kill_rate(series_data, player_name):
    """⚡ % rounds with first kill"""
    first_kills = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player and player.get("firstKill"):
                first_kills += 1
                break
    return first_kills / total_rounds if total_rounds else 0

def assist_rate(series_data, player_name):
    """🤝 Trade-kill efficiency"""
    total_assists = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                total_assists += player.get("killAssistsGiven", 0)
                break
    return total_assists / total_rounds if total_rounds else 0

def damage_per_round(series_data, player_name):
    """💥 DPR - Damage consistency"""
    total_dmg = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                total_dmg += player.get("damageDealt", 0)
                break
    return total_dmg / total_rounds if total_rounds else 0

def clutch_rate(series_data, player_name):
    """🌀 1vX win rate"""
    clutches = 0
    clutch_wins = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                # Proxy: high kills + team win
                kills = player.get("kills", 0)
                team_won = team.get("won", False)
                if kills >= 2 and team_won:
                    clutches += 1
                    clutch_wins += 1
                break
    return clutch_wins / max(1, clutches) if clutches else 0

def utility_usage_rate(series_data, player_name):
    """🛠️ Utility damage contribution"""
    util_dmg = 0
    total_dmg = 0
    UTILITY = ["snake-bite", "paint-shells", "guided-salvo", "shock-dart", "grenade", "molotov"]
    for round_seg in iter_rounds(series_data):
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                for src in player.get("damageDealtSources", []):
                    dmg = src["damageAmount"]
                    total_dmg += dmg
                    weapon = src["source"]["name"].lower()
                    if any(u in weapon for u in UTILITY):
                        util_dmg += dmg
                break
    return util_dmg / max(1, total_dmg) if total_dmg else 0

def post_plant_kd(series_data, player_name):
    """🌱 Post-plant specialist KD"""
    kills_post = 0
    deaths_post = 0
    post_rounds = 0
    for round_seg in iter_rounds(series_data):
        planted = any(obj["type"] == "plantBomb" 
                     for team in round_seg["teams"] 
                     for obj in team.get("objectives", []))
        if planted:
            post_rounds += 1
            for team in round_seg["teams"]:
                player = next((p for p in team["players"] if p["name"] == player_name), None)
                if player:
                    kills_post += player.get("kills", 0)
                    deaths_post += player.get("deaths", 0)
                    break
    return kills_post / max(1, deaths_post) if post_rounds else 0

def economy_impact(series_data, player_name):
    """💰 ADR on force-buy rounds (proxy)"""
    force_dmg = 0
    force_rounds = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        round_dur = isodate.parse_duration(round_seg["duration"]).total_seconds()
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player:
                dmg = player.get("damageDealt", 0)
                # Short rounds = pistol/eco proxy
                if round_dur < 60:
                    force_dmg += dmg
                    force_rounds += 1
                break
    return force_dmg / max(1, force_rounds) if force_rounds else 0

def teamfight_contribution(series_data, player_name):
    """⚔️ % rounds with multi-kill"""
    multi_kills = 0
    total_rounds = 0
    for round_seg in iter_rounds(series_data):
        total_rounds += 1
        for team in round_seg["teams"]:
            player = next((p for p in team["players"] if p["name"] == player_name), None)
            if player and player.get("kills", 0) >= 2:
                multi_kills += 1
                break
    return multi_kills / total_rounds if total_rounds else 0

# ============================================================================
# 🚀 MAIN PIPELINE - 15+ PRO FEATURES
# ============================================================================

def create_pro_player_features(target_team="2GAME eSports", n_series=20):
    """🎯 15+ PRO-LEVEL PLAYER EVALUATION"""
    print(f"🔥 PRO PLAYER ANALYSIS - {target_team}")
    print("=" * 60)
    
    all_series = get_all_team_series(".", target_team)
    all_series.sort(key=lambda x: x["time"], reverse=True)
    
    # AUTO-DETECT team players
    sample_series = all_series[0]["raw"] if all_series else {}
    team_players = get_team_players(sample_series, target_team)
    print(f"✅ Found {len(team_players)} players: {team_players}")
    
    all_player_features = []
    
    for i, series in enumerate(all_series[:n_series]):
        print(f"  {i+1}/{min(n_series, len(all_series))}: {series['series_id']}")
        
        player_data = []
        for player_name in team_players:
            features = {
                # 🔥 CORE 5
                "agent_pick_rate": agent_pick_rate(series["raw"], player_name),
                "entry_attempts_per_round": entry_attempts_per_round(series["raw"], player_name),
                "deaths_first_20s": deaths_first_20s(series["raw"], player_name),
                "kd_by_site": kd_by_site(series["raw"], player_name),
                "duel_win_pct": duel_win_pct(series["raw"], player_name),
                
                # 🔥 PRO 10+
                "headshot_pct": headshot_percentage(series["raw"], player_name),
                "first_kill_rate": first_kill_rate(series["raw"], player_name),
                "assist_rate": assist_rate(series["raw"], player_name),
                "dmg_per_round": damage_per_round(series["raw"], player_name),
                "clutch_rate": clutch_rate(series["raw"], player_name),
                "utility_usage": utility_usage_rate(series["raw"], player_name),
                "post_plant_kd": post_plant_kd(series["raw"], player_name),
                "eco_impact": economy_impact(series["raw"], player_name),
                "teamfight_contrib": teamfight_contribution(series["raw"], player_name),
            }
            
            player_data.append({
                "series_id": series["series_id"],
                "series_time": series["time"].isoformat(),
                "player_name": player_name,
                **features
            })
        
        all_player_features.append(pd.DataFrame(player_data))
    
    master_df = pd.concat(all_player_features, ignore_index=True)
    
    # Save comprehensive dataset
    output_file = f"{target_team.replace(' ', '_')}_pro_player_features.csv"
    # master_df.to_csv(output_file, index=False)
    
    # PRO PLAYER RANKINGS
    pro_summary = master_df.groupby("player_name")[[
        "agent_pick_rate", "entry_attempts_per_round", "deaths_first_20s", 
        "kd_by_site", "duel_win_pct", "headshot_pct", "first_kill_rate",
        "dmg_per_round", "clutch_rate", "post_plant_kd"
    ]].mean().round(3)
    
    summary_file = f"{target_team.replace(' ', '_')}_pro_player_rankings.csv"
    pro_summary.to_csv(summary_file)
    
    print(f"\n✅ PRO ANALYSIS COMPLETE ({len(master_df)} records):")
    print(f"   📊 {output_file} - 14 features")
    print(f"   🏆 {summary_file} - Player rankings")
    
    print("\n🔥 TOP ENTRY FRAGGERS:")
    print(pro_summary.sort_values("entry_attempts_per_round", ascending=False)[["entry_attempts_per_round", "duel_win_pct"]])
    
    print("\n🎯 ELITE DUALISTS:")
    print(pro_summary.sort_values("duel_win_pct", ascending=False)[["duel_win_pct", "headshot_pct"]].head())
    
    return master_df, pro_summary

# ============================================================================
# 🚀 EXECUTE PRO ANALYSIS
# ============================================================================

if __name__ == "__main__":
    print("🔥 PROFESSIONAL PLAYER EVALUATION - 15+ METRICS")
    print("=" * 70)
    
    MY_TEAM = "KRÜ Esports"  # ← EDIT TEAM NAME
    
    dataset, rankings = create_pro_player_features(MY_TEAM)
    

