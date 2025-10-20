# hebb_vs_pinv_plot.py
# Compara Hebb vs Pseudoinversa a lo largo de distintos niveles de ruido.
# Genera:
#  - hebb_pinv_accuracy_vs_noise.png
#  - hebb_pinv_center_err_vs_noise.png

import os, re, csv, glob
import matplotlib.pyplot as plt

def read_metrics(csv_path):
    oks, total = 0, 0
    cerrs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            total += 1
            try: oks += int(row["ok_match"])
            except: pass
            try: cerrs.append(float(row["center_err"]))
            except: pass
    acc = (oks/total) if total else float('nan')
    avg_ce = sum(cerrs)/len(cerrs) if cerrs else float('nan')
    return acc, avg_ce

def collect(series_glob, rx):
    xs, accs, ces = [], [], []
    for folder in sorted(glob.glob(series_glob)):
        m = rx.search(folder)
        if not m: continue
        noise = float(m.group(1))
        csv_path = os.path.join(folder, "results.csv")
        if not os.path.isfile(csv_path): continue
        acc, ce = read_metrics(csv_path)
        xs.append(noise); accs.append(acc); ces.append(ce)
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    xs = [xs[i] for i in order]
    accs = [accs[i] for i in order]
    ces = [ces[i] for i in order]
    return xs, accs, ces

def main():
    rx = re.compile(r"([0-9]+\.[0-9]+)$")

    # Colectar pinv
    xs_p, acc_p, ce_p = collect("out_pinv_noise_*", rx)
    # Colectar hebb
    xs_h, acc_h, ce_h = collect("out_hebb_noise_*", rx)

    if not xs_p or not xs_h:
        print("No se encontraron carpetas out_pinv_noise_* y/o out_hebb_noise_*. Corré primero los barridos.")
        return

    # Asegurar que comparo mismas x (ruidos)
    # Si hay diferencias, intersecto
    X = sorted(set(xs_p).intersection(xs_h))
    if not X:
        print("No hay intersección de niveles de ruido entre ambas series.")
        return

    def align(xs, ys):
        m = {x:y for x,y in zip(xs, ys)}
        return [m.get(x, float('nan')) for x in X]

    A_p = align(xs_p, acc_p); C_p = align(xs_p, ce_p)
    A_h = align(xs_h, acc_h); C_h = align(xs_h, ce_h)

    # Figura: Exactitud vs ruido (dos curvas)
    plt.figure()
    plt.title("Hebb vs Pseudoinversa – Exactitud vs. ruido")
    plt.plot(X, A_p, marker='o', label="Pseudoinversa")
    plt.plot(X, A_h, marker='s', label="Hebb")
    plt.xlabel("Ruido sal/pimienta (fracción)")
    plt.ylabel("Exactitud promedio (ok_match)")
    plt.ylim(0.0, 1.05)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig("hebb_pinv_accuracy_vs_noise.png")

    # Figura: Error de centro vs ruido (dos curvas)
    plt.figure()
    plt.title("Hebb vs Pseudoinversa – Error de centro vs. ruido")
    plt.plot(X, C_p, marker='o', label="Pseudoinversa")
    plt.plot(X, C_h, marker='s', label="Hebb")
    plt.xlabel("Ruido sal/pimienta (fracción)")
    plt.ylabel("Error de centro promedio (px)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig("hebb_pinv_center_err_vs_noise.png")

    # Consola: tabla rápida
    print("Ruido\tAcc_pinv\tAcc_hebb\tCE_pinv\tCE_hebb")
    for i, x in enumerate(X):
        print(f"{x:.2f}\t{A_p[i]:.3f}\t\t{A_h[i]:.3f}\t\t{C_p[i]:.3f}\t{C_h[i]:.3f}")

if __name__ == "__main__":
    main()
