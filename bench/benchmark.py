#!/usr/bin/env python3
"""
benchmark.py - Run a Python or Rust program N times and report execution-time stats.

Timing is measured externally (wall-clock around the subprocess call), so it
works regardless of what the program itself prints, and is directly
comparable between Python and Rust.

Usage:
    python3 benchmark.py --lang python --file loop.py
    python3 benchmark.py --lang rust   --file loop.rs
    python3 benchmark.py --lang rust   --file loop.rs --runs 10 --release
    python3 benchmark.py --lang rust   --file loop.rs --runs 10 --opt-level 3
    python3 benchmark.py --lang rust   --file loop.rs --rustc-flags "-C opt-level=3 -C lto=fat"
    python3 benchmark.py --lang python --file loop.py --python-bin python3.11
    python3 benchmark.py --lang rust   --file loop.rs --release --csv results/rust_release.csv

Rust programs are compiled once before the timed runs.
  --release          shorthand for -C opt-level=3 (roughly `cargo build --release`)
  --opt-level LEVEL   pass -C opt-level=LEVEL (0, 1, 2, 3, s, or z)
  --rustc-flags "..." any additional raw flags to pass straight to rustc,
                      appended after --release/--opt-level (space-separated,
                      use this for things like -C lto=fat or -C target-cpu=native)
  --csv PATH          write one row per run (raw timings, not just the
                      summary) to PATH, so results can be committed and
                      re-verified rather than taken on trust. Rows are
                      flushed to disk as each run finishes.
"""

import argparse
import csv
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def compile_rust(source: Path, release: bool, opt_level: str, rustc_flags: str) -> Path:
    """Compile a .rs file with rustc and return the path to the binary."""
    # opt-level precedence: explicit --opt-level wins; otherwise --release means "3"
    if opt_level is None and release:
        opt_level = "3"

    suffix = ""
    if opt_level is not None:
        suffix += f"_O{opt_level}"
    binary = source.with_suffix("")  # e.g. loop.rs -> loop
    if suffix:
        binary = binary.with_name(binary.name + suffix)

    cmd = ["rustc"]
    if opt_level is not None:
        cmd += ["-C", f"opt-level={opt_level}"]
    if rustc_flags:
        cmd += rustc_flags.split()
    cmd += [str(source), "-o", str(binary)]

    print(f"Compiling: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("rustc failed:\n" + result.stderr, file=sys.stderr)
        sys.exit(1)
    return binary


def build_command(lang: str, file: Path, python_bin: str, release: bool, opt_level: str, rustc_flags: str):
    if lang == "python":
        return [python_bin, str(file)]
    elif lang == "rust":
        binary = compile_rust(file, release, opt_level, rustc_flags)
        return [str(binary.resolve())]
    else:
        raise ValueError(f"Unsupported language: {lang}")


def run_once(cmd, show_output: bool):
    """Run the program once, returning (wall_clock_seconds, stdout)."""
    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        print(f"Program exited with code {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    if show_output:
        print(result.stdout.strip())
    return elapsed


def open_csv_writer(csv_path: Path, fieldnames):
    """Open csv_path for writing and return (file_handle, DictWriter). Writes the header immediately."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(csv_path, "w", newline="")
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    f.flush()
    return f, writer


def main():
    parser = argparse.ArgumentParser(description="Benchmark a Python or Rust program over multiple runs.")
    parser.add_argument("--lang", choices=["python", "rust"], required=True, help="Language of the program")
    parser.add_argument("--file", required=True, help="Path to the .py or .rs source file")
    parser.add_argument("--runs", type=int, default=30, help="Number of times to run the program (default: 30)")
    parser.add_argument("--python-bin", default=sys.executable, help="Python interpreter to use (default: current one)")
    parser.add_argument("--release", action="store_true", help="Compile Rust with optimizations (shorthand for --opt-level 3)")
    parser.add_argument("--opt-level", choices=["0", "1", "2", "3", "s", "z"], default=None,
                         help="Rust optimization level, passed as -C opt-level=LEVEL")
    parser.add_argument("--rustc-flags", default="", help='Extra raw flags passed to rustc, e.g. "-C lto=fat -C target-cpu=native"')
    parser.add_argument("--show-output", action="store_true", help="Print each run's stdout")
    parser.add_argument("--csv", default=None, help="Write per-run timings to this CSV path (raw data backing the summary stats)")
    args = parser.parse_args()

    file = Path(args.file)
    if not file.exists():
        print(f"File not found: {file}", file=sys.stderr)
        sys.exit(1)

    cmd = build_command(args.lang, file, args.python_bin, args.release, args.opt_level, args.rustc_flags)
    cmd_str = " ".join(cmd)

    csv_file, csv_writer = (None, None)
    if args.csv:
        csv_path = Path(args.csv)
        fieldnames = ["run", "elapsed_seconds", "timestamp_utc", "lang", "file", "command", "opt_level", "rustc_flags"]
        csv_file, csv_writer = open_csv_writer(csv_path, fieldnames)
        print(f"Writing per-run timings to {csv_path}")

    times = []
    print(f"\nRunning {args.file} ({args.lang}) {args.runs} times...\n")
    try:
        for i in range(1, args.runs + 1):
            elapsed = run_once(cmd, args.show_output)
            times.append(elapsed)
            print(f"  Run {i:>2}/{args.runs}: {elapsed:.4f} s")

            if csv_writer:
                csv_writer.writerow({
                    "run": i,
                    "elapsed_seconds": f"{elapsed:.6f}",
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "lang": args.lang,
                    "file": str(args.file),
                    "command": cmd_str,
                    "opt_level": args.opt_level or ("3" if args.release else ""),
                    "rustc_flags": args.rustc_flags,
                })
                csv_file.flush()  # flush after every run so a crash mid-benchmark doesn't lose completed rows
    finally:
        if csv_file:
            csv_file.close()

    print("\n--- Summary ---")
    print(f"Runs:    {len(times)}")
    print(f"Average: {statistics.mean(times):.4f} s")
    print(f"Median:  {statistics.median(times):.4f} s")
    print(f"Min:     {min(times):.4f} s")
    print(f"Max:     {max(times):.4f} s")
    if len(times) > 1:
        print(f"Std dev: {statistics.stdev(times):.4f} s")


if __name__ == "__main__":
    main()