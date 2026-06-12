"""
reports/report_generator.py
Generates ASCII/colorized reports from Monte Carlo simulation results.
"""
from __future__ import annotations
from typing import Dict, List, Optional
from colorama import Fore, Style, init as colorama_init

from engine.monte_carlo import MonteCarloResults

colorama_init(autoreset=True)


def _bar(value: float, max_val: float = 100.0, width: int = 30) -> str:
    """Return an ASCII progress bar."""
    filled = int((value / max(max_val, 0.01)) * width)
    return f"[{'█' * filled}{'░' * (width - filled)}]"


def print_champion_probabilities(mc: MonteCarloResults, top_n: int = 15) -> None:
    """Print top N champion probabilities as a ranked table."""
    top = mc.top_champions(top_n)
    if not top:
        print("No champion data available.")
        return

    max_pct = top[0][1] if top else 100.0

    print(f"\n{Fore.YELLOW}{'='*65}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  🏆  WORLD CUP 2026 — CHAMPION PROBABILITY RANKINGS  🏆{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*65}{Style.RESET_ALL}")
    print(f"  {'#':<4} {'Team':<20} {'Prob %':>7}  {'Bar':^32}")
    print(f"  {'-'*4} {'-'*20} {'-'*7}  {'-'*32}")

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, (team, pct) in enumerate(top, 1):
        medal = medals.get(rank, "  ")
        bar = _bar(pct, max_val=max_pct)
        color = Fore.GREEN if rank == 1 else (Fore.CYAN if rank <= 3 else Fore.WHITE)
        print(f"  {rank:<4} {color}{team:<20}{Style.RESET_ALL} {pct:>6.2f}%  {bar} {medal}")


def print_finalist_probabilities(mc: MonteCarloResults, top_n: int = 10) -> None:
    """Print top N finalist (reach final) probabilities."""
    top = sorted(mc.finalist_probs.items(), key=lambda x: x[1], reverse=True)[:top_n]
    if not top:
        return

    print(f"\n{Fore.CYAN}{'─'*55}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  PROBABILITY OF REACHING THE FINAL{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*55}{Style.RESET_ALL}")
    max_pct = top[0][1] * 100 if top else 1.0
    for team, prob in top:
        pct = prob * 100
        bar = _bar(pct, max_val=max_pct, width=20)
        print(f"  {team:<22} {pct:>6.2f}%  {bar}")


def print_semi_finalist_probabilities(mc: MonteCarloResults, top_n: int = 10) -> None:
    """Print top N semi-finalist probabilities."""
    top = sorted(mc.semi_finalist_probs.items(), key=lambda x: x[1], reverse=True)[:top_n]
    if not top:
        return

    print(f"\n{Fore.MAGENTA}{'─'*55}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}  PROBABILITY OF REACHING SEMI-FINALS{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'─'*55}{Style.RESET_ALL}")
    max_pct = top[0][1] * 100 if top else 1.0
    for team, prob in top:
        pct = prob * 100
        bar = _bar(pct, max_val=max_pct, width=20)
        print(f"  {team:<22} {pct:>6.2f}%  {bar}")


def print_group_predictions(group_standings: Dict) -> None:
    """Print predicted group stage standings from the last simulation."""
    if not group_standings:
        return

    print(f"\n{Fore.BLUE}{'='*55}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}  GROUP STAGE STANDINGS (last simulation){Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*55}{Style.RESET_ALL}")

    for group_name in sorted(group_standings.keys()):
        standings = group_standings[group_name]
        print(f"\n  {Fore.YELLOW}Group {group_name}{Style.RESET_ALL}")
        print(f"  {'Team':<22} {'Pts':>3} {'W':>2} {'D':>2} {'L':>2} {'GF':>3} {'GA':>3} {'GD':>4}")
        print(f"  {'-'*22} {'-'*3} {'-'*2} {'-'*2} {'-'*2} {'-'*3} {'-'*3} {'-'*4}")
        for i, row in enumerate(standings[:4]):
            t = row["team"]
            qualifier = "✓" if i < 2 else " "
            color = Fore.GREEN if i < 2 else Fore.WHITE
            print(
                f"  {color}{qualifier} {t.name:<20}{Style.RESET_ALL} "
                f"{row['pts']:>3} {row['w']:>2} {row['d']:>2} {row['l']:>2} "
                f"{row['gf']:>3} {row['ga']:>3} {row['gd']:>+4}"
            )


def print_most_likely_final(mc: MonteCarloResults) -> None:
    """Print the most likely final matchup."""
    champ, finalist = mc.most_likely_final()
    champ_pct = mc.champion_probs.get(champ, 0) * 100
    finalist_pct = mc.finalist_probs.get(finalist, 0) * 100

    print(f"\n{Fore.RED}{'='*55}{Style.RESET_ALL}")
    print(f"{Fore.RED}  MOST LIKELY FINAL{Style.RESET_ALL}")
    print(f"{Fore.RED}{'='*55}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}{champ}{Style.RESET_ALL} ({champ_pct:.1f}% to win)")
    print(f"       vs")
    print(f"  {Fore.CYAN}{finalist}{Style.RESET_ALL} ({finalist_pct:.1f}% to reach final)")


def print_simulation_summary(mc: MonteCarloResults) -> None:
    """Print a concise summary of Monte Carlo results."""
    print(f"\n{Fore.WHITE}{'='*55}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  SIMULATION SUMMARY ({mc.n:,} simulations){Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'='*55}{Style.RESET_ALL}")

    teams_won = len(mc.champion_counts)
    print(f"  Distinct champions observed: {teams_won}")
    top_champ, top_pct = mc.top_champions(1)[0] if mc.top_champions(1) else ("None", 0)
    print(f"  Most likely champion: {Fore.GREEN}{top_champ}{Style.RESET_ALL} ({top_pct:.2f}%)")


def generate_full_report(
    mc: MonteCarloResults,
    last_group_standings: Optional[Dict] = None,
    verbose: bool = True,
) -> None:
    """Generate and print the complete simulation report."""
    print_simulation_summary(mc)
    print_champion_probabilities(mc, top_n=15)
    print_most_likely_final(mc)
    print_finalist_probabilities(mc, top_n=10)
    print_semi_finalist_probabilities(mc, top_n=10)
    if last_group_standings and verbose:
        print_group_predictions(last_group_standings)
    print(f"\n{Fore.YELLOW}{'='*65}{Style.RESET_ALL}\n")
