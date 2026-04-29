# 📊 Módulo: Teoría de Decisiones de Bayes

## Contexto General

Este módulo analiza decisiones empresariales bajo incertidumbre utilizando la **Teoría de Bayes**. Es fundamental para la evaluación del **PETI 2025-2028** porque permite cuantificar cómo la información adicional (estudios de mercado, pruebas técnicas) mejora la calidad de las decisiones de inversión tecnológica.

---

## Estructura del módulo

### 1. **Variables** (Tab 1)
Definición de los elementos básicos del problema:

- **Estados de la naturaleza**: dos escenarios posibles (S1, S2)
  - Ejemplo: S1 = "Demanda sostenible", S2 = "Baja demanda"
- **Probabilidades previas**: P(S1), P(S2)
- **Información muestral**: P(F|S1), P(F|S2)
  - F puede ser resultado favorable o desfavorable de un estudio
- **Alternativas**: conjunto de decisiones posibles (A1, A2, A3...)
- **Tabla de pagos**: matriz de resultados (ganancias/costos) para cada (alternativa, estado)

### 2. **Tablas** (Tab 2)
Cálculos de probabilidades bayesianas:

| Tabla | Significado |
|-------|-------------|
| **Tabla de pagos** | Matriz de resultados brutos |
| **Enfoque Optimista (MAXIMAX)** | Mejor caso: max de lo máximo por alternativa |
| **Enfoque Conservador (MAXIMIN)** | Peor caso: max de lo mínimo por alternativa |
| **Máx Arrepentimiento (Regret)** | Minimizar el máximo arrepentimiento |
| **Valor Esperado (EV)** | Media ponderada por probabilidades previas |
| **Probabilidades Bayesianas** | Cálculos de P(F), P(U), P(S\|F), P(S\|U) |
| **EV Muestral (EV\|F, EV\|U)** | VE condicional si se realiza el estudio |

### 3. **Árbol de Bayes** (Tab 3)
Visualización gráfica del árbol de decisión:
- Nodos de decisión (cuadrados): donde el decisor elige alternativa
- Nodos de azar (círculos): donde ocurren estados inciertos
- Ramas etiquetadas con probabilidades
- Hojas con valores de pago final

### 4. **Gráficas** (Tab 4)
**Análisis de sensibilidad**: mostrar cómo varía el valor esperado cuando cambia P(S1):
- Línea por alternativa
- Intersecciones entre líneas = puntos de indiferencia
- Marcador en P(S1) actual

### 5. **Resumen** (Tab 5)
Síntesis ejecutiva con KPIs clave:

| Métrica | Significado |
|---------|-------------|
| **VE óptimo sin info** | Mejor valor esperado antes de estudiar |
| **VE con estudio** | Valor esperado después de estudiar |
| **EVwPI** | Valor esperado con información perfecta (cota superior) |
| **EVPI** | Máximo a pagar por información perfecta |
| **EVSI** | Máximo a pagar por el estudio muestral |
| **Eficiencia** | EVSI / EVPI (qué tan bueno es el estudio) |

---

## Fórmulas clave

```
P(F) = P(F|S1)·P(S1) + P(F|S2)·P(S2)                    [Ley total de probabilidad]

P(S1|F) = P(F|S1)·P(S1) / P(F)                          [Teorema de Bayes]

EV(Ai) = Σ V(Ai, Sj) · P(Sj)                           [Valor esperado]

VE Muestral = EV|F · P(F) + EV|U · P(U)                [VE con estudio]

EVPI = EVwPI - EV(óptima)                              [Valor perfecto]

EVSI = VE Muestral - EV(óptima)                        [Valor del estudio]
```

---

## Requisitos actuales

### Entradas
- Dos estados de naturaleza con etiquetas y probabilidades
- Cuatro probabilidades condicionales P(F|S1), P(F|S2), P(U|S1), P(U|S2)
- Lista de alternativas (editable)
- Tabla de pagos (editable celdas por celdas)

### Salidas
- 6 tablas de análisis
- 1 árbol de decisión (imagen PNG renderizada con D3/graphviz)
- 1 gráfica interactiva (Plotly)
- Resumen con 8 KPIs

### Stack actual
- **Backend**: Flask + Python (compute.py, tree_render.py, routes.py)
- **Frontend**: HTML + Bootstrap 5 + Plotly.js + D3.js v7
- **Renderizado de árbol**: graphviz → PNG → data:image

---

## Casos de uso

1. **Análisis de inversión**: ¿Invertir en tecnología o no? ¿Hacer estudio de mercado primero?
2. **Análisis de riesgo**: Comparar alternativas bajo diferentes escenarios
3. **Valuación de información**: ¿Cuánto pagar por un estudio de mercado?
4. **Enseñanza**: Demostración interactiva de teoría bayesiana

---

## Notas técnicas

- El árbol se genera dinámicamente en Python usando `tree_render.py`
- La tabla de pagos es completamente editable — los cálculos se actualizan en tiempo real
- El análisis de sensibilidad se recalcula cuando cambia P(S1)
- Todos los valores son formatreados a 4 decimales
- El módulo es 100% vanilla JS — sin frameworks
