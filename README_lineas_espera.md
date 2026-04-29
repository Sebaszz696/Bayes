# 📦 Módulo: Análisis de Líneas de Espera — Despacho Logístico

## Contexto del negocio

Este módulo forma parte de una aplicación empresarial de soporte a decisiones estratégicas del **PETI 2025-2028**. Analiza el impacto de la inversión tecnológica (Alternativa B — Proyecto TI-01) en los tiempos de espera del despacho de vehículos, comparando tres escenarios operativos.

La tasa de llegada es fija: **λ = 10 vehículos/hora**.

---

## Modelos implementados

### M/M/1 — Canal simple actual
- Tasa de servicio: **μ = 12 vehículos/hora**
- Sin inversión tecnológica

### M/M/1 — Canal simple mejorado
- Tasa de servicio: **μ = 18 vehículos/hora**
- Con inversión tecnológica (Alternativa B)

### M/M/2 — Canal múltiple
- Tasa de servicio por canal: **μ = 12 vehículos/hora**
- Número de servidores: **c = 2**

---

## Fórmulas aplicadas

```
ρ  = λ / μ                    (factor de utilización)
P₀ = 1 - ρ                   (probabilidad sistema vacío — M/M/1)
L  = ρ / (1 - ρ)             (clientes promedio en el sistema)
Lq = ρ² / (1 - ρ)            (clientes promedio en cola)
W  = L / λ                   (tiempo promedio en el sistema)
Wq = Lq / λ                  (tiempo promedio en cola)
```

> Para M/M/2, los cálculos de P₀ y Lq usan las fórmulas de Erlang-C con c=2.

---

## Resultados comparativos esperados

| Indicador     | M/M/1 Actual (μ=12) | M/M/1 Mejorado (μ=18) | M/M/2 (c=2, μ=12) |
|---------------|---------------------|-----------------------|--------------------|
| ρ             | 0.833               | 0.556                 | 0.417              |
| P₀            | 0.167               | 0.444                 | 0.410              |
| L (sistema)   | 5.00                | 1.25                  | 1.01               |
| Lq (cola)     | 4.17                | 0.69                  | 0.17               |
| W (horas)     | 0.50                | 0.13                  | 0.10               |
| Wq (horas)    | 0.42                | 0.07                  | 0.02               |

---

## Requisitos del módulo

### Entradas del usuario
- `lambda` (λ): tasa de llegada (vehículos/hora)
- `mu` (μ): tasa de servicio por canal (vehículos/hora)
- `c`: número de servidores (1 para M/M/1, 2 para M/M/2)

### Salidas calculadas
- Factor de utilización `ρ`
- Probabilidad de sistema vacío `P₀`
- Clientes en sistema `L`
- Clientes en cola `Lq`
- Tiempo en sistema `W` (en horas)
- Tiempo en cola `Wq` (en horas)

### Vista comparativa
- El módulo debe mostrar los **3 escenarios en paralelo** (tabla o tarjetas)
- Resaltar visualmente el escenario con mejor desempeño
- Incluir conclusión textual automática basada en los resultados

---

## Stack sugerido

- **React + TypeScript** (consistente con el resto del proyecto)
- Cálculos en utilidades puras (`/utils/queueingTheory.ts`)
- UI con componentes reutilizables por escenario
- Gráficas opcionales con `recharts` para comparar L, Lq, W, Wq

---

## Estructura de archivos sugerida

```
src/
├── modules/
│   └── queueing/
│       ├── QueueingModule.tsx        # Componente raíz del módulo
│       ├── ScenarioCard.tsx          # Tarjeta por escenario (M/M/1, M/M/2)
│       ├── ComparisonTable.tsx       # Tabla comparativa de los 3 escenarios
│       ├── QueueingChart.tsx         # Gráfica de barras comparativa
│       └── queueingTheory.ts         # Lógica de cálculo (funciones puras)
```

---

## Notas para la IA

- Los cálculos deben ser funciones **puras y testeables** en `queueingTheory.ts`
- Separar lógica de presentación estrictamente
- Validar que `ρ < 1` para M/M/1 y `ρ/c < 1` para M/M/2 (sistema inestable si no se cumple)
- Los valores de la tabla de resultados son los valores de referencia para validar los cálculos
- Moneda de referencia: **COP (pesos colombianos)** si se muestran costos asociados
