# 🎯 Módulo: Teoría de Juegos — Negociación JW vs. Sindicato

## Contexto del negocio

Este módulo modela la negociación estratégica entre la empresa **JW** y el **sindicato de trabajadores**, en el marco de la implementación del **PETI 2025-2028**. El resultado de esta negociación determina la viabilidad de la **Alternativa B (Inversión Media — Proyecto TI-01)** y el nivel de adopción digital esperado.

Se trata de un **juego de suma cero** resuelto mediante reducción por dominación y estrategias mixtas óptimas.

---

## Definición del juego

### Jugadores
- **JW (empresa)**: jugador fila (maximizador)
- **Sindicato**: jugador columna (minimizador)

### Tipo de juego
- Suma cero (lo que gana JW, lo pierde el sindicato y viceversa)
- Resuelto con **estrategias mixtas** tras reducción por dominación

### Valor del juego
> **V = 17.5 millones de COP**

---

## Estrategias óptimas

### Sindicato (jugador columna)
| Estrategia | Probabilidad óptima |
|------------|---------------------|
| U1         | p = 0.25            |
| U4         | p = 0.75            |

> Las estrategias no listadas fueron eliminadas por dominación.

### JW (jugador fila)
- Las probabilidades óptimas de JW deben calcularse a partir de la matriz reducida.
- Deben mostrarse en el módulo una vez se resuelva el sistema de ecuaciones de indiferencia.

---

## Proceso de solución implementado

1. **Construcción de la matriz de pagos** original (JW vs. Sindicato)
2. **Reducción por dominación**:
   - Eliminar estrategias dominadas del sindicato (columnas)
   - Eliminar estrategias dominadas de JW (filas)
   - Repetir iterativamente hasta obtener matriz irreducible
3. **Resolución con estrategias mixtas**:
   - Plantear ecuaciones de indiferencia para cada jugador
   - Resolver el sistema para obtener probabilidades óptimas `p` y `q`
   - Calcular el valor del juego `V`
4. **Interpretación estratégica** del resultado en contexto empresarial

---

## Requisitos del módulo

### Entradas
- Matriz de pagos original (configurable, formato bidimensional)
- Etiquetas de estrategias para JW y para el Sindicato
- Unidad monetaria: **COP (millones)**

### Salidas
- Matriz original renderizada
- Pasos de reducción por dominación (mostrar qué estrategias se eliminan y por qué)
- Matriz reducida final
- Probabilidades óptimas del Sindicato y de JW
- Valor del juego `V`
- Conclusión interpretativa en lenguaje de negocio

### Valores de referencia para validación
- Valor del juego: **17.5 millones de COP**
- Estrategias activas del sindicato: **U1 (25%)** y **U4 (75%)**

---

## Stack sugerido

- **React + TypeScript**
- Lógica de resolución en utilidades puras (`/utils/gameTheory.ts`)
- Visualización de la matriz con resaltado de celdas eliminadas/activas
- Mostrar los pasos de dominación como proceso educativo/auditable

---

## Estructura de archivos sugerida

```
src/
├── modules/
│   └── gameTheory/
│       ├── GameTheoryModule.tsx      # Componente raíz del módulo
│       ├── PayoffMatrix.tsx          # Renderizado visual de la matriz de pagos
│       ├── DominanceSteps.tsx        # Visualización paso a paso de la reducción
│       ├── StrategyResult.tsx        # Probabilidades óptimas y valor del juego
│       ├── NegotiationConclusion.tsx # Interpretación en contexto empresarial
│       └── gameTheory.ts             # Lógica pura: dominancia, estrategias mixtas, valor V
```

---

## Lógica de `gameTheory.ts`

```typescript
// Funciones que debe exponer el módulo de lógica:

reduceDominatedStrategies(matrix: number[][]): ReductionResult
// Retorna la matriz reducida y el log de pasos de eliminación

solveMixedStrategies(reducedMatrix: number[][]): MixedStrategyResult
// Retorna probabilidades óptimas de ambos jugadores y valor del juego

interface MixedStrategyResult {
  playerRowProbabilities: number[]   // probabilidades de JW
  playerColProbabilities: number[]   // probabilidades del Sindicato
  gameValue: number                  // valor del juego en COP
}
```

---

## Notas para la IA

- El módulo debe ser **educativo y auditable**: mostrar cada paso de la reducción, no solo el resultado final
- Los valores hardcodeados de referencia (V = 17.5, U1=0.25, U4=0.75) son para **validar** que el algoritmo funciona correctamente
- La matriz de pagos debe ser **configurable** (no hardcodeada) para que el módulo sea reutilizable
- Moneda: todos los valores monetarios en **millones de COP**
- El lenguaje de la interfaz es **español**
