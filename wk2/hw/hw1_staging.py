"""
SPCE 5045 Homework #1 -- Multi-Stage Rocket Mass Calculator
============================================================
Solves the three-part staging problem:
  1. Number of stages needed given delta-V per stage and total delta-V
  2. Total rocket mass given the equal-mass-above rule
  3. General closed-form relationship

Textbook: Wertz, Everett, Puschell, "Space Mission Engineering: The New SMAD"
          Microcosm Press, 2011. Chapter 1, pp. 10-11.
"""

import math
from typing import List, Tuple

import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Problem parameters
# ---------------------------------------------------------------------------
DELTA_V_PER_STAGE: float = 3.0          # km/s per stage
PAYLOAD_MASS: float = 100.0             # kg

# Target delta-V values (km/s) and labels
BODIES: List[Tuple[str, float]] = [
    ("Moon",    1.7),
    ("Earth",   7.8),
    ("Jupiter", 42.0),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def stages_required(delta_v_total: float, delta_v_per_stage: float) -> int:
    """Return the minimum integer number of stages to reach delta_v_total.

    Each stage contributes exactly delta_v_per_stage km/s.
    We round UP because partial stages do not exist.
    """
    return math.ceil(delta_v_total / delta_v_per_stage)


def build_stage_masses(n_stages: int, payload_kg: float) -> List[float]:
    """Compute individual stage masses from top stage to bottom stage.

    Rule: mass of each stage = (mass of all stages above it) + payload.
    Construction proceeds from the topmost (smallest) stage downward.

    Returns a list where index 0 = topmost stage, index -1 = bottom stage.
    """
    stages: List[float] = []
    cumulative_above: float = payload_kg  # everything the top stage must support

    for _ in range(n_stages):
        stage_mass = cumulative_above      # this stage's mass = everything above
        stages.append(stage_mass)
        cumulative_above += stage_mass      # update cumulative for next stage down

    return stages


def total_rocket_mass(n_stages: int, payload_kg: float) -> float:
    """Total mass = payload + sum of all stage masses (iterative)."""
    stage_masses = build_stage_masses(n_stages, payload_kg)
    return payload_kg + sum(stage_masses)


def total_mass_closed_form(n_stages: int, payload_kg: float) -> float:
    """Closed-form: Total mass = payload * 2^n."""
    return payload_kg * (2 ** n_stages)


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 65)
    print("SPCE 5045 Homework #1 -- Multi-Stage Rocket Analysis")
    print("=" * 65)

    # ------ Problem 1: Number of stages ------
    print("\n--- Problem 1: Number of Stages Required ---\n")
    print(f"  Delta-V per stage: {DELTA_V_PER_STAGE} km/s\n")

    results = []
    for body, dv in BODIES:
        n = stages_required(dv, DELTA_V_PER_STAGE)
        print(f"  {body:>8s}:  delta-V = {dv:5.1f} km/s  -->  "
              f"ceil({dv}/{DELTA_V_PER_STAGE}) = {n} stage(s)")
        results.append((body, dv, n))

    # ------ Problem 2: Total rocket mass ------
    print("\n--- Problem 2: Total Rocket Mass (100 kg payload) ---\n")

    mass_results = []
    for body, dv, n in results:
        # Iterative calculation
        stage_masses = build_stage_masses(n, PAYLOAD_MASS)
        total_iter = PAYLOAD_MASS + sum(stage_masses)

        # Closed-form verification
        total_cf = total_mass_closed_form(n, PAYLOAD_MASS)

        print(f"  {body:>8s}:  {n} stage(s)")
        # Print individual stage masses (bottom = stage 1, top = stage n)
        for i, sm in enumerate(stage_masses):
            stage_num = n - i  # convert top-first index to conventional numbering
            label = "(bottom, 1st stage)" if stage_num == 1 else \
                    "(top)"              if stage_num == n else ""
            print(f"    Stage {stage_num}: {sm:>14,.0f} kg  {label}")
        print(f"    Payload:  {PAYLOAD_MASS:>14,.0f} kg")
        print(f"    TOTAL:    {total_iter:>14,.0f} kg")
        print(f"    Verify (closed-form): {total_cf:,.0f} kg  "
              f"[match: {math.isclose(total_iter, total_cf)}]")
        print()
        mass_results.append((body, n, total_iter))

    # ------ Problem 3: General formula ------
    print("--- Problem 3: General Relationship ---\n")
    print("  For n stages and payload mass m_p:")
    print("    Total_mass = m_p * 2^n")
    print()
    print("  Derivation sketch:")
    print("    Each stage's mass equals the cumulative mass above it.")
    print("    Adding a stage doubles the cumulative total.")
    print("    After n doublings starting from m_p: Total = m_p * 2^n")

    # ------ Verification: dimensional / limiting cases ------
    print("\n--- Verification ---\n")
    print("  Limiting case n=0 (no stages, payload only):")
    print(f"    100 * 2^0 = {total_mass_closed_form(0, 100):.0f} kg  [correct]")
    print("  Limiting case n=1:")
    print(f"    100 * 2^1 = {total_mass_closed_form(1, 100):.0f} kg")
    print("    Stage mass = payload = 100 kg, total = 200 kg  [correct]")
    print("  Growth check: each additional stage doubles total mass.")
    for n_test in range(1, 5):
        ratio = total_mass_closed_form(n_test, 100) / total_mass_closed_form(n_test - 1, 100)
        print(f"    n={n_test}: total = {total_mass_closed_form(n_test, 100):,.0f} kg, "
              f"ratio to n={n_test-1}: {ratio:.1f}x")

    # ------ Plot ------
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [r[0] for r in mass_results]
    masses = [r[2] for r in mass_results]
    n_stages_list = [r[1] for r in mass_results]

    bars = ax.bar(names, masses, color=["#7eb0d5", "#b2e061", "#fd7f6f"],
                  edgecolor="black", linewidth=0.8)

    ax.set_yscale("log")
    ax.set_ylabel("Total Rocket Mass (kg)", fontsize=12)
    ax.set_title("Total Launch Mass to Reach Orbit\n"
                 "(100 kg payload, 3 km/s per stage)", fontsize=13)

    for bar, n, m in zip(bars, n_stages_list, masses):
        ax.text(bar.get_x() + bar.get_width() / 2, m * 1.4,
                f"{m:,.0f} kg\n({n} stages)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylim(top=max(masses) * 8)
    plt.tight_layout()
    plt.savefig("hw1_staging_mass.png", dpi=150)
    print("\n  Plot saved to hw1_staging_mass.png")
    plt.show()


if __name__ == "__main__":
    main()
