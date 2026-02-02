# import json
# import pandas as pd
# from pathlib import Path
# from collections import Counter
# import numpy as np

# # ============================================================================
# # 🎯 3️⃣ TEAM COMPOSITIONS & SETUP ANALYSIS
# # ============================================================================

# def analyze_team_compositions(target_team="2GAME eSports", n_series=20):
#     """Extract agent picks, site anchors, defensive setups, attack formations"""
    
#     def iter_rounds(series_data):
#         for game in series_data.get("seriesState", {}).get("games", []):
#             for seg in game.get("segments", []):
#                 if seg.get("type") == "round" and seg.get("finished"):
#                     yield seg
    
#     def get_team_agent_picks(round_seg, target_team):
#         """Get agent lineup for specific team"""
#         for team in round_seg["teams"]:
#             if target_team.lower() in team.get("name", "").lower():
#                 agents = {}
#                 for player in team["players"]:
#                     if player["participationStatus"] == "active":
#                         # Agent from primary weapon proxy (damageDealtSources[0])
#                         agent = "unknown"
#                         if player.get("damageDealtSources"):
#                             agent = player["damageDealtSources"][0]["source"]["name"]
#                         agents[player["name"]] = agent
#                 return agents
#         return {}
    
#     def identify_site_anchor(round_seg, target_team):
#         """Site anchor = highest kills on planted rounds"""
#         planted = any(obj["type"] == "plantBomb" 
#                      for team in round_seg["teams"] 
#                      for obj in team.get("objectives", []))
        
#         if not planted:
#             return None
        
#         for team in round_seg["teams"]:
#             if target_team.lower() in team.get("name", "").lower():
#                 top_player = max(team["players"], 
#                                key=lambda p: p.get("kills", 0), default=None)
#                 return top_player["name"] if top_player else None
#         return None
    
#     all_series = []
#     for path in Path(".").glob("series_*_raw.json"):
#         try:
#             with open(path, "r") as f:
#                 data = json.load(f)
#             if any(target_team.lower() in team.get("name", "").lower() 
#                    for game in data.get("seriesState", {}).get("games", [])
#                    for seg in game.get("segments", [])
#                    for team in seg.get("teams", [])):
#                 all_series.append({
#                     "id": path.stem.replace("series_", "").replace("_raw", ""),
#                     "data": data
#                 })
#         except:
#             continue
    
#     print(f"🔍 Analyzing {len(all_series)} series for {target_team}")
    
#     # 1️⃣ AGENT PICK FREQUENCY
#     agent_picks = Counter()
#     player_agent_map = {}
    
#     # 2️⃣ SITE ANCHOR PREFERENCES  
#     site_anchors = Counter()
    
#     # 3️⃣ DEFENSIVE SETUPS (most common 5-agent combos)
#     def_setups = Counter()
    
#     # 4️⃣ ATTACK FORMATIONS (player positions by kills location)
#     attack_formations = Counter()
    
#     for series in all_series[:n_series]:
#         for round_seg in iter_rounds(series["data"]):
#             agents = get_team_agent_picks(round_seg, target_team)
            
#             if agents:
#                 # Agent frequency
#                 for player, agent in agents.items():
#                     agent_picks[agent] += 1
#                     player_agent_map.setdefault(player, Counter())[agent] += 1
                
#                 # Defensive setup (sorted tuple for Counter)
#                 def_setup = tuple(sorted(agents.values()))
#                 def_setups[def_setup] += 1
                
#                 # Site anchor
#                 anchor = identify_site_anchor(round_seg, target_team)
#                 if anchor:
#                     site_anchors[anchor] += 1
    
#     # ADDITIONAL FEATURES
#     # 5️⃣ WIN RATE BY AGENT COMBO
#     win_rates = {}
#     for setup, count in def_setups.most_common(10):
#         # Calculate win rate for top setups
#         win_count = sum(1 for series in all_series[:5] 
#                        for round_seg in iter_rounds(series["data"])
#                        if tuple(sorted(get_team_agent_picks(round_seg, target_team).values())) == setup
#                        and next(team["won"] for team in round_seg["teams"] 
#                                if target_team.lower() in team["name"].lower()))
#         win_rates[''.join(setup)] = round(win_count / count, 3) if count else 0
    
#     # 6️⃣ ENTRY FRAGGER AGENT PREFERENCE
#     entry_agent_pref = {}
#     for player, agent_counts in player_agent_map.items():
#         total = sum(agent_counts.values())
#         if total > 10:  # Reliable sample
#             top_agent = agent_counts.most_common(1)[0]
#             entry_agent_pref[player] = {
#                 "primary_agent": top_agent[0],
#                 "pick_rate": round(top_agent[1]/total, 3)
#             }
    
#     # RESULTS
#     results = {
#         "team": target_team,
#         "series_analyzed": len(all_series),
#         "agent_pick_frequency": dict(agent_picks.most_common()),
#         "top_defensive_setups": [
#             {
#                 "agents": list(setup),
#                 "frequency": count,
#                 "win_rate": win_rates.get(''.join(setup), 0)
#             }
#             for setup, count in def_setups.most_common(5)
#         ],
#         "site_anchor_preferences": dict(site_anchors.most_common()),
#         "entry_fragger_agents": entry_agent_pref,
#         "analysis_date": "2026-02-02"
#     }
    
#     # Save JSON
#     output_file = f"{target_team.replace(' ', '_')}_compositions_analysis.json"
#     with open(output_file, 'w') as f:
#         json.dump(results, f, indent=2)
    
#     print(f"✅ SAVED: {output_file}")
#     print(f"\n🏆 TOP AGENTS: {dict(agent_picks.most_common(5))}")
#     print(f"🔒 TOP DEF SETUP: {results['top_defensive_setups'][0]['agents']}")
    
#     return results

# # ============================================================================
# # 🚀 BATCH PROCESS ALL 12 TEAMS
# # ============================================================================

# TEAMS = [
#     "100 Thieves", "2GAME eSports", "Cloud9", "Evil Geniuses", "FURIA", 
#     "G2", "KRÜ Esports", "Leviatán Esports", "LOUD", "MIBR", 
#     "NRG", "Sentinels"
# ]

# all_comps = {}
# for team in TEAMS:
#     print(f"\n🎯 Analyzing {team}...")
#     comps = analyze_team_compositions(team, n_series=20)
#     all_comps[team] = comps

# # Master analysis across all teams
# master_file = "valorant_12teams_compositions_analysis.json"
# with open(master_file, 'w') as f:
#     json.dump(all_comps, f, indent=2)

# print(f"\n✅ MASTER ANALYSIS: {master_file}")
# print(f"📊 12 teams × 6 composition features")

import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from datetime import datetime

class ValorantFeatureExtractor:
    """
    Comprehensive Valorant esports feature extraction
    Extracts: Agent picks, Site anchors, Defensive setups, Attack formations
    """
    
    def __init__(self, data_dir="/mnt/user-data/uploads"):
        self.data_dir = Path(data_dir)
        self.series_data = []
        self.load_all_series()
        
    def load_all_series(self):
        """Load all series JSON files"""
        series_files = sorted(self.data_dir.glob("series_*_raw.json"))
        print(f"🔍 Found {len(series_files)} series files")
        
        for path in series_files:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.series_data.append({
                        "id": path.stem.replace("series_", "").replace("_raw", ""),
                        "data": data,
                        "path": str(path)
                    })
            except Exception as e:
                print(f"⚠️  Error loading {path.name}: {e}")
        
        print(f"✅ Loaded {len(self.series_data)} series successfully\n")
    
    def get_game_agent_mapping(self, game_data):
        """Extract player->agent mapping from game level"""
        player_agents = {}
        team_agents = defaultdict(dict)
        
        for team in game_data.get("teams", []):
            team_name = team.get("name", "unknown")
            for player in team.get("players", []):
                if player.get("participationStatus") == "active":
                    character = player.get("character", {})
                    agent = character.get("name", "unknown")
                    player_name = player.get("name", "unknown")
                    player_agents[player_name] = agent
                    team_agents[team_name][player_name] = agent
        
        return player_agents, team_agents
    
    def extract_features(self):
        """Main feature extraction pipeline"""
        print("="*70)
        print("🎯 FEATURE EXTRACTION PIPELINE")
        print("="*70)
        
        # Initialize feature storage
        features = {
            "agent_picks": Counter(),
            "agent_picks_by_team": defaultdict(Counter),
            "agent_picks_by_map": defaultdict(Counter),
            "site_anchors": Counter(),
            "site_anchors_by_team": defaultdict(Counter),
            "defensive_setups": Counter(),
            "defensive_setups_by_team": defaultdict(Counter),
            "attack_setups": Counter(),
            "attack_setups_by_team": defaultdict(Counter),
            "player_agent_preferences": defaultdict(Counter),
            "player_teams": {},
            "rounds_analyzed": 0,
            "games_analyzed": 0,
            "teams_found": set(),
            "maps_played": Counter(),
            "agent_role_map": {},
            "site_anchor_details": defaultdict(lambda: {"total": 0, "kills": 0, "agents": Counter()}),
            "composition_win_rates": defaultdict(lambda: {"wins": 0, "total": 0})
        }
        
        # Process all series
        for series in self.series_data:
            series_id = series["id"]
            print(f"\n📊 Processing Series {series_id}...")
            
            for game in series["data"].get("seriesState", {}).get("games", []):
                features["games_analyzed"] += 1
                map_name = game.get("map", {}).get("name", "unknown")
                features["maps_played"][map_name] += 1
                
                # Get agent mappings for this game
                player_agents, team_agents = self.get_game_agent_mapping(game)
                
                # Process each round
                for segment in game.get("segments", []):
                    if segment.get("type") == "round" and segment.get("finished"):
                        features["rounds_analyzed"] += 1
                        
                        # Process each team in the round
                        for team in segment.get("teams", []):
                            team_name = team.get("name", "unknown")
                            features["teams_found"].add(team_name)
                            side = team.get("side", "unknown")
                            round_won = team.get("won", False)
                            
                            # Get team composition for this round
                            active_players = [p for p in team.get("players", []) 
                                            if p.get("participationStatus") == "active"]
                            
                            composition = []
                            for player in active_players:
                                player_name = player.get("name")
                                agent = player_agents.get(player_name, "unknown")
                                composition.append(agent)
                                
                                # Track player-team association
                                features["player_teams"][player_name] = team_name
                                
                                # 1️⃣ AGENT PICK FREQUENCY
                                features["agent_picks"][agent] += 1
                                features["agent_picks_by_team"][team_name][agent] += 1
                                features["agent_picks_by_map"][map_name][agent] += 1
                                features["player_agent_preferences"][player_name][agent] += 1
                            
                            # Sort composition for consistent comparison
                            sorted_comp = tuple(sorted(composition))
                            
                            # 2️⃣ DEFENSIVE SETUPS
                            if side == "defender":
                                features["defensive_setups"][sorted_comp] += 1
                                features["defensive_setups_by_team"][team_name][sorted_comp] += 1
                                
                                # Track composition win rates
                                comp_key = f"DEF:{','.join(sorted_comp)}"
                                features["composition_win_rates"][comp_key]["total"] += 1
                                if round_won:
                                    features["composition_win_rates"][comp_key]["wins"] += 1
                                
                                # 3️⃣ SITE ANCHOR IDENTIFICATION
                                # Find player with most kills on defense
                                if active_players:
                                    top_fragger = max(active_players, 
                                                    key=lambda p: p.get("kills", 0),
                                                    default=None)
                                    if top_fragger and top_fragger.get("kills", 0) > 0:
                                        anchor_name = top_fragger.get("name")
                                        anchor_kills = top_fragger.get("kills", 0)
                                        anchor_agent = player_agents.get(anchor_name, "unknown")
                                        
                                        features["site_anchors"][anchor_name] += 1
                                        features["site_anchors_by_team"][team_name][anchor_name] += 1
                                        
                                        # Detailed anchor stats
                                        features["site_anchor_details"][anchor_name]["total"] += 1
                                        features["site_anchor_details"][anchor_name]["kills"] += anchor_kills
                                        features["site_anchor_details"][anchor_name]["agents"][anchor_agent] += 1
                            
                            # 4️⃣ ATTACK-SIDE FORMATIONS
                            elif side == "attacker":
                                features["attack_setups"][sorted_comp] += 1
                                features["attack_setups_by_team"][team_name][sorted_comp] += 1
                                
                                # Track composition win rates
                                comp_key = f"ATK:{','.join(sorted_comp)}"
                                features["composition_win_rates"][comp_key]["total"] += 1
                                if round_won:
                                    features["composition_win_rates"][comp_key]["wins"] += 1
        
        # Post-processing
        features["teams_found"] = sorted(list(features["teams_found"]))
        
        print(f"\n✅ Feature extraction complete!")
        print(f"   📈 {features['rounds_analyzed']} rounds across {features['games_analyzed']} games")
        print(f"   🏆 {len(features['teams_found'])} teams found")
        print(f"   🗺️  {len(features['maps_played'])} maps played")
        
        return features
    
    def generate_report(self, features):
        """Generate comprehensive analysis report"""
        report = {
            "metadata": {
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_series": len(self.series_data),
                "total_games": features["games_analyzed"],
                "total_rounds": features["rounds_analyzed"],
                "teams_analyzed": features["teams_found"],
                "maps_played": dict(features["maps_played"])
            },
            
            # 1️⃣ AGENT PICK FREQUENCY
            "agent_pick_frequency": {
                "overall": dict(features["agent_picks"].most_common()),
                "top_10_agents": [
                    {
                        "agent": agent,
                        "picks": count,
                        "pick_rate": round(count / features["rounds_analyzed"] * 100, 2)
                    }
                    for agent, count in features["agent_picks"].most_common(10)
                ],
                "by_team": {
                    team: dict(agents.most_common())
                    for team, agents in features["agent_picks_by_team"].items()
                },
                "by_map": {
                    map_name: dict(agents.most_common(10))
                    for map_name, agents in features["agent_picks_by_map"].items()
                }
            },
            
            # 2️⃣ SITE ANCHOR PREFERENCES
            "site_anchor_preferences": {
                "overall_frequency": dict(features["site_anchors"].most_common()),
                "top_anchors": [
                    {
                        "player": player,
                        "anchor_rounds": count,
                        "anchor_rate": round(count / features["rounds_analyzed"] * 100, 2),
                        "avg_kills_per_anchor": round(features["site_anchor_details"][player]["kills"] / 
                                                      features["site_anchor_details"][player]["total"], 2),
                        "preferred_agents": dict(features["site_anchor_details"][player]["agents"].most_common(3))
                    }
                    for player, count in features["site_anchors"].most_common(15)
                ],
                "by_team": {
                    team: dict(anchors.most_common(5))
                    for team, anchors in features["site_anchors_by_team"].items()
                }
            },
            
            # 3️⃣ COMMON DEFENSIVE SETUPS
            "defensive_setups": {
                "top_compositions": [
                    {
                        "composition": list(comp),
                        "frequency": count,
                        "percentage": round(count / sum(features["defensive_setups"].values()) * 100, 2),
                        "win_rate": round(features["composition_win_rates"][f"DEF:{','.join(comp)}"]["wins"] / 
                                        features["composition_win_rates"][f"DEF:{','.join(comp)}"]["total"] * 100, 2)
                        if features["composition_win_rates"][f"DEF:{','.join(comp)}"]["total"] > 0 else 0
                    }
                    for comp, count in features["defensive_setups"].most_common(15)
                ],
                "by_team": {
                    team: [
                        {
                            "composition": list(comp),
                            "frequency": count,
                            "percentage": round(count / sum(setups.values()) * 100, 2)
                        }
                        for comp, count in setups.most_common(5)
                    ]
                    for team, setups in features["defensive_setups_by_team"].items()
                }
            },
            
            # 4️⃣ ATTACK-SIDE DEFAULT FORMATIONS
            "attack_formations": {
                "top_compositions": [
                    {
                        "composition": list(comp),
                        "frequency": count,
                        "percentage": round(count / sum(features["attack_setups"].values()) * 100, 2),
                        "win_rate": round(features["composition_win_rates"][f"ATK:{','.join(comp)}"]["wins"] / 
                                        features["composition_win_rates"][f"ATK:{','.join(comp)}"]["total"] * 100, 2)
                        if features["composition_win_rates"][f"ATK:{','.join(comp)}"]["total"] > 0 else 0
                    }
                    for comp, count in features["attack_setups"].most_common(15)
                ],
                "by_team": {
                    team: [
                        {
                            "composition": list(comp),
                            "frequency": count,
                            "percentage": round(count / sum(setups.values()) * 100, 2)
                        }
                        for comp, count in setups.most_common(5)
                    ]
                    for team, setups in features["attack_setups_by_team"].items()
                }
            },
            
            # 5️⃣ PLAYER AGENT POOLS
            "player_agent_pools": {
                player: {
                    "team": features["player_teams"].get(player, "unknown"),
                    "total_rounds": sum(agents.values()),
                    "agent_pool": [
                        {
                            "agent": agent,
                            "picks": count,
                            "pick_rate": round(count / sum(agents.values()) * 100, 2)
                        }
                        for agent, count in agents.most_common()
                    ]
                }
                for player, agents in features["player_agent_preferences"].items()
                if sum(agents.values()) >= 5  # Minimum 5 rounds
            }
        }
        
        return report
    
    def save_results(self, report):
        """Save analysis results to files"""
        output_dir = Path("/mnt/user-data/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full report as JSON
        json_file = output_dir / "valorant_feature_extraction_full.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Saved full report: {json_file}")
        
        # Save summary CSV files
        self.save_csv_summaries(report, output_dir)
        
        return json_file
    
    def save_csv_summaries(self, report, output_dir):
        """Save key features as CSV files for easy analysis"""
        
        # 1. Agent picks CSV
        if report["agent_pick_frequency"]["top_10_agents"]:
            agent_df = pd.DataFrame(report["agent_pick_frequency"]["top_10_agents"])
            agent_df.to_csv(output_dir / "agent_pick_frequency.csv", index=False)
        
        # 2. Site anchors CSV
        if report["site_anchor_preferences"]["top_anchors"]:
            anchor_df = pd.DataFrame(report["site_anchor_preferences"]["top_anchors"])
            anchor_df.to_csv(output_dir / "site_anchors.csv", index=False)
        
        # 3. Defensive compositions CSV
        if report["defensive_setups"]["top_compositions"]:
            def_df = pd.DataFrame(report["defensive_setups"]["top_compositions"])
            def_df['composition'] = def_df['composition'].apply(lambda x: ', '.join(x))
            def_df.to_csv(output_dir / "defensive_compositions.csv", index=False)
        
        # 4. Attack compositions CSV
        if report["attack_formations"]["top_compositions"]:
            atk_df = pd.DataFrame(report["attack_formations"]["top_compositions"])
            atk_df['composition'] = atk_df['composition'].apply(lambda x: ', '.join(x))
            atk_df.to_csv(output_dir / "attack_compositions.csv", index=False)
        
        print(f"📊 Saved CSV summaries:")
        print(f"   - agent_pick_frequency.csv")
        if report["site_anchor_preferences"]["top_anchors"]:
            print(f"   - site_anchors.csv")
        if report["defensive_setups"]["top_compositions"]:
            print(f"   - defensive_compositions.csv")
        if report["attack_formations"]["top_compositions"]:
            print(f"   - attack_compositions.csv")
    
    def print_summary(self, report):
        """Print key insights to console"""
        print("\n" + "="*70)
        print("📊 ANALYSIS SUMMARY")
        print("="*70)
        
        print("\n1️⃣  TOP 10 AGENT PICKS:")
        for item in report["agent_pick_frequency"]["top_10_agents"]:
            print(f"   {item['agent']:15} {item['picks']:4} picks ({item['pick_rate']:5.1f}%)")
        
        print("\n2️⃣  TOP 5 SITE ANCHORS:")
        for item in report["site_anchor_preferences"]["top_anchors"][:5]:
            print(f"   {item['player']:15} {item['anchor_rounds']:3} rounds ({item['anchor_rate']:4.1f}%) "
                  f"| Avg {item['avg_kills_per_anchor']:.1f} kills | {list(item['preferred_agents'].keys())[0]}")
        
        print("\n3️⃣  TOP 3 DEFENSIVE COMPOSITIONS:")
        for i, item in enumerate(report["defensive_setups"]["top_compositions"][:3], 1):
            agents = ', '.join(item['composition'])
            print(f"   {i}. {agents}")
            print(f"      Frequency: {item['frequency']} ({item['percentage']:.1f}%) | Win Rate: {item['win_rate']:.1f}%")
        
        print("\n4️⃣  TOP 3 ATTACK FORMATIONS:")
        for i, item in enumerate(report["attack_formations"]["top_compositions"][:3], 1):
            agents = ', '.join(item['composition'])
            print(f"   {i}. {agents}")
            print(f"      Frequency: {item['frequency']} ({item['percentage']:.1f}%) | Win Rate: {item['win_rate']:.1f}%")
        
        print("\n" + "="*70)


# ============================================================================
# 🚀 MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎮 VALORANT ESPORTS FEATURE EXTRACTOR")
    print("="*70 + "\n")
    
    # Initialize extractor
    extractor = ValorantFeatureExtractor()
    
    # Extract features
    features = extractor.extract_features()
    
    # Generate report
    report = extractor.generate_report(features)
    
    # Print summary
    extractor.print_summary(report)
    
    # Save results
    output_file = extractor.save_results(report)
    
    print("\n✅ Analysis complete! Check output files for detailed results.")
    print("="*70 + "\n")