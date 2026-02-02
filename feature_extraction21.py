# import pandas as pd
# import json
# from typing import Dict, List

# def quantitative_to_qualitative(csv_files, output_file="pro_player_qualitative_analysis.json"):
#     """
#     Convert your quantitative rankings → Rich qualitative LLM analysis
#     """
    
#     # Thresholds for qualitative assessment (Valorant pro-level)
#     QUALITY_TIERS = {
#         'elite': 0.85,      # Top 1%
#         'excellent': 0.75,  # Top 5%
#         'strong': 0.65,     # Top 15%
#         'average': 0.50,    # Roster standard
#         'developing': 0.35  # Needs work
#     }
    
#     def score_to_qualitative(score: float, metric: str) -> str:
#         """Convert raw score → Descriptive qualitative label"""
#         if metric in ['entry_attempts_per_round', 'duel_win_pct', 'headshot_pct', 'clutch_rate']:
#             threshold = QUALITY_TIERS['elite'] if score > 0.75 else \
#                        QUALITY_TIERS['excellent'] if score > 0.65 else \
#                        QUALITY_TIERS['strong'] if score > 0.50 else \
#                        QUALITY_TIERS['average']
#         elif metric == 'kd_by_site':
#             threshold = 1.4 if score > 1.4 else \
#                        1.2 if score > 1.2 else \
#                        1.0 if score > 1.0 else \
#                        0.8
#             return f"{threshold:.1f} K/D {'🔥 Elite' if score > 1.4 else '⚡ Strong' if score > 1.2 else '✅ Solid' if score > 1.0 else '📈 Developing'}"
#         elif metric == 'dmg_per_round':
#             return f"{int(score)} DPR {'🏆 Carry' if score > 140 else '💪 Main Damage' if score > 110 else '⚙️ Support' if score > 90 else '📊 Utility'}"
        
#         tier = 'elite' if score > QUALITY_TIERS['elite'] else \
#                'excellent' if score > QUALITY_TIERS['excellent'] else \
#                'strong' if score > QUALITY_TIERS['strong'] else \
#                'average' if score > QUALITY_TIERS['average'] else 'developing'
#         return tier.title()
    
#     def generate_player_profile(row) -> Dict:
#         """Create rich qualitative player assessment"""
#         return {
#             "name": row["player_name"],
#             "role": "Entry Fragger" if row["entry_attempts_per_round"] > 0.70 else \
#                    "Duelist" if row["duel_win_pct"] > 0.55 else \
#                    "Anchor/Support" if row["post_plant_kd"] > 1.1 else "Flex",
            
#             "strengths": [
#                 f"Entry aggression ({row['entry_attempts_per_round']:.1%})" if row["entry_attempts_per_round"] > 0.65 else "",
#                 f"Clean duels ({row['duel_win_pct']:.1%})" if row['duel_win_pct'] > 0.55 else "",
#                 f"Laser aim ({row['headshot_pct']:.1%} HS%)" if row['headshot_pct'] > 0.45 else "",
#                 f"Clutch god ({row['clutch_rate']:.1%})" if row['clutch_rate'] > 0.9 else ""
#             ],
#             "qualitative_assessment": {
#                 "aim": score_to_qualitative(row['headshot_pct'], 'headshot_pct'),
#                 "dueling": score_to_qualitative(row['duel_win_pct'], 'duel_win_pct'),
#                 "entry_fragging": score_to_qualitative(row['entry_attempts_per_round'], 'entry_attempts_per_round'),
#                 "site_hold": score_to_qualitative(row['kd_by_site'], 'kd_by_site'),
#                 "post_plant": score_to_qualitative(row['post_plant_kd'], 'kd_by_site'),
#                 "damage_output": score_to_qualitative(row['dmg_per_round'], 'dmg_per_round'),
#                 "clutch_factor": score_to_qualitative(row['clutch_rate'], 'clutch_rate')
#             },
#             "raw_metrics": {k: float(v) for k, v in row.items() if k != "player_name"}
#         }
    
#     all_teams = {}
    
#     for csv_file in csv_files:
#         df = pd.read_csv(csv_file)
#         team_name = csv_file.replace("_pro_player_rankings.csv", "").replace("_", " ")
        
#         # Convert each player to qualitative profile
#         players = [generate_player_profile(row) for _, row in df.iterrows()]
        
#         # Team-level qualitative summary
#         team_summary = {
#             "playstyle": "Aggressive Entry" if sum(p['raw_metrics']['entry_attempts_per_round'] for p in players)/len(players) > 0.70 else \
#                         "Balanced Duelists" if sum(p['raw_metrics']['duel_win_pct'] for p in players)/len(players) > 0.55 else \
#                         "Post-Plant Heavy",
#             "key_strength": max(players, key=lambda p: p['raw_metrics']['entry_attempts_per_round'])['name'] + " leads entries",
#             "weakness": "Early deaths" if any(p['raw_metrics']['deaths_first_20s'] > 0.1 for p in players) else "Clutch consistency",
#             "players": players
#         }
        
#         all_teams[team_name] = team_summary
    
#     # LLM-ready qualitative JSON
#     qualitative_json = {
#         "esports_analysis": {
#             "type": "Professional Valorant Player Evaluation",
#             "teams_assessed": len(all_teams),
#             "assessment_date": "2026-02-02",
#             "evaluation_focus": "Player roles, strengths, playstyle classification"
#         },
#         "team_profiles": all_teams,
#         "cross_team_comparison": {
#             "most_aggressive": max(all_teams.keys(), key=lambda t: sum(p['raw_metrics']['entry_attempts_per_round'] 
#                                                                     for p in all_teams[t]['players'])/len(all_teams[t]['players'])),
#             "best_duelists": max(all_teams.keys(), key=lambda t: max(p['raw_metrics']['duel_win_pct'] 
#                                                                    for p in all_teams[t]['players']))
#         }
#     }
    
#     # Save qualitative analysis
#     with open(output_file, 'w') as f:
#         json.dump(qualitative_json, f, indent=2)
    
#     print(f"✅ QUALITATIVE ANALYSIS SAVED: {output_file}")
#     print(f"📊 {len(all_teams)} teams fully assessed")
    
#     return qualitative_json

# # ============================================================================
# # 🚀 EXECUTE FOR YOUR FILES
# # ============================================================================

# CSV_FILES = [
#     "100_Thieves_pro_player_rankings.csv",
#     "2GAME_eSports_pro_player_rankings.csv",
#     "Cloud9_pro_player_rankings.csv",
#     "Evil_Geniuses_pro_player_rankings.csv",
#     "FURIA_pro_player_rankings.csv",
#     "G2_pro_player_rankings.csv",
#     "KRÜ_Esports_pro_player_rankings.csv",
#     "Leviatán_Esports_pro_player_rankings.csv",
#     "LOUD_pro_player_rankings.csv",
#     "MIBR_pro_player_rankings.csv",
#     "NRG_pro_player_rankings.csv",
#     "Sentinels_pro_player_rankings.csv"
# ]

# # 🏁 GENERATE QUALITATIVE JSON
# qualitative_analysis = quantitative_to_qualitative(CSV_FILES)

# # 🎯 SAMPLE OUTPUT PREVIEW
# print("\n📋 SAMPLE QUALITATIVE JSON:")
# print(json.dumps(qualitative_analysis["team_profiles"]["100 Thieves"], indent=2)[:800] + "...")



###################################################################################################################3



import pandas as pd
import json
import os

def quantitative_to_qualitative(csv_files=None, output_file="pro_player_qualitative_analysis.json"):
    """Convert ALL 12 CSVs → LLM-ready qualitative JSON"""
    
    # AUTO-FIND your 12 CSV files
    if csv_files is None:
        csv_files = [f for f in os.listdir('.') if f.endswith('_pro_player_rankings.csv')]
    print(f"🔍 Found {len(csv_files)} CSV files")
    
    all_teams = {}
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"⚠️  Skipping: {csv_file}")
            continue
            
        try:
            df = pd.read_csv(csv_file)
            team_name = csv_file.replace("_pro_player_rankings.csv", "").replace("_", " ")
            
            players = []
            entry_rates = []
            
            for _, row in df.iterrows():
                # FIXED role classification (Valorant pro standards)
                entry_rate = row['entry_attempts_per_round']
                duel_pct = row['duel_win_pct']
                post_kd = row['post_plant_kd']
                
                role = ("Entry Fragger" if entry_rate > 0.72 else 
                       "Duelist" if duel_pct > 0.52 else 
                       "Anchor" if post_kd > 1.15 else "Flex")
                
                # FIXED strengths (no empties)
                strengths = []
                if entry_rate > 0.65: strengths.append(f"Entry: {entry_rate:.0%}")
                if duel_pct > 0.50: strengths.append(f"Duelist: {duel_pct:.0%}") 
                if row['headshot_pct'] > 0.45: strengths.append(f"HS%: {row['headshot_pct']:.0%}")
                if row['kd_by_site'] > 1.1: strengths.append(f"Site KD: {row['kd_by_site']:.1f}")
                
                players.append({
                    "name": row["player_name"],
                    "role": role,
                    "strengths": strengths or ["Versatile contributor"],
                    "stats": {
                        "entry": f"{entry_rate:.0%}",
                        "duels": f"{duel_pct:.0%}", 
                        "kd_site": f"{row['kd_by_site']:.1f}",
                        "dpr": f"{int(row['dmg_per_round'])}"
                    }
                })
                entry_rates.append(entry_rate)
            
            # Team analysis
            avg_entry = sum(entry_rates) / len(entry_rates)
            playstyle = "Aggressive" if avg_entry > 0.70 else "Balanced" if avg_entry > 0.60 else "Methodical"
            
            all_teams[team_name] = {
                "playstyle": playstyle,
                "avg_entry_rate": f"{avg_entry:.0%}",
                "star_entry": max(players, key=lambda p: float(p['stats']['entry'][:-1]))['name'],
                "players": players
            }
            
            print(f"✅ {team_name}: {len(players)} players")
            
        except Exception as e:
            print(f"❌ {csv_file}: {e}")
    
    # Final JSON structure
    result = {
        "valorant_analysis": {
            "teams": len(all_teams),
            "players_total": sum(len(t["players"]) for t in all_teams.values()),
            "date": "2026-02-02"
        },
        "teams": all_teams
    }
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ SUCCESS: {output_file}")
    print(f"📊 {len(all_teams)} teams processed")
    
    return result

# 🏁 RUN IT (handles missing files automatically)
CSV_FILES = [  # Your actual 12 files
    "100_Thieves_pro_player_rankings.csv",
    "2GAME_eSports_pro_player_rankings.csv",
    "Cloud9_pro_player_rankings.csv",
    "Evil_Geniuses_pro_player_rankings.csv",
    "FURIA_pro_player_rankings.csv",
    "G2_pro_player_rankings.csv",
    "KRÜ_Esports_pro_player_rankings.csv",
    "Leviatán_Esports_pro_player_rankings.csv",
    "LOUD_pro_player_rankings.csv",
    "MIBR_pro_player_rankings.csv",
    "NRG_pro_player_rankings.csv",
    "Sentinels_pro_player_rankings.csv"
]

qualitative_analysis = quantitative_to_qualitative(CSV_FILES)

