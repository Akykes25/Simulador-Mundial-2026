"""
main.py
Entry point for the World Cup 2026 Simulator.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time

import numpy as np
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)


def load_groups_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def banner() -> None:
    print(f"\n{Fore.YELLOW}{'='*65}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   ██╗    ██╗ ██████╗    ██████╗ ██████╗ ██████╗  ██████╗ {Style.RESET_ALL}")
    print(f"{Fore.GREEN}        SIMULADOR MUNDIAL 2026{Style.RESET_ALL}")
    print(f"{Fore.CYAN}        FIFA World Cup 2026 — USA / Mexico / Canada{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*65}{Style.RESET_ALL}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Simulador Mundial 2026 — Monte Carlo World Cup Simulator"
    )
    parser.add_argument(
        "--simulations", "-n", type=int, default=10000,
        help="Number of Monte Carlo simulations (default: 10000)"
    )
    parser.add_argument(
        "--quick", "-q", action="store_true",
        help="Run only 100 simulations (quick test mode)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Disable colorized output"
    )
    parser.add_argument(
        "--groups-file", type=str, default=None,
        help="Path to groups JSON file (default: data/groups_2026.json)"
    )
    args = parser.parse_args()

    n_sims = 100 if args.quick else args.simulations

    banner()
    print(f"  Simulations : {n_sims:,}")
    if args.seed is not None:
        print(f"  Seed        : {args.seed}")
        np.random.seed(args.seed)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ── 1. Load rankings (with web fallback) ─────────────────────────────────
    print(f"\n{Fore.CYAN}[1/5] Loading FIFA rankings...{Style.RESET_ALL}")
    try:
        from fetchers.fifa_data import fetch_fifa_rankings
        rankings = fetch_fifa_rankings()
        print(f"      Rankings loaded for {len(rankings)} teams.")
    except Exception as e:
        print(f"      Warning: {e} — using fallback rankings.")
        from config import FALLBACK_FIFA_RANKINGS
        rankings = dict(FALLBACK_FIFA_RANKINGS)

    # ── 2. Build Team objects ─────────────────────────────────────────────────
    print(f"\n{Fore.CYAN}[2/5] Building team profiles...{Style.RESET_ALL}")
    from analyzers.team_analyzer import build_all_teams
    all_teams = build_all_teams(rankings)
    print(f"      Built {len(all_teams)} team profiles.")

    # Show top 5 teams by strength
    top5 = sorted(all_teams.values(), key=lambda t: t.overall_strength, reverse=True)[:5]
    print(f"      Top 5 by strength: {', '.join(f'{t.name}({t.overall_strength:.1f})' for t in top5)}")

    # ── 3. Load groups ────────────────────────────────────────────────────────
    print(f"\n{Fore.CYAN}[3/5] Loading group assignments...{Style.RESET_ALL}")
    groups_path = args.groups_file or os.path.join(base_dir, "data", "groups_2026.json")
    raw_groups = load_groups_json(groups_path)
    group_data = raw_groups.get("groups", raw_groups)

    groups: dict = {}
    missing_teams = []
    for group_name, team_names in group_data.items():
        group_teams = []
        for name in team_names:
            if name in all_teams:
                group_teams.append(all_teams[name])
            else:
                missing_teams.append(name)
                # Create a generic team for missing entries
                from models.team import Team as TeamClass
                generic = TeamClass(
                    name=name, fifa_code=name[:3].upper(),
                    fifa_points=900.0, fifa_rank=50,
                    confederation="UEFA", overall_strength=40.0,
                )
                group_teams.append(generic)
        groups[group_name] = group_teams

    total_teams = sum(len(t) for t in groups.values())
    print(f"      {len(groups)} groups loaded, {total_teams} team slots.")
    if missing_teams:
        print(f"      Warning: {len(missing_teams)} teams not in rankings: {missing_teams}")

    # ── 4. Run Monte Carlo ────────────────────────────────────────────────────
    print(f"\n{Fore.CYAN}[4/5] Running {n_sims:,} tournament simulations...{Style.RESET_ALL}")
    t0 = time.time()
    from engine.monte_carlo import run_monte_carlo
    mc_results = run_monte_carlo(groups, n=n_sims, verbose=True, seed=args.seed)
    elapsed = time.time() - t0
    print(f"\n      Completed in {elapsed:.1f}s ({n_sims/elapsed:.0f} sims/sec)")

    # ── 5. Run one final simulation for group stage display ───────────────────
    print(f"\n{Fore.CYAN}[5/5] Generating report...{Style.RESET_ALL}")
    last_group_standings = None
    try:
        from simulator.tournament_simulator import simulate_tournament
        final_result = simulate_tournament(groups)
        last_group_standings = final_result.group_standings
    except Exception as e:
        print(f"      Warning: Could not run display simulation: {e}")

    # ── Report ────────────────────────────────────────────────────────────────
    from reports.report_generator import generate_full_report
    generate_full_report(mc_results, last_group_standings=last_group_standings, verbose=True)

    # Final summary line
    top_champ = mc_results.top_champions(1)
    if top_champ:
        champ_name, champ_pct = top_champ[0]
        print(f"\n{Fore.GREEN}RESULT: {champ_name} won the most simulations "
              f"({champ_pct:.2f}% of {n_sims:,} runs){Style.RESET_ALL}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
