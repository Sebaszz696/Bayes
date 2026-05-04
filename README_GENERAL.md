# 🎓 Aplicación de Soporte a Decisiones — PETI 2025-2028

## Descripción general

Esta es una **aplicación web interactiva de análisis de decisiones empresariales** desarrollada para soportar la evaluación e implementación del **Plan Estratégico de Tecnología de la Información (PETI) 2025-2028**. Integra tres módulos especializados de investigación operativa:

1. **📊 Teoría de Decisiones de Bayes** — Análisis bajo incertidumbre
2. **♟️ Teoría de Juegos** — Negociación estratégica
3. **🚗 Líneas de Espera** — Optimización de operaciones

---

## Stack tecnológico

| Componente | Tecnología |
|-----------|-----------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML5 + Bootstrap 5 + Vanilla JS |
| **Visualización** | Plotly.js (gráficas interactivas), D3.js v7 (árbol de decisión) |
| **Matemáticas** | NumPy (Python), funciones puras (sin frameworks) |
| **Exportación** | html2pdf.js (descarga PDF) |

---

## Estructura de archivos

```
Bayes/
├── app_flask.py                 # Punto de entrada Flask
├── routes.py                    # Rutas HTTP (/compute, /compute_queueing, /compute_game_theory)
├── compute.py                   # Lógica de Teoría de Bayes
├── game_theory.py               # Lógica de Teoría de Juegos
├── queueing.py                  # Lógica de Análisis de Colas
├── tree_render.py               # Renderizado de árbol de decisión (graphviz → PNG)
├── decision_theory.py           # (Auxiliar) Cálculos avanzados de Bayes
│
├── templates/
│   └── index.html               # Interfaz única (HTML5 + Bootstrap)
│       ├── Sidebar con 3 secciones expandibles (Bayes, Juegos, Colas)
│       ├── 7 tab-panes (Variables, Tablas, Árbol, Gráficas, Resumen, Colas, Juegos)
│       └── 3 modales de glosario (1 por módulo)
│
├── static/
│   ├── css/
│   │   └── style.css            # Estilos personalizados (colores, .best-ev, .gt-eliminated, etc.)
│   └── js/
│       ├── main.js              # Lógica principal del frontend (2,000+ líneas)
│       │   ├── Bayes: getTableData(), computeAndRender(), renderTables(), renderChart()
│       │   ├── Colas: computeQueueing(), renderQueueingResults()
│       │   └── Juegos: computeGame(), renderGameResults(), renderDominanceChart()
│       └── tree-d3.js           # Renderizado D3 del árbol (si es necesario)
│
├── requirements.txt             # Dependencias Python
├── .git/                        # Control de versiones
│
├── README_GENERAL.md            # Este archivo
├── README_BAYES.md              # Documentación del módulo Bayes
├── README_COLAS.md              # Documentación del módulo Colas
└── README_JUEGOS.md             # Documentación del módulo Juegos
```

---

## Módulo 1: Teoría de Decisiones de Bayes

### Propósito
Analizar decisiones estratégicas bajo incertidumbre usando Teoría Bayesiana. Responde preguntas como:
- ¿Cuál alternativa maximiza el valor esperado?
- ¿Vale la pena realizar un estudio de mercado?
- ¿Cuánto puedo pagar por información adicional?

### Tabs (5)
1. **Variables** — Definir estados, probabilidades, tabla de pagos
2. **Tablas** — Mostrar 6 análisis de decisión
3. **Árbol de Bayes** — Visualización gráfica interactiva
4. **Gráficas** — Análisis de sensibilidad (cómo varía EV)
5. **Resumen** — Síntesis ejecutiva con KPIs

### KPIs principales
- **EV óptimo** — Mejor valor esperado sin información
- **EVPI** — Máximo a pagar por información perfecta
- **EVSI** — Máximo a pagar por el estudio
- **Eficiencia** — EVSI / EVPI × 100%

**Documentación:** Ver [README_BAYES.md](README_BAYES.md)

---

## Módulo 2: Teoría de Juegos

### Propósito
Modelar la **negociación JW vs. Sindicato** como un juego de suma cero. Determina:
- Estrategias óptimas de ambos jugadores
- Valor de equilibrio de Nash
- Viabilidad de la Alternativa B (Inversión Media)

### Funcionalidades
- **Matriz editable** — Agregar/quitar estrategias dinámicamente
- **Dominancia iterada** — Elimina estrategias subóptimas automáticamente
- **Estrategias mixtas** — Resuelve ecuaciones de indiferencia para 2×2
- **Gráfica de 4 líneas** — Visualiza payoffs vs. probabilidades mixtas
- **Conclusión contextual** — Interpretación en lenguaje de negocio

### Resultado predeterminado
- **V = 17.5 M COP** — Valor del juego
- **Sindicato:** U1 (25%), U4 (75%)
- **JW:** E1 (50%), E4 (50%)

**Documentación:** Ver [README_JUEGOS.md](README_JUEGOS.md)

---

## Módulo 3: Líneas de Espera (Teoría de Colas)

### Propósito
Evaluar impacto de inversión tecnológica en tiempos de espera. Compara:
- **Canal Simple** (M/M/1 actual) — sin inversión, μ=12
- **Canal Mejorado** (M/M/1 mejorado) — con inversión, μ=18
- **Canal Múltiple** (M/M/2) — agregar servidor, c=2

### Métricas
- **ρ** — Factor de utilización
- **P₀** — Probabilidad de sistema vacío
- **L, Lq** — Clientes en sistema y en cola
- **W, Wq** — Tiempos en sistema y en cola

### Fórmulas implementadas
- **M/M/1:** ρ = λ/μ, L = ρ/(1−ρ), W = L/λ
- **M/M/2 (Erlang-C):** c=2 fijo, P₀ = [1 + r + r²/(2(1−ρ))]⁻¹, Lq = P₀·r²·ρ/(2(1−ρ)²)

### Validación
- Alerta si ρ ≥ 1 (sistema inestable)
- Resalta mejor escenario por métrica

**Documentación:** Ver [README_COLAS.md](README_COLAS.md)

---

## Características transversales

### 1. Glosario interactivo
Cada módulo tiene un botón **"📖 Glosario"** que abre un modal con:
- **Definiciones de términos clave** (ej: EV, ρ, estrategia dominada)
- **Fórmulas asociadas**
- **Pasos de uso del módulo**

### 2. Exportación a PDF
Botón **"Descargar PDF"** en cada tab-pane. Exporta:
- Tablas, gráficas, árboles
- Conclusiones y análisis
- Formateo automático de página

### 3. Interfaz responsive
- Sidebar colapsable en móviles
- Tablas scrolleables
- Gráficas responsivas

### 4. Validación y alertas
- Validación de ρ < 1 para colas
- Alertas si matriz es degenerada (juegos)
- Mensajes de error amigables

---

## Flujo de uso típico

### Usuario empresarial
1. Abre la aplicación web
2. Selecciona módulo (Bayes, Juegos, o Colas) en la sidebar
3. Ingresa parámetros (probabilidades, matriz, λ, μ)
4. Hace clic en **"Calcular"**
5. Revisa tablas, gráficas, árbol
6. Lee conclusión y recomendaciones
7. Descargar PDF con el análisis
8. Toma decisión respecto al PETI 2025-2028

### Desarrollador
1. Modifica parámetros en las funciones Python (`compute.py`, `game_theory.py`, `queueing.py`)
2. Agrega nuevas rutas en `routes.py`
3. Actualiza `main.js` para renderizar nuevos campos
4. Actualiza `style.css` si hay nuevos estilos
5. Ejecuta tests y verifica en el navegador

---

## Requisitos para ejecutar

### Backend
```bash
pip install -r requirements.txt
python app_flask.py
```

### Navegador
- Chrome, Firefox, Edge, Safari (versión reciente)
- Soporte para ES6 (vanilla JS moderno)
- Cookies habilitadas (sesiones)

---

## Tests unitarios (Python)

Validación de fórmulas:

```python
# Bayes
from compute import compute_all
result = compute_all({'alt_names': ['A1','A2','A3'], ...})
assert result['EV'][0] > 0  # EV debe ser positivo

# Colas
from queueing import compute_queueing
result = compute_queueing({'lam': 10, 'mu_mm1_actual': 12, ...})
assert abs(result['scenarios'][0]['rho'] - 0.833) < 0.001

# Juegos
from game_theory import compute_game_theory
result = compute_game_theory({'matrix': [[10,30],[5,40]], ...})
assert abs(result['mixed_strategy']['value'] - 17.5) < 0.01
```

---

## Notas de desarrollo

### Conversión de tipos NumPy
- **Problema:** `np.float64(10.0)` aparecía en el frontend como "np.float64(10.0)"
- **Solución:** Convertir arrays a Python nativo con `.tolist()` antes de retornar en JSON

### Plotly vs. D3
- **Plotly:** Usado para gráficas interactivas (líneas, barras, intersecciones)
- **D3:** Usado para árbol de decisión (topología, nodos, bordes)

### Bootstrap + Vanilla JS
- **Modales:** `data-bs-toggle="modal"` + `data-bs-target="#id"`
- **Tabs:** `data-bs-toggle="list"` + eventos `.addEventListener('shown.bs.tab')`
- **Collapses:** `data-bs-toggle="collapse"` (sidebar desplegable)

---

## Autores

- Sebastian Velasquez
- Camila Bermudez
- Diego Zabaleta
- Simon Cortes
- Sara Patiño

---

## Licencia

Uso interno — PETI 2025-2028
