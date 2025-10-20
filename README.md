# Hopfield Tapas - Limpieza y centrado de sellos circulares

Prototipo didactico que usa una red de Hopfield como memoria autoasociativa para limpiar/completar el sello circular (anillo) de una tapa a partir de imagenes degradadas (ruido, partes faltantes, desplazamiento). Luego de la recuperacion, se estima el centro (X,Y) y se evalua un criterio simple de OK/NO-OK por tolerancia de descentramiento. 
Todo el tratamiento de imagenes esta escrito a mano con NumPy (algebra). Los graficos son opcionales con matplotlib.

---

## Conceptos

- Hopfield: red recurrente que "recuerda" patrones guardados. Si le das un patron ruidoso, minimiza su energia y converge al punto fijo mas cercano (la plantilla "limpia").
- Hebb vs. Pseudoinversa:
  - Hebb: simple, prefiere patrones poco correlacionados. Capacidad tipica ~= 0.14 * n (n = N^2).
  - Pseudoinversa (pinv): tolera patrones parecidos. Capacidad tipica ~= 0.5 * n.

---

## Requisitos

- Python 3.9+
- Obligatorio: `numpy`
- Opcional: `matplotlib` (solo para guardar *.png; si no esta, se generan igual PGM y CSV)

Instalacion minima:

    pip install numpy matplotlib

> Si no queres graficos, podes omitir matplotlib.

---

# Estructura del repositorio

- tp3_hopfield.py
    - Script principal. Genera plantillas (anillos), entrena W (Hebb o pseudoinversa), degrada imágenes (ruido, arco faltante, desplazamiento), recupera con Hopfield y exporta resultados (CSV, PGM y, si hay matplotlib, PNG).

- Scripts de resultados (gráficos)
  - `noise_sweep_plot.py`: lee `out_noise_*`/`results.csv` y genera `noise_vs_accuracy.png` + tabla en consola.
  - `arc_sweep_plot.py`: lee `out_arc_*`/`results.csv` y genera `arc_vs_accuracy.png`, `arc_vs_center_error.png` + tabla.
  - `shift_sweep_plot.py`: lee `out_shift_*`/`results.csv` y genera `shift_vs_accuracy.png`, `shift_vs_center_error.png` + tabla.
  - `hebb_vs_pinv_plot.py`: compara Hebb vs Pseudoinversa a lo largo de ruido; produce `hebb_pinv_accuracy_vs_noise.png`, `hebb_pinv_center_err_vs_noise.png` + tabla.

---

## Uso 

Generar 10 corridas con pseudoinversa y guardar todo en `out_pinv`:

    python tp3_hopfield.py --N 64 --q 5 --noise 0.20 --arc 0.15 --shift 3 --method pinv --runs 10 --outdir out_pinv

Comparar con Hebb:

    python tp3_hopfield.py --N 64 --q 5 --noise 0.20 --arc 0.15 --shift 3 --method hebb --runs 10 --outdir out_hebb

### Que se genera?
En cada `--outdir`:

- `results.csv` -> una fila por corrida con: `run, method, ok_match, center_err, final_energy`
  - `ok_match`: 1 si la recuperacion coincide con la plantilla elegida.
  - `center_err`: error del centroide (px) respecto del centro ideal.
  - `final_energy`: energia en la ultima iteracion (debe tender a bajar).
- `sample_clean.pgm`, `sample_noisy.pgm`, `sample_recovered.pgm` -> imagenes ASCII PGM hechas a mano (visibles en cualquier visor).
- (Si tenes matplotlib) `energy.png` (curva energia vs. iteracion), `img_clean.png`, `img_noisy.png`, `img_recovered.png`.

---

## Parametros

- `--N` (int, default 64): tamano de imagen N x N.
  - Nota: a mayor N, mas detalle pero W crece como N^2 x N^2.
- `--q` (int, default 5): cantidad de plantillas guardadas (anillos con radios/grosores distintos).
- `--noise` (float [0..1], default 0.20): fraccion de pixeles invertidos (ruido sal/pimienta).
- `--arc` (float [0..1], default 0.15): fraccion de perimetro del anillo que se borra como "segmento faltante".
- `--shift` (int, default 3): desplazamiento maximo aleatorio (en pixeles) en X e Y.
- `--method` (pinv | hebb, default pinv): metodo de entrenamiento de W.
- `--runs` (int, default 10): numero de corridas para poblar el CSV.
- `--outdir` (str, default out): carpeta de salida.

---

## Como funciona (resumen tecnico)

1. Plantillas: se generan q anillos (variando radio/grosor).
2. Entrenamiento:
   - Hebb: W = sum(x x^T) - q*I
   - Pseudoinversa: W = U (U^T U)^-1 U^T
3. Degradacion: se toma una plantilla y se arruina con --noise, --arc, --shift.
4. Recuperacion: actualizacion asincrona y calculo de energia E = -1/2 x^T W x por iteracion.
5. Metricas:
   - ok_match (Hamming minimo con alguna plantilla guardada),
   - center_err (distancia del centroide recuperado al centro ideal).

---

## Limitaciones y alcance

- Matriz W de tamano N^2 x N^2 -> crecer N impacta memoria/tiempo.
- Sin normalizacion previa, hay sensibilidad a rotacion/escala.
- Hebb se degrada con patrones muy parecidos; pinv tolera mejor correlacion.

---

## Cómo generar resultados y gráficos 

A continuación se indican los comandos para crear las carpetas `out_*` (cada una con su `results.csv` e imágenes de ejemplo) y luego graficar/obtener promedios con los scripts de apoyo. Los ejemplos asumen `N=64`, `q=5`, `arc=0.15`, `shift=3`, `runs=30`.

**Requisitos:** `python`, `numpy` (obligatorio) y `matplotlib` (para gráficos).

---

## 1) Barrido de **ruido** → `out_noise_*` + `noise_vs_accuracy.png`

**Linux/macOS (Bash):**
```bash
for n in 0.00 0.05 0.10 0.15 0.20 0.25 0.30; do
  python tp3_hopfield.py --N 64 --q 5 --noise $n --arc 0.15 --shift 3 \
    --method pinv --runs 30 --outdir out_noise_${n}
done
python noise_sweep_plot.py
```

**Windows (PowerShell):**
```powershell
$nlevels = 0.00,0.05,0.10,0.15,0.20,0.25,0.30
foreach ($n in $nlevels) {
  $out = ("out_noise_{0:N2}" -f $n) -replace ',', '.'
  python tp3_hopfield.py --N 64 --q 5 --noise $n --arc 0.15 --shift 3 `
    --method pinv --runs 30 --outdir $out
}
python noise_sweep_plot.py
```

**Salida:** `noise_vs_accuracy.png` y una tabla “Ruido vs Exactitud” en consola.

---

## 2) Barrido de **faltantes (arco)** → `out_arc_*` + `arc_vs_*.png`

**Linux/macOS (Bash):**
```bash
for a in 0.00 0.05 0.10 0.15 0.20 0.25 0.30 0.35; do
  python tp3_hopfield.py --N 64 --q 5 --noise 0.20 --arc $a --shift 3 \
    --method pinv --runs 30 --outdir out_arc_${a}
done
python arc_sweep_plot.py
```

**Windows (PowerShell):**
```powershell
$alevels = 0.00,0.05,0.10,0.15,0.20,0.25,0.30,0.35
foreach ($a in $alevels) {
  $out = ("out_arc_{0:N2}" -f $a) -replace ',', '.'
  python tp3_hopfield.py --N 64 --q 5 --noise 0.20 --arc $a --shift 3 `
    --method pinv --runs 30 --outdir $out
}
python arc_sweep_plot.py
```

**Salida:** `arc_vs_accuracy.png`, `arc_vs_center_error.png` y tabla “Arco – Acc – CenterErr” en consola.

---

## 3) Barrido de **desplazamiento (shift)** → `out_shift_*` + `shift_vs_*.png`

**Linux/macOS (Bash):**
```bash
for s in 0 1 2 3 4 5 6; do
  python tp3_hopfield.py --N 64 --q 5 --noise 0.20 --arc 0.15 --shift $s \
    --method pinv --runs 30 --outdir out_shift_${s}
done
python shift_sweep_plot.py
```

**Windows (PowerShell):**
```powershell
$shifts = 0,1,2,3,4,5,6
foreach ($s in $shifts) {
  $out = "out_shift_$s"
  python tp3_hopfield.py --N 64 --q 5 --noise 0.20 --arc 0.15 --shift $s `
    --method pinv --runs 30 --outdir $out
}
python shift_sweep_plot.py
```

**Salida:** `shift_vs_accuracy.png`, `shift_vs_center_error.png` y tabla “Shift – Acc – CenterErr” en consola.

---

## 4) **Comparación Hebb vs. Pseudoinversa** (vs. ruido) → `hebb_pinv_*.png`

Generá primero ambas series:

**Linux/macOS (Bash):**
```bash
# Pseudoinversa
for n in 0.00 0.05 0.10 0.15 0.20 0.25 0.30; do
  python tp3_hopfield.py --N 64 --q 5 --noise $n --arc 0.15 --shift 3 \
    --method pinv --runs 30 --outdir out_pinv_noise_${n}
done
# Hebb
for n in 0.00 0.05 0.10 0.15 0.20 0.25 0.30; do
  python tp3_hopfield.py --N 64 --q 5 --noise $n --arc 0.15 --shift 3 \
    --method hebb --runs 30 --outdir out_hebb_noise_${n}
done
python hebb_vs_pinv_plot.py
```

**Windows (PowerShell):**
```powershell
$nlevels = 0.00,0.05,0.10,0.15,0.20,0.25,0.30
# Pseudoinversa
foreach ($n in $nlevels) {
  $out = ("out_pinv_noise_{0:N2}" -f $n) -replace ',', '.'
  python tp3_hopfield.py --N 64 --q 5 --noise $n --arc 0.15 --shift 3 `
    --method pinv --runs 30 --outdir $out
}
# Hebb
foreach ($n in $nlevels) {
  $out = ("out_hebb_noise_{0:N2}" -f $n) -replace ',', '.'
  python tp3_hopfield.py --N 64 --q 5 --noise $n --arc 0.15 --shift 3 `
    --method hebb --runs 30 --outdir $out
}
python hebb_vs_pinv_plot.py
```

**Salida:** `hebb_pinv_accuracy_vs_noise.png`, `hebb_pinv_center_err_vs_noise.png` y tabla “Ruido – Acc_pinv – Acc_hebb – CE_pinv – CE_hebb” en consola.

---

### Nota
- Si cambiás `N`, `q`, `runs` o los rangos de barrido, mantené el **prefijo de carpeta** (por ejemplo, `out_noise_*`) para que los scripts de graficado las detecten automáticamente.

