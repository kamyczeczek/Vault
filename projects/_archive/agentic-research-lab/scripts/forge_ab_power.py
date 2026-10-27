#!/usr/bin/env python3
"""Required N for the forge-guardrails hooks-ON vs hooks-OFF A/B.

The design is paired: every task is run in both arms, so the outcome is a
paired 2x2 table and the test is McNemar's exact conditional binomial on the
discordant pairs (b = ON pass/OFF fail, c = ON fail/OFF pass). Power is
integrated over the binomial count of discordant pairs, m ~ Binom(N, phi),
where phi is the share of tasks whose outcome differs between arms.

Why this file exists: the handoff carried "N>=5/arm" as a guess. A guess is
not a design. N has to follow from (a) the baseline pass rate, (b) the lift
worth detecting, and (c) phi, the discordance rate -- which is measurable
today from the 15/arm rescue A/B in scripts/forge_ab_test.py.

Stdlib only, per workspace convention. Deterministic: fixed seed.

Usage:
    python scripts/forge_ab_power.py --table
    python scripts/forge_ab_power.py --phi 0.13 --baseline 0.90 --lift 0.10
    python scripts/forge_ab_power.py --mde --phi 0.13 --baseline 0.90 --n 30
"""

from __future__ import annotations

import argparse
import sys
from functools import lru_cache

ALPHA = 0.05
CAP = 400


@lru_cache(maxsize=None)
def _pmf_row(n: int, p_key: float) -> tuple[float, ...]:
    """Binom(n, p) pmf for k=0..n, by forward recurrence (no comb, no pow)."""
    p = p_key
    row = [0.0] * (n + 1)
    if p >= 1.0:
        row[n] = 1.0
        return tuple(row)
    if p <= 0.0:
        row[0] = 1.0
        return tuple(row)
    row[0] = (1.0 - p) ** n
    for k in range(n):
        row[k + 1] = row[k] * (n - k) / (k + 1) * p / (1.0 - p)
    return tuple(row)


def _cum(row: tuple[float, ...], upto: int) -> float:
    return sum(row[: upto + 1])


@lru_cache(maxsize=None)
def _crit(m: int, alpha: float = ALPHA) -> int:
    """Largest t with 2*Cdf(t; m, 0.5) < alpha: reject when min(b, c) <= t.

    m is the discordant-pair count. Under H0 the split of the m discordant
    pairs is Binom(m, 0.5), so this is the exact conditional McNemar test --
    the small-sample, mid-p flavoured upgrade over chi-square.
    """
    half = _pmf_row(m, 0.5)
    acc = 0.0
    t = -1
    for k in range(m + 1):
        acc += half[k]
        if 2.0 * acc < alpha:
            t = k
        else:
            break
    return t


def reject_two_sided(b: int, c: int, alpha: float = ALPHA) -> bool:
    m = b + c
    if m == 0:
        return False
    return min(b, c) <= _crit(m, alpha)


def power(n: int, phi: float, psi: float, alpha: float = ALPHA) -> float:
    """Exact power of the paired test at n tasks, discordance phi, lift psi.

    m ~ Binom(n, phi) discordant pairs; conditional on m, b ~ Binom(m, psi)
    go ON's way. Enumerated exactly -- no Monte Carlo, no seed, deterministic.
    """
    if not 0.0 < phi < 1.0:
        raise ValueError("phi must be in (0, 1)")
    if not 0.5 <= psi <= 1.0:
        raise ValueError("psi must be in [0.5, 1.0]")
    mrow = _pmf_row(n, phi)
    total = 0.0
    for m in range(n + 1):
        if mrow[m] < 1e-12:
            continue
        t = _crit(m, alpha)
        if t < 0:
            continue
        brow = _pmf_row(m, psi)
        # reject iff b <= t or b >= m-t, so P(hit) = Cdf(t) + 1 - Cdf(m-t-1)
        hit = (_cum(brow, t) if t >= 0 else 0.0) + \
            (1.0 - _cum(brow, m - t - 1) if m - t - 1 >= 0 else 1.0)
        total += mrow[m] * min(hit, 1.0)
    return total


def _psi_for(baseline: float, lift: float, phi: float) -> float:
    """Directional share of discordant pairs, exact given (p0, p1, phi).

    Paired table: a = both pass, b = ON pass/OFF fail, c = ON fail/OFF pass,
    d = both fail. Then b + c = phi and b - c = p1 - p0 = lift, so
    psi = b/phi = (phi + lift) / (2 phi). Feasibility requires lift <= phi:
    a marginal difference between two arms can never exceed the share of
    tasks that flip between them. `required_n` reports lift > phi as
    unreachable rather than silently clipping.
    """
    return 0.5 + lift / (2.0 * phi)


def required_n(baseline: float, lift: float, phi: float,
               target: float = 0.8, cap: int = CAP) -> int | None:
    """Smallest n reaching `target` power for an absolute lift (binary search)."""
    if lift > phi:
        return None  # unattainable: lift cannot exceed the discordance rate
    psi = _psi_for(baseline, lift, phi)
    if power(cap, phi, psi) < target:
        return None
    lo, hi = 2, cap
    while lo < hi:
        mid = (lo + hi) // 2
        if power(mid, phi, psi) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def mde(baseline: float, phi: float, n: int, target: float = 0.8) -> float:
    """Smallest absolute lift detectable at n (the inverse question)."""
    if power(n, phi, 1.0) < target:
        return float("nan")  # unreachable even winning every discordant pair
    lo, hi = 0.0, max(0.0, min(1.0 - baseline, phi))
    for _ in range(30):
        mid = (lo + hi) / 2.0
        psi = _psi_for(baseline, mid, phi)
        if power(n, phi, psi) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def _selftest() -> int:
    """Pin the two claims the design rests on. Returns the failure count.

    1. Minimum discordant pairs for any rejection. Under H0 the split is
       Binom(m, 0.5), so an all-one-sided result gives p = 2*(0.5)^m. That
       crosses alpha=0.05 between m=5 (0.0625, no) and m=6 (0.03125, yes).
       .forge-ab/tasks.yaml states `min_discordant_pairs_for_a_verdict: 6`;
       this is where that number comes from.
    2. The null is not rejected: a genuinely null pair set (b == c) never
       rejects, at any m.
    """
    bad = 0
    if reject_two_sided(6, 0):
        pass
    else:
        sys.stderr.write("FAIL: m=6 all-one-sided should reject\n")
        bad += 1
    if reject_two_sided(5, 0):
        sys.stderr.write("FAIL: m=5 all-one-sided must not reject\n")
        bad += 1
    for m in (6, 7, 9, 14, 20):
        for b in range(0, m + 1):
            # A null split (b == c) must never reject, at any m.
            if b * 2 == m and reject_two_sided(b, m - b):
                sys.stderr.write(f"FAIL: null split b=c={b} rejected at m={m}\n")
                bad += 1
    # lift cannot exceed phi
    if required_n(0.5, 0.30, 0.13) is not None:
        sys.stderr.write("FAIL: lift 0.30 > phi 0.13 reported as reachable\n")
        bad += 1
    # power is monotone in n, bounded, and deterministic (no Monte Carlo)
    if not (power(10, 0.3, 0.8) <= power(40, 0.3, 0.8) <= 1.0):
        sys.stderr.write("FAIL: power not monotone/bounded in n\n")
        bad += 1
    if power(37, 0.17, 0.71) != power(37, 0.17, 0.71):
        sys.stderr.write("FAIL: power is not deterministic\n")
        bad += 1
    if bad:
        return bad
    sys.stderr.write(
        "SELFTEST OK: min discordant m=6, null never rejects, lift>phi "
        "unreachable, power deterministic\n")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="verify the test's own claims and exit")
    ap.add_argument("--phi", type=float, default=0.13,
                    help="discordance rate between arms (default 0.13, "
                         "empirical from the 15/arm rescue A/B)")
    ap.add_argument("--baseline", type=float, default=0.90,
                    help="hooks-OFF pass rate")
    ap.add_argument("--lift", type=float, default=0.10)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--target", type=float, default=0.8)
    ap.add_argument("--mde", action="store_true",
                    help="report the minimum detectable lift at --n")
    ap.add_argument("--table", action="store_true",
                    help="grid over baseline x phi x lift")
    args = ap.parse_args()

    if args.selftest:
        raise SystemExit(_selftest())

    if args.table:
        print(f"required n (paired McNemar, alpha={ALPHA}, power={args.target})")
        print(f"{'baseline':>9} {'phi':>6} {'lift':>6} {'n':>5} {'runs':>6}")
        for baseline in (0.30, 0.50, 0.70, 0.90):
            for phi in (0.05, 0.13, 0.30, 0.60):
                for lift in (0.10, 0.20, 0.30):
                    if baseline + lift > 1.0:
                        continue
                    n = required_n(baseline, lift, phi, args.target)
                    cell = str(n) if n else "unreach"
                    runs = str(2 * n) if n else "-"
                    print(f"{baseline:>9.2f} {phi:>6.2f} {lift:>6.2f} "
                          f"{cell:>5} {runs:>6}")
        print("\nn = paired tasks per arm; runs = total goose runs = 2n.")
        print("unreach = lift > phi is unattainable for a paired design (a")
        print("marginal difference cannot exceed the share of tasks that flip),")
        print("or n > 400. Fix phi by task heterogeneity, not by adding runs.")
        print("\nEmpirical phi anchor: the 15/arm rescue A/B scored 14/15 in")
        print("both arms with one MaxIterationsError each -> phi ~= 2/15 =")
        print("0.13 if the failures are different tasks, 0.0 if the same one.")
        return

    if args.mde:
        print(f"baseline={args.baseline:.2f} phi={args.phi:.2f} "
              f"n={args.n} power={args.target}")
        print(f"minimum detectable lift: "
              f"{mde(args.baseline, args.phi, args.n, args.target):.3f}")
        return

    n = required_n(args.baseline, args.lift, args.phi, args.target)
    if n is None:
        if args.lift > args.phi:
            print(f"unattainable: lift={args.lift} > phi={args.phi}. In a")
            print("paired design the marginal difference is bounded by the")
            print("discordance rate; widen the task set, do not add runs.")
        else:
            print(f"unreachable at lift={args.lift} phi={args.phi} "
                  f"(cap {CAP} tasks/arm)")
        return
    psi = _psi_for(args.baseline, args.lift, args.phi)
    print(f"baseline={args.baseline:.2f} lift={args.lift:+.2f} "
          f"phi={args.phi:.2f} -> n={n} paired tasks per arm "
          f"({2 * n} goose runs), psi={psi:.3f}, "
          f"expected discordant m={n * args.phi:.1f}")


if __name__ == "__main__":
    main()