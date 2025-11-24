#!/usr/bin/env python3
import time
import math
import sys
import os
from collections import namedtuple

SIZES = [64 * 1024, 1 * 1024 * 1024, 8 * 1024 * 1024]  # bytes: 64KB, 1MB, 8MB
WARMUP = 2
RUNS = 32
DATA_TYPES = ['random', 'repetitive', 'textlike']
# -------------------------

Candidate = namedtuple('Candidate', ['name', 'module', 'compress', 'decompress'])

def try_imports():
    candidates = []
    tried = []
    imports_to_try = [
        ('snappy_py (import snappy_py)', 'snappy_py'),
        ('python-snappy (import snappy)', 'snappy'),
        ('cramjam (import cramjam)', 'cramjam')
    ]
    for pretty, name in imports_to_try:
        if name in tried:
            continue
        tried.append(name)
        try:
            mod = __import__(name)
        except Exception:
            continue
        compress = getattr(mod, 'compress', None)
        decompress = getattr(mod, 'decompress', None)
        if not compress or not decompress:
            if hasattr(mod, 'snappy'):
                sub = getattr(mod, 'snappy')
                if hasattr(sub, 'compress') and hasattr(sub, 'decompress'):
                    compress = getattr(sub, 'compress')
                    decompress = getattr(sub, 'decompress')
        if callable(compress) and callable(decompress):
            candidates.append(Candidate(pretty, mod, compress, decompress))
    return candidates

def make_data(kind, size):
    if kind == 'random':
        return os.urandom(size)
    elif kind == 'repetitive':
        chunk = b'ABCD'  # small repeating pattern
        return (chunk * (size // len(chunk) + 1))[:size]
    elif kind == 'textlike':
        lorem = (b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                 b"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ")
        return (lorem * (size // len(lorem) + 1))[:size]
    else:
        raise ValueError('unknown kind')

def time_func(func, data, runs, warmup=1):
    # warmup
    for _ in range(warmup):
        func(data)
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        func(data)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return (sum(times) / len(times), min(times), max(times))

def bytes_to_mb(b):
    return b / (1024*1024)

def bench_candidate(cand):
    results = []
    for kind in DATA_TYPES:
        for size in SIZES:
            data = make_data(kind, size)
            # compress
            try:
                c_avg, c_min, c_max = time_func(cand.compress, data, runs=RUNS, warmup=WARMUP)
                comp = cand.compress(data)
                comp_len = len(comp)
            except Exception as e:
                c_avg = c_min = c_max = float('nan')
                comp_len = None
                comp = None
                comp_err = e
            # decompress: use compressed blob if available, otherwise skip
            if comp is not None:
                try:
                    d_avg, d_min, d_max = time_func(cand.decompress, comp, runs=RUNS, warmup=WARMUP)
                except Exception as e:
                    d_avg = d_min = d_max = float('nan')
                    decomp_err = e
            else:
                d_avg = d_min = d_max = float('nan')
            results.append({
                'impl': cand.name,
                'kind': kind,
                'size_bytes': size,
                'orig_MB': bytes_to_mb(size),
                'comp_bytes': comp_len,
                'comp_ratio': (comp_len / size) if (comp_len is not None and size>0) else None,
                'compress_avg_s': c_avg,
                'compress_min_s': c_min,
                'compress_max_s': c_max,
                'decompress_avg_s': d_avg,
                'decompress_min_s': d_min,
                'decompress_max_s': d_max,
            })
    return results

def pretty_print(results):
    header = ("Impl", "Data", "Size", "Orig(MB)", "Comp(bytes)", "CompRatio", "Comp MB/s", "Decomp MB/s")
    print("{:30s} {:10s} {:8s} {:9s} {:12s} {:9s} {:11s} {:11s}".format(*header))
    print("-"*110)
    for r in results:
        impl = r['impl']
        kind = r['kind']
        size_label = f"{r['size_bytes']//1024}K" if r['size_bytes'] < 1024*1024 else f"{r['size_bytes']//(1024*1024)}M"
        orig_mb = f"{r['orig_MB']:.2f}"
        comp_bytes = str(r['comp_bytes']) if r['comp_bytes'] is not None else "err"
        comp_ratio = f"{r['comp_ratio']:.3f}" if r['comp_ratio'] is not None else "err"
        # MB/s = orig_MB / avg_time
        try:
            comp_mbs = f"{(r['orig_MB'] / r['compress_avg_s']):.2f}"
        except Exception:
            comp_mbs = "err"
        try:
            decomp_mbs = f"{(r['orig_MB'] / r['decompress_avg_s']):.2f}"
        except Exception:
            decomp_mbs = "err"
        print("{:30s} {:10s} {:8s} {:9s} {:12s} {:9s} {:11s} {:11s}".format(
            impl, kind, size_label, orig_mb, comp_bytes, comp_ratio, comp_mbs, decomp_mbs
        ))

def main():
    cands = try_imports()
    if not cands:
        sys.exit(1)
    for c in cands:
        print(" -", c.name)
    all_results = []
    for cand in cands:
        try:
            res = bench_candidate(cand)
            all_results.extend(res)
        except Exception as e:
            pass
    pretty_print(all_results)
    print("\nCompRatio = compressed_bytes / original_bytes")

if __name__ == '__main__':
    main()
