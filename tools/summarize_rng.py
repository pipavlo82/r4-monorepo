#!/usr/bin/env python3
import sys, re, csv, os, time
from pathlib import Path

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def parse_practrand_stream(path: Path, max_lines=None, sample_every=1):
    # Потоково читаємо, не тягнемо все у пам'ять
    pvals = []
    rx = re.compile(r'\bp\s*=\s*([0-9.]+|1-\s*[\deE.+-]+)')
    cnt = 0
    with path.open('r', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            if max_lines and i > max_lines: break
            m = rx.search(line)
            if not m: 
                continue
            if sample_every > 1 and (len(pvals) % sample_every) != 0:
                # легке прорідження великого набору
                pass
            raw = m.group(1).replace(" ", "")
            try:
                if raw.startswith("1-"):
                    x = float(raw[2:])
                    p = max(0.0, min(1.0, 1.0 - x))
                else:
                    p = float(raw)
            except Exception:
                continue
            pvals.append(p)
            cnt += 1
            if cnt % 100000 == 0:
                log(f"PractRand parsed {cnt} p-values so far…")
    log(f"PractRand total p-values: {len(pvals)}")
    return pvals

def parse_dieharder(path: Path):
    rx = re.compile(r"p-value\s*=\s*([0-9.]+(?:e[+-]?\d+)?)", re.I)
    summ = {"PASSED":0, "WEAK":0, "FAILED":0}
    rows = []
    seen = 0
    with path.open('r', errors='ignore') as f:
        for line in f:
            if "p-value" in line:
                status = "PASSED" if "PASSED" in line else ("WEAK" if "WEAK" in line else ("FAILED" if "FAILED" in line else ""))
                m = rx.search(line)
                p = m.group(1) if m else ""
                rows.append((p, status, line.strip()))
                if status in summ: summ[status] += 1
                seen += 1
    log(f"Dieharder total lines with p-value: {seen}")
    return summ, rows

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",  dest="inp",  required=True, help="folder with *consolidated logs")
    ap.add_argument("--out", dest="out", required=True, help="output folder")
    ap.add_argument("--max-practrand-lines", type=int, default=None, help="optional cap for very big files")
    ap.add_argument("--sample-every", type=int, default=1, help="thin out points for plotting (default=1)")
    args = ap.parse_args()

    din = Path(args.inp); dout = Path(args.out)
    dout.mkdir(parents=True, exist_ok=True)
    log(f"INPUT: {din}")
    log(f"OUTPUT: {dout}")

    # locate files
    pract = None
    for name in ("practrand_1gb.txt",):
        p = din / name
        if p.exists(): pract = p; break
    if not pract:
        cands = list(din.glob("*practrand*.txt"))
        if cands: pract = cands[0]
    if pract:
        log(f"PractRand log: {pract} ({pract.stat().st_size/1e6:.2f} MB)")
    else:
        log("PractRand log: NOT FOUND")

    dieh = None
    for name in ("dieharder_1gb.txt",):
        p = din / name
        if p.exists(): dieh = p; break
    if not dieh:
        cands = list(din.glob("*dieharder*.txt"))
        if cands: dieh = cands[0]
    if dieh:
        log(f"Dieharder log: {dieh} ({dieh.stat().st_size/1e6:.2f} MB)")
    else:
        log("Dieharder log: NOT FOUND")

    # PractRand
    pvals = []
    if pract:
        log("Parsing PractRand…")
        pvals = parse_practrand_stream(pract, max_lines=args.max_practrand_lines, sample_every=max(1, args.sample_every))
        # CSV
        csv_path = dout / "consolidated.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["index","practrand_p"])
            for i,p in enumerate(pvals): w.writerow([i,p])
        log(f"Wrote CSV: {csv_path} ({len(pvals)} rows)")
        # Plot (headless)
        if pvals:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            log("Rendering PractRand timeline plot…")
            plt.figure()
            plt.plot(range(len(pvals)), pvals, marker='.', linestyle='none')
            plt.xlabel("test index"); plt.ylabel("p-value"); plt.title("PractRand timeline")
            plt.ylim(-0.02, 1.02); plt.grid(True, alpha=0.3)
            out_png = dout / "practrand_timeline.png"
            plt.savefig(out_png, dpi=140, bbox_inches="tight"); plt.close()
            log(f"Wrote PNG: {out_png}")

    # Dieharder
    if dieh:
        log("Parsing Dieharder…")
        summ, rows = parse_dieharder(dieh)
        with (dout/"dieharder_summary.txt").open("w", encoding="utf-8") as f:
            f.write("Dieharder summary\n")
            for k in ("PASSED","WEAK","FAILED"):
                f.write(f"{k}: {summ.get(k,0)}\n")
        log(f"Wrote summary: {dout/'dieharder_summary.txt'} (PASSED={summ.get('PASSED',0)}, WEAK={summ.get('WEAK',0)}, FAILED={summ.get('FAILED',0)})")

    log("DONE")

if __name__ == "__main__":
    main()
