# noise_sweep_plot.py
# Lee out_noise_*/results.csv, calcula exactitud promedio y dibuja Exactitud vs. Ruido

import sys, os, re, csv, glob
import math
import matplotlib.pyplot as plt

def read_accuracy(csv_path):
    oks = 0
    total = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            total += 1
            try:
                oks += int(row["ok_match"])
            except Exception:
                pass
    return (oks/total) if total else float('nan')

def main():
    # Permitir pasar carpetas por argv o usar glob por defecto
    if len(sys.argv) > 1:
        folders = sys.argv[1:]
    else:
        folders = sorted(glob.glob("out_noise_*"))

    noise_vals = []
    acc_vals = []

    # Extraer el nivel de ruido desde el nombre de carpeta (out_noise_X.XX)
    rx = re.compile(r"out_noise_([0-9]+\.[0-9]+)$")

    for folder in folders:
        m = rx.search(folder)
        if not m:
            continue
        noise = float(m.group(1))
        csv_path = os.path.join(folder, "results.csv")
        if not os.path.isfile(csv_path):
            continue
        acc = read_accuracy(csv_path)
        noise_vals.append(noise)
        acc_vals.append(acc)

    # Ordenar por nivel de ruido
    pairs = sorted(zip(noise_vals, acc_vals), key=lambda x: x[0])
    if not pairs:
        print("No se encontraron resultados. Pasá carpetas explícitas o corré primero tp3_hopfield.py.")
        sys.exit(1)

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    # Plot (una figura, sin estilos ni colores explícitos)
    plt.figure()
    plt.title("Robustez al ruido – Hopfield (pinv)")
    plt.plot(xs, ys, marker='o')  # un solo gráfico, sin setear colores
    plt.xlabel("Ruido sal/pimienta (fracción)")
    plt.ylabel("Exactitud promedio (ok_match)")
    plt.ylim(0.0, 1.05)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("noise_vs_accuracy.png")
    # También imprimir tabla simple
    print("Ruido\tExactitud")
    for x, y in zip(xs, ys):
        print(f"{x:.2f}\t{y:.3f}")
    print("Guardado: noise_vs_accuracy.png")

if __name__ == "__main__":
    main()
