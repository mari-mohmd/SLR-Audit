"""
Local vs. Global Variable Loop Benchmark
==========================================
Benchmarks how long a simple Python for-loop takes when incrementing
a LOCAL variable (inside a function) vs. a GLOBAL variable, across
several loop counts, then plots the results with trendlines/equations
in the same style as the reference chart.

Usage:
    python local_vs_global_benchmark.py

Adjust LOOP_COUNTS below if you want faster/slower runs.
"""

import time
import numpy as np
import matplotlib.pyplot as plt


LOOP_COUNTS = [1_000_000, 100_000_000, 500_000_000, 1_000_000_000]

counter_global = 0  # module-level global used by loop_global()


def loop_local(n):
    """Increment a LOCAL variable n times."""
    counter_local = 0
    for _ in range(n):
        counter_local += 1
    return counter_local


def loop_global(n):
    """Increment a GLOBAL variable n times."""
    global counter_global
    counter_global = 0
    for _ in range(n):
        counter_global += 1
    return counter_global


def time_it(func, n):
    start = time.perf_counter()
    func(n)
    return time.perf_counter() - start


def run_benchmarks(loop_counts):
    local_times = []
    global_times = []
    for n in loop_counts:
        t_local = time_it(loop_local, n)
        t_global = time_it(loop_global, n)
        local_times.append(t_local)
        global_times.append(t_global)
        print(f"n={n:>15,}  local={t_local:8.4f}s   global={t_global:8.4f}s")
    return np.array(local_times), np.array(global_times)


def plot_results(loop_counts, local_times, global_times, out_path="loop_benchmark.png"):
    x = np.array(loop_counts, dtype=float)

    # Linear trendlines (least-squares fit), same as Excel's "linear trendline"
    m_local, b_local = np.polyfit(x, local_times, 1)
    m_global, b_global = np.polyfit(x, global_times, 1)

    x_line = np.linspace(0, x.max(), 200)
    y_local_line = m_local * x_line + b_local
    y_global_line = m_global * x_line + b_global

    fig, ax = plt.subplots(figsize=(11, 8))

    # Data points
    ax.plot(x, local_times, marker="^", color="black", linestyle="None",
            markersize=9, label="Python loop - Local")
    ax.plot(x, global_times, marker="s", color="firebrick", linestyle="None",
            markersize=9, label="Python Loop - Global")

    # Dotted trendlines
    ax.plot(x_line, y_local_line, linestyle=":", color="gray", linewidth=1.5)
    ax.plot(x_line, y_global_line, linestyle=":", color="firebrick", linewidth=1.5)

    # Trendline equations, annotated near the middle of each line
    ax.annotate(f"y = {m_global:.0E}x {'+' if b_global >= 0 else '-'} {abs(b_global):.4f}",
                xy=(x.max() * 0.62, m_global * x.max() * 0.62 + b_global + 4),
                fontsize=11, color="black")
    ax.annotate(f"y = {m_local:.0E}x {'+' if b_local >= 0 else '-'} {abs(b_local):.4f}",
                xy=(x.max() * 0.62, m_local * x.max() * 0.62 + b_local + 2),
                fontsize=11, color="black")

    ax.set_xlabel("Loop Count", fontsize=13)
    ax.set_ylabel("Time (seconds)", fontsize=13)
    ax.grid(True, linestyle="-", linewidth=0.5, color="0.85")
    ax.legend(loc="upper left", bbox_to_anchor=(0.15, 1.12), ncol=2,
              frameon=False, fontsize=12)

    ax.set_xticks(loop_counts)
    ax.set_xticklabels([f"{int(c):,}" for c in loop_counts], rotation=30, ha="right")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"\nSaved chart to {out_path}")


if __name__ == "__main__":
    local_times, global_times = run_benchmarks(LOOP_COUNTS)
    plot_results(LOOP_COUNTS, local_times, global_times)