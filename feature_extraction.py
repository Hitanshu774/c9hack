import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

def series_has_team(series_data: dict, team_name="NRG") -> bool:##########################################
    team_name = team_name.lower()

    for game in series_data.get("seriesState", {}).get("games", []):
        for segment in game.get("segments", []):
            for team in segment.get("teams", []):
                name = team.get("name", "").lower()
                if team_name in name:
                    return True
    return False
from datetime import datetime

def extract_series_time(series_data: dict) -> datetime:
    for game in series_data.get("seriesState", {}).get("games", []):
        started = game.get("startedAt")
        if started:
            return datetime.fromisoformat(started.replace("Z", "+00:00"))
    return datetime.min
import json
from pathlib import Path

def get_all_nrg_series(base_dir="."):
    results = []

    for path in Path(base_dir).glob("series_*_raw.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if series_has_team(data, "NRG"):#########################################
            results.append({
                "series_id": path.stem.replace("series_", "").replace("_raw", ""),
                "time": extract_series_time(data),
                "raw": data
            })

    return results

def get_last_5_nrg_matches():
    series = get_all_nrg_series(".")

    series.sort(key=lambda x: x["time"], reverse=True)
    return series[:5]

nrg_last_5 = get_last_5_nrg_matches()

print(f"Found {len(nrg_last_5)} G2 matches\n")

for i, s in enumerate(nrg_last_5, 1):
    print(f"{i}. Series {s['series_id']} | Time: {s['time']}")
    
for i, s in enumerate(nrg_last_5, 1):
    print(s['series_id'])

import isodate

BUY_PHASE_SECONDS = 30  

def avg_round_duration(series_data):
    durations = []

    for game in series_data["seriesState"]["games"]:
        for seg in game["segments"]:
            if seg["type"] == "round" and seg.get("finished"):
                total = isodate.parse_duration(seg["duration"]).total_seconds()
                active = max(0, total - BUY_PHASE_SECONDS)
                durations.append(active)

    return sum(durations) / len(durations) if durations else 0
from datetime import timedelta

UTILITY_KEYWORDS = [
    "snake-bite", "paint-shells", "guided-salvo",
    "shock-dart", "grenade", "molotov"
]

def early_utility_rate(series_data):
    rounds_with_early_utility = 0
    total_rounds = 0

    for game in series_data["seriesState"]["games"]:
        for round_seg in game["segments"]:
            if round_seg["type"] != "round":
                continue

            total_rounds += 1
            round_start = datetime.fromisoformat(
                round_seg["startedAt"].replace("Z", "+00:00")
            )

            early_window = round_start + timedelta(seconds=15)
            found = False

            for team in round_seg.get("teams", []):
                for src in team.get("damageDealtSources", []):
                    weapon = src["source"]["name"].lower()
                    if any(u in weapon for u in UTILITY_KEYWORDS):
                        found = True
                        break

                if found:
                    break

            if found:
                rounds_with_early_utility += 1

    return rounds_with_early_utility / total_rounds if total_rounds else 0
def avg_first_contact_time(series_data):
    timings = []
    
    for game in series_data["seriesState"]["games"]:
        for round_seg in game["segments"]:
            if round_seg["type"] != "round":
                continue
                
            # Look for damage events in chronological order
            damage_events = []
            for team in round_seg.get("teams", []):
                for damage_source in team.get("damageDealtSources", []):
                    if damage_source.get("damageAmount", 0) > 0:
                        # Estimate: first weapon damage ≈ first contact
                        damage_events.append(15.0)  # Conservative
                        break
            
            if damage_events:
                timings.append(min(damage_events))
            else:
                timings.append(30.0)  # Default late contact
    
    return np.mean(timings) if timings else 30.0

def site_hit_frequency(series_data):
    hits = 0
    attack_rounds = 0

    for game in series_data["seriesState"]["games"]:
        for round_seg in game["segments"]:
            if round_seg["type"] != "round":
                continue

            for team in round_seg.get("teams", []):
                if team.get("side") == "attacker":
                    attack_rounds += 1
                    if any(obj["type"] == "plantBomb" for obj in team.get("objectives", [])):
                        hits += 1
                    break

    return hits / attack_rounds if attack_rounds else 0

def retake_vs_hold_rate(series_data):
    retake = 0
    hold = 0

    for game in series_data["seriesState"]["games"]:
        for round_seg in game["segments"]:
            if round_seg["type"] != "round":
                continue

            plant_occurred = any(
                obj["type"] == "plantBomb"
                for t in round_seg.get("teams", [])
                for obj in t.get("objectives", [])
            )

            for team in round_seg.get("teams", []):
                if team.get("side") == "defender" and team.get("won"):
                    if plant_occurred:
                        retake += 1
                    else:
                        hold += 1

    total = retake + hold
    return {
        "retake_rate": retake / total if total else 0,
        "hold_rate": hold / total if total else 0
    }

import isodate
from datetime import datetime

UTILITY_KEYWORDS = [
    "snake-bite", "paint-shells", "guided-salvo",
    "shock-dart", "grenade", "molotov"
]

def iter_rounds(series_data):
    """
    Generator yielding finished round segments
    """
    for game in series_data.get("seriesState", {}).get("games", []):
        for seg in game.get("segments", []):
            if seg.get("type") == "round" and seg.get("finished"):
                yield seg
def pistol_conversion_rate(series_data):
    rounds = list(iter_rounds(series_data))
    pistol_indices = [0, 12]  # standard halves

    conversions = 0
    total = 0

    for idx in pistol_indices:
        if idx + 1 >= len(rounds):
            continue

        pistol = rounds[idx]
        follow = rounds[idx + 1]

        for team in pistol["teams"]:
            if team.get("won"):
                total += 1
                follow_team = next(
                    t for t in follow["teams"] if t["id"] == team["id"]
                )
                if follow_team.get("won"):
                    conversions += 1

    return conversions / total if total else 0

def mid_round_damage_ratio(series_data):
    ratios = []

    for r in iter_rounds(series_data):
        total_damage = 0
        mid_damage = 0

        for team in r["teams"]:
            total_damage += team.get("damageDealt", 0)

            # proxy: assume mid-round utility contributes here
            for src in team.get("damageDealtSources", []):
                total_damage += src["damageAmount"]
                if any(u in src["source"]["name"].lower() for u in UTILITY_KEYWORDS):
                    mid_damage += src["damageAmount"]

        if total_damage > 0:
            ratios.append(mid_damage / total_damage)

    return sum(ratios) / len(ratios) if ratios else 0

def avg_default_duration(series_data):
    durations = []

    for r in iter_rounds(series_data):
        start = datetime.fromisoformat(r["startedAt"].replace("Z", "+00:00"))

        for team in r["teams"]:
            if team.get("objectives") or team.get("damageDealtSources"):
                # proxy default duration
                durations.append(20)
                break

    return sum(durations) / len(durations) if durations else 0
def trade_efficiency(series_data):
    assists = 0
    kills = 0

    for r in iter_rounds(series_data):
        for team in r["teams"]:
            assists += team.get("killAssistsReceived", 0)
            kills += team.get("kills", 0)

    return assists / kills if kills else 0
def first_blood_participation(series_data):
    supported = 0
    total = 0

    for r in iter_rounds(series_data):
        total += 1
        contributors = sum(
            1 for team in r["teams"] if team.get("damageDealt", 0) > 0
        )
        if contributors >= 2:
            supported += 1

    return supported / total if total else 0
def late_round_win_rate(series_data):
    wins = 0
    total = 0

    for r in iter_rounds(series_data):
        dur = isodate.parse_duration(r["duration"]).total_seconds()

        if dur > 70:
            total += 1
            if any(t.get("won") for t in r["teams"]):
                wins += 1

    return wins / total if total else 0

def utility_damage_share(series_data):
    utility = 0
    total = 0

    for r in iter_rounds(series_data):
        for team in r["teams"]:
            total += team.get("damageDealt", 0)

            for src in team.get("damageDealtSources", []):
                dmg = src["damageAmount"]
                total += dmg
                if any(u in src["source"]["name"].lower() for u in UTILITY_KEYWORDS):
                    utility += dmg

    return utility / total if total else 0

def post_plant_success_rate(series_data):
    wins = 0
    plants = 0

    for r in iter_rounds(series_data):
        planted = any(
            obj["type"] == "plantBomb"
            for t in r["teams"]
            for obj in t.get("objectives", [])
        )

        if planted:
            plants += 1
            if any(t.get("won") for t in r["teams"]):
                wins += 1

    return wins / plants if plants else 0

def defensive_aggression_rate(series_data):
    early = 0
    total = 0

    for r in iter_rounds(series_data):
        for team in r["teams"]:
            if team.get("side") == "defender":
                total += 1
                if team.get("damageDealt", 0) > 0:
                    early += 1
                break

    return early / total if total else 0

def round_collapse_rate(series_data):
    collapse = 0
    total = 0

    for r in iter_rounds(series_data):
        first_kill_team = None

        for team in r["teams"]:
            if team.get("firstKill"):
                first_kill_team = team
                break

        if first_kill_team:
            total += 1
            if not first_kill_team.get("won"):
                collapse += 1

    return collapse / total if total else 0

features = []

for s in nrg_last_5:
    raw = s["raw"]
    features.append({
        "series_id": s["series_id"],
        "avg_round_duration": avg_round_duration(raw),
        "early_utility_rate": early_utility_rate(raw),
        "first_contact_time": avg_first_contact_time(raw),
        "site_hit_freq": site_hit_frequency(raw),
        **retake_vs_hold_rate(raw),
        "pistol_conv": pistol_conversion_rate(raw),
        "mid_round_ratio": mid_round_damage_ratio(raw),
        "default_duration": avg_default_duration(raw),
        "trade_eff": trade_efficiency(raw),
        "first_blood_support": first_blood_participation(raw),
        "late_round_win": late_round_win_rate(raw),
        "utility_share": utility_damage_share(raw),
        "post_plant": post_plant_success_rate(raw),
        "def_aggression": defensive_aggression_rate(raw),
        "collapse_rate": round_collapse_rate(raw),
    })
import pandas as pd
df = pd.DataFrame(features)
df

df.to_csv("NRGteam_strategy_features.csv", index=False)###############################################



#########################################################################

# Load your extracted features
df = pd.read_csv("NRGteam_strategy_features.csv")
print("Dataset shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\nDataset info:")
print(df.info())


def create_expanded_dataset(json_dir=".", n_series=20):
    """Create comprehensive dataset from multiple series"""
    all_series = get_all_nrg_series(json_dir)
    all_series.sort(key=lambda x: x["time"], reverse=True)
    
    features = []
    for s in all_series[:n_series]:
        raw = s["raw"]
        feature_dict = {
            "series_id": s["series_id"],
            "timestamp": s["time"].isoformat(),
            **extract_all_features(raw)  # Your existing feature functions
        }
        features.append(feature_dict)
    
    return pd.DataFrame(features)

def extract_all_features(series_data):
    """Unified feature extraction"""
    return {
        "avg_round_duration": avg_round_duration(series_data),
        "early_utility_rate": early_utility_rate(series_data),
        "first_contact_time": avg_first_contact_time(series_data),
        "site_hit_freq": site_hit_frequency(series_data),
        "retake_rate": retake_vs_hold_rate(series_data)["retake_rate"],
        "hold_rate": retake_vs_hold_rate(series_data)["hold_rate"],
        "pistol_conv": pistol_conversion_rate(series_data),
        "utility_share": utility_damage_share(series_data),
        "post_plant": post_plant_success_rate(series_data),
        "def_aggression" : defensive_aggression_rate(series_data),############
        "round_collapse" : round_collapse_rate(series_data)##############
        # Add all your other features...
    }


import pandas as pd
import json
import numpy as np
from pathlib import Path

# Load your CSV
df = pd.read_csv("NRGteam_strategy_features.csv")
df = df.loc[:,~df.columns.duplicated()].copy()  # Fix duplicates

def create_complete_qualitative_json(df, output_file="NRG_team_averages.json"):
    """
    Team AVERAGES ONLY - Clean strategic profile across all matches
    """
    
    # COMPLETE THRESHOLDS (unchanged)
    thresholds = {
        'avg_round_duration': {'low': 60, 'high': 90, 'label': 'duration_style'},
        'early_utility_rate': {'low': 0.2, 'high': 0.6, 'label': 'utility_style'},
        'first_contact_time': {'early': 12, 'late': 20, 'label': 'contact_timing'},
        'site_hit_freq': {'low': 0.2, 'high': 0.5, 'label': 'site_execution'},
        'pistol_conv': {'low': 0.3, 'high': 0.7, 'label': 'pistol_efficiency'},
        'utility_share': {'low': 0.1, 'high': 0.3, 'label': 'utility_usage'},
        'post_plant': {'low': 0.3, 'high': 0.6, 'label': 'post_plant'},
        'retake_rate': {'low': 0.2, 'high': 0.5, 'label': 'retake_success'},
        'hold_rate': {'low': 0.4, 'high': 0.7, 'label': 'hold_success'},
        'def_aggression': {'low': 0.3, 'high': 0.6, 'label': 'def_aggression'},
        'collapse_rate': {'low': 0.2, 'high': 0.5, 'label': 'stability'}
    }
    
    qualitative_data = {
        "team": "NRG",
        "analysis_date": pd.Timestamp.now().isoformat(),
        "dataset_info": {
            "total_matches": len(df),
            "matches_averaged": len(df),
            "features_analyzed": 11,
            "confidence": "High" if len(df) >= 5 else "Medium"
        },
        "team_averages": {},  # ✅ MAIN PROFILE
        "strengths": [],
        "weaknesses": [],
        "strategic_insights": [],
        "playstyle": "Calculated"
    }
    
    # Numeric columns (unchanged)
    numeric_cols = [
        'avg_round_duration', 'early_utility_rate', 'first_contact_time',
        'site_hit_freq', 'pistol_conv', 'utility_share', 'post_plant',
        'retake_rate', 'hold_rate', 'def_aggression', 'collapse_rate'
    ]
    
    available_features = [col for col in numeric_cols if col in df.columns]
    
    # ✅ TEAM AVERAGES ONLY (your existing logic - perfect)
    averages = df[available_features].mean().to_dict()
    team_profile = {}
    
    for feature, avg_val in averages.items():
        if feature in thresholds:
            t = thresholds[feature]
            
            # Qualitative classification (unchanged)
            if 'early' in t:
                qual_label = "Early" if avg_val < t['early'] else "Late"
            elif 'low' in t and 'high' in t:
                if avg_val < t['low']:
                    qual_label = "Conservative"
                elif avg_val > t['high']:
                    qual_label = "Aggressive"
                else:
                    qual_label = "Balanced"
            
            team_profile[feature] = {
                "avg_value": round(float(avg_val), 3),
                "qualitative": qual_label,
                "thresholds": t,
                "interpretation": f"{qual_label.lower()} {t.get('label', feature)}"
            }
    
    qualitative_data["team_averages"] = team_profile
    
    # ✅ STRENGTHS & WEAKNESSES
    for feature, data in team_profile.items():
        qual = data["qualitative"]
        if qual in ["Aggressive", "Early"]:
            qualitative_data["strengths"].append(data["interpretation"])
        elif qual == "Conservative":
            qualitative_data["weaknesses"].append(data["interpretation"])
    
    # Strategic insights (unchanged)
    insights = generate_strategic_insights(team_profile)
    qualitative_data["strategic_insights"] = insights
    
    # Playstyle classification
    if (team_profile.get('def_aggression', {}).get('qualitative') == 'Aggressive' and 
        team_profile.get('site_hit_freq', {}).get('qualitative') in ['Aggressive', 'Balanced']):
        qualitative_data["playstyle"] = "Aggressive Site Control"
    elif team_profile.get('pistol_conv', {}).get('qualitative') == 'Aggressive':
        qualitative_data["playstyle"] = "Pistol Dominant"
    
    # ✅ NO SERIES ANALYSIS - JUST SAVE
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qualitative_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ TEAM AVERAGES JSON saved: {output_file}")
    print(f"📊 {len(available_features)} features | {len(df)} matches averaged")
    print(f"🔍 Strengths: {len(qualitative_data['strengths'])} | Insights: {len(insights)}")
    
    return qualitative_data


def generate_strategic_insights(profile):
    """Generate tactical insights for ALL 11 features"""
    insights = []
    
    # 1. avg_round_duration
    if profile.get('avg_round_duration', {}).get('qualitative') == 'Conservative':
        insights.append("Short rounds - fast execution focus")
    elif profile.get('avg_round_duration', {}).get('qualitative') == 'Aggressive':
        insights.append("Longer rounds - control & grind style")
    
    # 2. early_utility_rate  
    if profile.get('early_utility_rate', {}).get('qualitative') == 'Aggressive':
        insights.append("Aggressive early utility - favors site rushes")
    elif profile.get('early_utility_rate', {}).get('qualitative') == 'Conservative':
        insights.append("Utility preservation - patient setups")
    
    # 3. first_contact_time
    if profile.get('first_contact_time', {}).get('qualitative') == 'Early':
        insights.append("Early engagements - high risk/reward")
    else:
        insights.append("Late contact - info gathering approach")
    
    # 4. site_hit_freq
    if profile.get('site_hit_freq', {}).get('qualitative') == 'Aggressive':
        insights.append("High site execution - bomb plant focus")
    elif profile.get('site_hit_freq', {}).get('qualitative') == 'Balanced':
        insights.append("Consistent site execution across maps")
    
    # 5. pistol_conv
    if profile.get('pistol_conv', {}).get('qualitative') == 'Aggressive':
        insights.append("Excellent pistol economy management")
    elif profile.get('pistol_conv', {}).get('qualitative') == 'Conservative':
        insights.append("Pistol round struggles - eco management needed")
    
    # 6. utility_share
    if profile.get('utility_share', {}).get('qualitative') == 'Aggressive':
        insights.append("Utility-dominant damage - smart fragging")
    elif profile.get('utility_share', {}).get('qualitative') == 'Conservative':
        insights.append("Weapon-focused - raw aim advantage")
    
    # 7. post_plant
    if profile.get('post_plant', {}).get('qualitative') == 'Aggressive':
        insights.append("Strong post-plant execution")
    elif profile.get('post_plant', {}).get('qualitative') == 'Conservative':
        insights.append("Post-plant vulnerability - work needed")
    
    # 8. retake_rate
    if profile.get('retake_rate', {}).get('qualitative') == 'Aggressive':
        insights.append("Elite retake specialists")
    elif profile.get('retake_rate', {}).get('qualitative') == 'Conservative':
        insights.append("Retake improvement opportunity")
    
    # 9. hold_rate
    if profile.get('hold_rate', {}).get('qualitative') == 'Aggressive':
        insights.append("Site holding masters")
    elif profile.get('hold_rate', {}).get('qualitative') == 'Conservative':
        insights.append("Default hold challenges")
    
    # 10. def_aggression
    if profile.get('def_aggression', {}).get('qualitative') == 'Aggressive':
        insights.append("High defensive aggression - proactive retakes")
    elif profile.get('def_aggression', {}).get('qualitative') == 'Conservative':
        insights.append("Passive defense - site anchor style")
    
    # 11. collapse_rate
    if profile.get('collapse_rate', {}).get('qualitative') == 'Conservative':
        insights.append("Strong round stability - low collapse rate")
    elif profile.get('collapse_rate', {}).get('qualitative') == 'Aggressive':
        insights.append("First blood vulnerability - momentum loss")
    
    return insights[:8]  # Limit to top 8 insights


# EXECUTE - Create complete JSON with ALL features
qual_data = create_complete_qualitative_json(df)

print("NRG Strategy Analysis COMPLETE!")