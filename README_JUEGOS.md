# ♟️ Módulo: Teoría de Juegos — Negociación Estratégica

## Contexto empresarial

Este módulo modela la **negociación estratégica entre JW (empresa) y el sindicato de trabajadores** en el marco del **PETI 2025-2028**. El análisis determina:

- La viabilidad de la **Alternativa B (Inversión Media — Proyecto TI-01)**
- El nivel de adopción digital esperado
- El valor en juego de la negociación: **V ≈ 17.5 millones de COP**

Se trata de un **juego de suma cero** (lo que gana JW, lo pierde el sindicato) resuelto mediante **reducción por dominancia** e **indifference equations** para estrategias mixtas.

---

## Estructura del módulo

### 1. **Matriz de pagos**
- **Filas** = Estrategias de JW (E1, E2, E3, E4)
- **Columnas** = Estrategias del Sindicato (U1, U2, U3, U4)
- **Celdas** = Pago en millones de COP (perspectiva de JW)
- **Editable**: usuario puede cambiar valores, etiquetas, agregar/quitar estrategias

**Matriz predeterminada:**
```
        U1   U2   U3   U4
E1      10   30   25   15
E2       5   40   10   30
E3      15   25    5   10
E4      20   20   15   40
```

### 2. **Reducción por dominancia**
Pasos iterativos que eliminan estrategias subóptimas:

- **Estrategia dominada (Sindicato/minimizador)**: columna A domina B si A[i] ≤ B[i] para todas las filas
- **Estrategia dominada (JW/maximizador)**: fila A domina B si A[j] ≥ B[j] para todas las columnas

**Resultado esperado** (matriz predeterminada):
```
Paso 1: Columna U2 dominada por U4 → elimina U2
Paso 2: Columna U3 dominada por U4 → elimina U3
Matriz reducida final: 2×2 (E1,E4 × U1,U4)
```

### 3. **Estrategias mixtas óptimas**
Después de reducir a 2×2, se calculan probabilidades usando **ecuaciones de indiferencia**:

**Para el sindicato** (minimizador):
```
q = (d - b) / (a - b - c + d)   donde matriz es [[a,b],[c,d]]
p = (d - c) / (a - b - c + d)
V = a·p + c·(1-p)
```

Donde:
- `p` = P(JW juega fila 1)
- `q` = P(Sindicato juega columna 1)
- `V` = Valor del juego (mismo para ambos)

**Resultado esperado** (matriz 2×2 reducida):
- p = 0.50 (JW mezcla E1 y E4 al 50%)
- q = 0.25 (Sindicato mezcla U1 (25%) y U4 (75%))
- V = 17.5 M COP

### 4. **Gráfica de dominancia — Estrategias mixtas**
Visualización de 4 líneas en [0,1]:

**Líneas azules** (Sindicato — ambas columnas como función de p):
- U1: va de 10 (p=0) a 20 (p=1)
- U4: va de 25 (p=0) a 15 (p=1)
- Intersección en p* = 0.75, V = 17.5

**Líneas moradas** (JW — ambas filas como función de q):
- E1: va de 10 (q=0) a 25 (q=1)
- E4: va de 20 (q=0) a 15 (q=1)
- Intersección en q* = 0.5, V = 17.5

### 5. **Conclusión estratégica**
Texto ejecutivo explicando:
- Valor de equilibrio de Nash mixto
- Probabilidades óptimas de cada jugador
- Implicación para la implementación del PETI 2025-2028

---

## Fórmulas clave

```
Dominancia (columna A domina B para minimizador):
  ∀i: A[i] ≤ B[i]  →  elimina B

Dominancia (fila A domina B para maximizador):
  ∀j: A[j] ≥ B[j]  →  elimina B

Indifference (jugador 2 indiferente ante ambas columnas):
  c1[i]·p + c1[j]·(1-p) = c2[i]·p + c2[j]·(1-p)

Valor del juego:
  V = a·p + c·(1-p)  donde [[a,b],[c,d]] es matriz reducida 2×2
```

---

## Requisitos actuales

### Entradas
- Matriz de pagos (configurable)
- Etiquetas de estrategias JW (filas)
- Etiquetas de estrategias Sindicato (columnas)
- Botones "+ Estrategia JW" y "+ Estrategia Sindicato" para expandir

### Salidas
- Matriz original renderizada
- **Pasos de dominancia eliminados** (mejora: mostrar cada paso)
- Matriz reducida final
- Tabla de estrategias mixtas óptimas
- Gráfica de 4 líneas con intersecciones
- Conclusión textual

### Stack actual
- **Backend**: Flask + Python (game_theory.py)
  - `iterated_dominance()`: reduce por dominancia
  - `solve_2x2_mixed()`: ecuaciones de indiferencia
  - `compute_game_theory()`: orquestador
- **Frontend**: HTML + Bootstrap 5 + Plotly.js
- **Cálculos**: numpy arrays, lógica pura sin estado

---

## Casos de uso

1. **Negociación empresarial**: predicción de puntos de equilibrio
2. **Análisis de competencia**: modelos duopólicos
3. **Enseñanza de teoría de juegos**: interactividad + visualización
4. **Valuación de decisiones**: impacto de diferentes estrategias mixtas

---

## Limitaciones actuales

- Solo resuelve 2×2 después de dominancia (no LP para matrices mayores)
- Suma cero (no soporta juegos no-cooperativos generales)
- Edición de matriz sin guardar histórico de cambios

---

## Notas técnicas

- **numpy.float64**: convertido a float nativo con `.tolist()`
- **Rendering**: Plotly con shapes (líneas vertical/horizontal) + annotations
- **Validación**: chequea si denom = 0 (juego degenerado)
- **UI**: tablas HTML editables, botones dinámicos +/- filas/columnas
