# Hopfield para limpieza/completado de sellos circulares (tapas)
# Autor: Brenda Haberkon
# Requisitos: numpy (obligatorio). matplotlib (solo para gráficos, opcional).

import numpy as np
import math
import os
import argparse

# ---------- Utilidades básicas ----------

def to_bipolar(img_bin):
    """0/1 -> -1/+1 (vector int8)."""
    return np.where(img_bin > 0, 1, -1).astype(np.int8).ravel()

def from_bipolar(x, N):
    """-1/+1 -> 0/1 imagen NxN."""
    return (x.reshape(N, N) > 0).astype(np.uint8)

def ring_template(N, r_in, r_out, cx=None, cy=None):
    """Plantilla de anillo binaria NxN (1=anillo, 0=fondo)."""
    if cx is None: cx = (N - 1) / 2.0
    if cy is None: cy = (N - 1) / 2.0
    Y, X = np.ogrid[:N, :N]
    R = np.sqrt((X - cx)**2 + (Y - cy)**2)
    return ((R >= r_in) & (R <= r_out)).astype(np.uint8)

def add_salt_pepper(img, p):
    """Invierte una fracción p de píxeles (ruido sal/pimienta)."""
    out = img.copy()
    n = out.size
    k = int(round(p * n))
    idx = np.random.choice(n, size=k, replace=False)
    flat = out.ravel()
    flat[idx] = 1 - flat[idx]
    return out

def remove_ring_arc(img, frac=0.15):
    """Elimina un arco contiguo del anillo (aprox. frac del perímetro)."""
    N = img.shape[0]
    Y, X = np.mgrid[0:N, 0:N]
    cx = cy = (N - 1) / 2.0
    theta = np.arctan2(Y - cy, X - cx)  # [-pi, pi]
    window = frac * 2.0 * math.pi
    start = np.random.uniform(-math.pi, math.pi - window)
    mask_arc = (theta >= start) & (theta <= (start + window))
    out = img.copy()
    out[(img == 1) & (mask_arc)] = 0
    return out

def shift_image(img, dx, dy):
    """Desplaza con roll y rellena de 0 los bordes entrantes."""
    out = np.roll(np.roll(img, dy, axis=0), dx, axis=1)
    if dx > 0:   out[:, :dx] = 0
    elif dx < 0: out[:, dx:] = 0
    if dy > 0:   out[:dy, :] = 0
    elif dy < 0: out[dy:, :] = 0
    return out

def centroid(binary_img):
    """Centroide (cx, cy) en float; NaN si vacío."""
    ys, xs = np.nonzero(binary_img)
    if xs.size == 0: return float('nan'), float('nan')
    return xs.mean(), ys.mean()

def hamming_distance(x, y):
    """Distancia de Hamming entre vectores bipolares (-1/+1)."""
    return int(np.sum(x != y))

def to_pgm_ascii(path, img):
    """Guarda imagen 0/1 o 0/255 como PGM ASCII (P2), sin librerías externas."""
    arr = img.astype(np.uint8)
    if arr.max() == 1:
        arr = arr * 255
    h, w = arr.shape
    with open(path, 'w') as f:
        f.write("P2\n")
        f.write(f"{w} {h}\n255\n")
        for row in arr:
            f.write(" ".join(str(int(v)) for v in row) + "\n")

# ---------- Hopfield ----------

def train_hebb(U):
    """
    Entrenamiento Hebb: U es (n x q) con columnas bipolares.
    Capacidad típica ~ 0.14*n (si patrones poco correlacionados).
    """
    n, q = U.shape
    W = U @ U.T - q * np.eye(n)
    np.fill_diagonal(W, 0.0)
    return W

def train_pinv(U):
    """
    Entrenamiento por pseudoinversa: W = U (U^T U)^-1 U^T.
    Tolera patrones correlacionados. Capacidad típica ~ 0.5*n.
    """
    G = U.T @ U
    W = U @ np.linalg.inv(G) @ U.T
    np.fill_diagonal(W, 0.0)
    return W

def recall(W, x0, max_iter=50, async_update=True, track_energy=True):
    """
    Dinámica de recuperación. Devuelve x_rec y la trayectoria de energía.
    """
    x = x0.copy()
    n = x.size
    energies = []
    for _ in range(max_iter):
        if async_update:
            for i in np.random.permutation(n):
                s = W[i, :] @ x
                x[i] = 1 if s >= 0 else -1
        else:
            x = np.where((W @ x) >= 0, 1, -1).astype(x.dtype)
        if track_energy:
            E = -0.5 * x @ (W @ x)
            energies.append(float(E))
            if len(energies) > 1 and energies[-1] == energies[-2]:
                break
    return x, energies

# ---------- Generacion / Evaluación ----------

def generate_templates(N=64, q=5, r0=12, dr=3, t=3):
    """q plantillas de anillos con radios/grosores crecientes."""
    templates = []
    for k in range(q):
        r_in  = r0 + k * dr
        r_out = r_in + t
        templates.append(ring_template(N, r_in, r_out))
    return templates

def degrade(img, noise_p=0.2, arc_frac=0.15, shift_px=3):
    """Aplica ruido + elimina arco + desplaza la imagen."""
    out = img.copy()
    if noise_p > 0:
        out = add_salt_pepper(out, noise_p)
    if arc_frac > 0:
        out = remove_ring_arc(out, arc_frac)
    if shift_px != 0:
        out = shift_image(
            out,
            dx=np.random.randint(-shift_px, shift_px + 1),
            dy=np.random.randint(-shift_px, shift_px + 1)
        )
    return out

def evaluate_once(N=64, q=5, noise_p=0.2, arc_frac=0.15, shift_px=3, method="pinv"):
    """
    Corre una prueba: entrena, degrada una plantilla, recupera y mide.
    Devuelve dict con artefactos y métricas.
    """
    templates = generate_templates(N=N, q=q)
    U = np.column_stack([to_bipolar(t) for t in templates])  # (n x q)

    if method == "hebb":
        W = train_hebb(U)
    else:
        W = train_pinv(U)

    k = np.random.randint(q)
    clean = templates[k]
    noisy = degrade(clean, noise_p=noise_p, arc_frac=arc_frac, shift_px=shift_px)

    x0 = to_bipolar(noisy)
    x_rec, energies = recall(W, x0, max_iter=50, async_update=True, track_energy=True)
    recovered = from_bipolar(x_rec, N)

    # Métrica 1: ¿se recupera la misma plantilla? (menor Hamming)
    dists = [hamming_distance(x_rec, U[:, i]) for i in range(q)]
    idx_best = int(np.argmin(dists))
    ok_match = int(idx_best == k)

    # Métrica 2: error de centroide vs centro ideal (N-1)/2
    cx_r, cy_r = centroid(recovered)
    cx_true = cy_true = (N - 1) / 2.0
    center_err = float(math.hypot(cx_r - cx_true, cy_r - cy_true))

    return {
        "templates": templates,
        "chosen_index": int(k),
        "noisy": noisy,
        "recovered": recovered,
        "energies": energies,
        "best_index": idx_best,
        "ok_match": ok_match,
        "center_err": center_err,
        "W": W,
    }

# ---------- CLI / Main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=64)
    ap.add_argument("--q", type=int, default=5)
    ap.add_argument("--noise", type=float, default=0.2)
    ap.add_argument("--arc", type=float, default=0.15)
    ap.add_argument("--shift", type=int, default=3)
    ap.add_argument("--method", type=str, default="pinv", choices=["pinv","hebb"])
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--outdir", type=str, default="out")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Lote de experimentos -> CSV
    csv_path = os.path.join(args.outdir, "results.csv")
    with open(csv_path, "w") as f:
        f.write("run,method,ok_match,center_err,final_energy\n")
        for r in range(args.runs):
            res = evaluate_once(
                N=args.N, q=args.q, noise_p=args.noise,
                arc_frac=args.arc, shift_px=args.shift, method=args.method
            )
            finE = res["energies"][-1] if res["energies"] else float("nan")
            f.write(f"{r},{args.method},{res['ok_match']},{res['center_err']:.4f},{finE:.4f}\n")

    # Un caso con imágenes y curva de energía
    res = evaluate_once(
        N=args.N, q=args.q, noise_p=args.noise,
        arc_frac=args.arc, shift_px=args.shift, method=args.method
    )
    # Guardar PGM (sin libs)
    to_pgm_ascii(os.path.join(args.outdir, "sample_clean.pgm"),     res["templates"][res["chosen_index"]])
    to_pgm_ascii(os.path.join(args.outdir, "sample_noisy.pgm"),     res["noisy"])
    to_pgm_ascii(os.path.join(args.outdir, "sample_recovered.pgm"), res["recovered"])

    # Figuras (si está matplotlib)
    try:
        import matplotlib.pyplot as plt
        # Energía
        plt.figure()
        plt.title("Energy vs Iteration")
        plt.plot(res["energies"])
        plt.xlabel("Iteration"); plt.ylabel("Energy"); plt.tight_layout()
        plt.savefig(os.path.join(args.outdir, "energy.png"))
        plt.close()
        # Imágenes (una por figura; sin especificar colores)
        def save_img(path, img, title):
            plt.figure(); plt.title(title)
            plt.imshow(img, interpolation="nearest"); plt.axis("off"); plt.tight_layout()
            plt.savefig(path); plt.close()
        save_img(os.path.join(args.outdir, "img_clean.png"),     res["templates"][res["chosen_index"]], "Clean Template")
        save_img(os.path.join(args.outdir, "img_noisy.png"),     res["noisy"],                        "Noisy Input")
        save_img(os.path.join(args.outdir, "img_recovered.png"), res["recovered"],                    "Recovered Output")
    except Exception as e:
        # Si no hay matplotlib, no graficamos; quedan PGM y CSV
        pass

    print("OK. Artefactos en:", args.outdir)

if __name__ == "__main__":
    main()
