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

