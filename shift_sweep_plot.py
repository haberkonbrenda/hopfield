# shift_sweep_plot.py
# Lee out_shift_*/results.csv, calcula exactitud y error de centro promedios y grafica vs shift.
import sys, os, re, csv, glob
import matplotlib.pyplot as plt

def read_metrics(csv_path):
    oks, total = 0, 0
    errs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            total += 1
            try: oks += int(row["ok_match"])
            except: pass
            try: errs.append(float(row["center_err"]))
            except: pass
    acc = (oks/total) if total else float('nan')
    avg_err = sum(errs)/len(errs) if errs else float('nan')
    return acc, avg_err

def main():
    folders = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob("out_shift_*"))
    rx = re.compile(r"out_shift_([0-9]+)$")
    xs, accs, cerrs = [], [], []
    for folder in folders:
        m = rx.search(folder)
        if not m: continue
        shift = int(m.group(1))
        csv_path = os.path.join(folder, "results.csv")
        if not os.path.isfile(csv_path): continue
        acc, avg_err = read_metrics(csv_path)
        xs.append(shift); accs.append(acc); cerrs.append(avg_err)

    pairs = sorted(zip(xs, accs, cerrs), key=lambda t: t[0])
    if not pairs:
        print("No se encontraron resultados out_shift_*/results.csv")
        sys.exit(1)
    xs = [p[0] for p in pairs]; accs = [p[1] for p in pairs]; cerrs = [p[2] for p in pairs]

    # Exactitud vs shift
    plt.figure()
    plt.title("Robustez al desplazamiento – Hopfield (pinv)")
    plt.plot(xs, accs, marker='o')
    plt.xlabel("Shift máximo (px)")
    plt.ylabel("Exactitud promedio (ok_match)")
    plt.ylim(0.0, 1.05)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("shift_vs_accuracy.png")

    # Error de centro vs shift
    plt.figure()
    plt.title("Error de centro vs. shift")
    plt.plot(xs, cerrs, marker='o')
    plt.xlabel("Shift máximo (px)")
    plt.ylabel("Error de centro promedio (px)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("shift_vs_center_error.png")

    print("Guardados: shift_vs_accuracy.png, shift_vs_center_error.png")
    print("Shift\tAcc\tCenterErr")
    for s, acc, ce in zip(xs, accs, cerrs):
        print(f"{s}\t{acc:.3f}\t{ce:.3f}")

if __name__ == "__main__":
    main()
