"""
engine/monte_carlo.py
Monte Carlo engine that runs N tournament simulations and aggregates results.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Dict, List, Optional
import numpy as np
from tqdm import tqdm

from models.team import Team
from simulator.tournament_simulator import simulate_tournament, TournamentResult


class MonteCarloResults:
    """Aggregated results from N tournament simulations."""

    def __init__(self, n: int):
        self.n = n
        self.champion_counts: Counter = Counter()
        self.finalist_counts: Counter = Counter()
        self.semi_finalist_counts: Counter = Counter()
        self.quarter_finalist_counts: Counter = Counter()
        self.round_of_16_counts: Counter = Counter()
        self.champion_probs: Dict[str, float] = {}
        self.finalist_probs: Dict[str, float] = {}
        self.semi_finalist_probs: Dict[str, float] = {}

    def compute_probabilities(self) -> None:
        """Convert counts to probabilities."""
        self.champion_probs = {
            team: count / self.n
            for team, count in self.champion_counts.most_common()
        }
        self.finalist_probs = {
            team: count / self.n
            for team, count in self.finalist_counts.most_common()
        }
        self.semi_finalist_probs = {
            team: count / self.n
            for team, count in self.semi_finalist_counts.most_common()
        }

    def top_champions(self, n: int = 10) -> List[tuple]:
        """Return top n champion teams with their probabilities."""
        return [
            (team, round(prob * 100, 2))
            for team, prob in sorted(
                self.champion_probs.items(), key=lambda x: x[1], reverse=True
            )[:n]
        ]

    def most_likely_final(self) -> tuple:
        """Return the most likely (team_a, team_b) final pairing."""
        if not self.champion_probs or not self.finalist_probs:
            return ("Unknown", "Unknown")
        top_champ = max(self.champion_probs, key=self.champion_probs.get)
        top_final = max(self.finalist_probs, key=self.finalist_probs.get)
        return (top_champ, top_final)

    def __repr__(self) -> str:
        top = self.top_champions(3)
        return f"MonteCarloResults(n={self.n}, top3={top})"


def run_monte_carlo(
    groups: Dict[str, List[Team]],
    n: int = 10000,
    verbose: bool = True,
    seed: Optional[int] = None,
) -> MonteCarloResults:
    """
    Run N full tournament simulations.
    Returns aggregated MonteCarloResults.
    """
    if seed is not None:
        np.random.seed(seed)

    mc = MonteCarloResults(n=n)
    iterator = tqdm(range(n), desc="Simulating", unit="sim") if verbose else range(n)

    for _ in iterator:
        try:
            result = simulate_tournament(groups)
            if result.champion:
                mc.champion_counts[result.champion.name] += 1
            if result.finalist:
                mc.finalist_counts[result.finalist.name] += 1
            if result.champion:
                mc.finalist_counts[result.champion.name] += 1  # champion also reached final
            for team in result.semi_finalists:
                mc.semi_finalist_counts[team.name] += 1
            for team in result.quarter_finalists:
                mc.quarter_finalist_counts[team.name] += 1
            for team in result.round_of_16_teams:
                mc.round_of_16_counts[team.name] += 1
        except Exception as e:
            # Don't let a single simulation crash the whole run
            continue

    mc.compute_probabilities()
    return mc
