# 🚗 Módulo: Análisis de Líneas de Espera (Teoría de Colas)

## Contexto empresarial

Este módulo cuantifica el **impacto de la inversión tecnológica (Alternativa B — PETI 2025-2028) en los tiempos de espera** del sistema de despacho de vehículos. Compara tres escenarios operativos usando modelos **M/M/1** (servidor simple) y **M/M/2** (servidor dual).

**Decisión clave**: ¿Vale la pena invertir en tecnología (μ = 12→18) o mejor agregar un servidor (c = 1→2)?

---

## Estructura del módulo

### 1. **Configuración de parámetros**
Entradas del usuario:

| Parámetro | Símbolo | Rango | Unidad | Descripción |
|-----------|---------|-------|--------|-------------|
| Tasa de llegada | λ | (0, ∞) | veh/hora | Vehículos que llegan (Poisson) |
| Tasa Canal Simple | μ actual | (λ, ∞) | veh/hora | Serv. actual sin inversión |
| Tasa Canal Mejorado | μ mejor | (λ, ∞) | veh/hora | Serv. con inversión (típ. +50%) |
| Tasa Canal Múltiple | μ servidor | (λ/2, ∞) | veh/hora | Serv. por servidor en M/M/2 |

### 2. **Tres escenarios comparativos**

#### Escenario A: Canal Simple (M/M/1 actual)
- Modelo: M/M/1 con λ y μ actual
- Caso base — **sin inversión**
- 1 solo servidor atiende todas las llegadas

#### Escenario B: Canal Mejorado (M/M/1 mejorado)
- Modelo: M/M/1 con λ y μ mejor
- Con inversión tecnológica
- Mismo servidor pero más rápido (+ eficiencia)

#### Escenario C: Canal Múltiple (M/M/2)
- Modelo: M/M/2 con λ y μ servidor, **c=2 fijo**
- Alternativa: agregar servidor
- 2 servidores en paralelo (balanceado)

### 3. **Tabla de resultados**
Comparación de **6 métricas clave** entre los 3 escenarios:

| Métrica | Símbolo | Fórmula M/M/1 | Fórmula M/M/2 | Interpretación |
|---------|---------|--------------|--------------|---|
| **Utilización** | ρ | λ/μ | λ/(2μ) | % de tiempo servidor ocupado |
| **Prob. vacío** | P₀ | 1−ρ | [1+r+r²/(2(1−ρ))]⁻¹ | Probabilidad de entrar sin espera |
| **Clientes sistema** | L | ρ/(1−ρ) | Lq + r | Promedio en el sistema |
| **Clientes cola** | Lq | ρ²/(1−ρ) | P₀·r²·ρ/(2(1−ρ)²) | Promedio esperando en cola |
| **Tiempo sistema** | W | L/λ | L/λ | Tiempo promedio (espera + servicio) |
| **Tiempo cola** | Wq | Lq/λ | Lq/λ | Tiempo promedio solo esperando |

Donde `r = λ/μ` (carga ofrecida).

**Mejor de cada métrica** está resaltada con ★ y fondo `best-ev`.

### 4. **Conclusión automática**
Texto basado en el escenario más eficiente:

> "El escenario 'Canal Mejorado' es el más eficiente: W = 0.1296 h (7.8 min) por vehículo, con L = 1.2963 vehículos en el sistema y ρ = 0.5556. Se recomienda su implementación para el horizonte PETI 2025-2028."

### 5. **Validación de estabilidad**
Si ρ ≥ 1:
- Sistema inestable (cola crece indefinidamente)
- Muestra alerta: "Inestable: ρ = X ≥ 1"
- Recomendación: aumentar μ o agregar servidores

---

## Fórmulas implementadas

### M/M/1 (Canal simple)
```
ρ = λ/μ                           (factor de utilización)
P₀ = 1 − ρ                        (sistema vacío)
L = ρ/(1−ρ)                       (clientes en sistema)
Lq = ρ²/(1−ρ)                     (clientes en cola)
W = L/λ                           (tiempo en sistema)
Wq = Lq/λ                         (tiempo en cola)

Condición: ρ < 1 (estabilidad)
```

### M/M/2 (Erlang-C, c=2)
```
r = λ/μ                                      (carga ofrecida)
ρ = λ/(2μ)                                   (factor de utilización)
P₀ = [1 + r + r²/(2(1−ρ))]⁻¹               (sistema vacío)
Lq = P₀·r²·ρ / (2(1−ρ)²)                    (clientes en cola)
L = Lq + r                                   (clientes en sistema)
W = L/λ                                      (tiempo en sistema)
Wq = Lq/λ                                    (tiempo en cola)

Condición: ρ < 1  ⟺  λ/(2μ) < 1  ⟺  λ < 2μ  (estabilidad)
```

---

## Requisitos actuales

### Entradas
- λ (tasa de llegada)
- 3 tasas de servicio (actual, mejorada, múltiple)
- Botón "Calcular"

### Salidas
- Tabla de 6 métricas × 3 escenarios
- Identificación visual de "mejor" en cada métrica
- Alertas de inestabilidad (ρ ≥ 1)
- Conclusión textual recomendatoria

### Stack actual
- **Backend**: Flask + Python (queueing.py)
  - `mm1_metrics(lam, mu)`: calcula 6 métricas M/M/1
  - `mm2_metrics(lam, mu)`: calcula 6 métricas M/M/2 (Erlang-C)
  - `compute_queueing(cfg)`: orquestador + best per metric + conclusion
- **Frontend**: HTML + Bootstrap 5 + vanilla JS
- **Cálculos**: funciones puras, numpy arrays convertidos a float

---

## Valores de referencia (validación)

Con λ=10 veh/hora:

| Métrica | M/M/1 (μ=12) | M/M/1 (μ=18) | M/M/2 (μ=12) |
|---------|-------------|-------------|-------------|
| ρ | 0.833 | 0.556 | 0.417 |
| P₀ | 0.167 | 0.444 | 0.410 |
| L | 5.00 | 1.25 | 1.01 |
| Lq | 4.17 | 0.69 | 0.17 |
| W (h) | 0.50 | 0.13 | 0.10 |
| Wq (h) | 0.42 | 0.07 | 0.02 |

---

## Casos de uso

1. **Diseño de capacidad**: ¿Cuántos servidores necesito?
2. **Optimización de operaciones**: Equilibrio costo/servicio
3. **Análisis de inversión**: ROI de mejorar μ vs. agregar servidor
4. **Pronóstico de SLA**: Predicción de tiempos de espera
5. **Enseñanza**: Demostración interactiva de teoría de colas

---

## Limitaciones actuales

- **c=2 fijo** para M/M/2 (no es generalizable a c>2)
- **Modelo Poisson**: supone llegadas exponenciales (puede no ser real)
- **Servidor único**: no modela múltiples canales en paralelo con política FIFO diferentes
- **Sin costos**: solo métricas de desempeño, no incluye análisis costo/beneficio

---

## Notas técnicas

- Validación `ρ < 1` antes de calcular métricas (retorna error si inestable)
- Conversión numpy arrays → float nativo para evitar display `np.float64(X)`
- Redondeo: ρ a 3 decimales, L/Lq a 4, W/Wq a 4
- Interfaz responsive: funciona en mobile (tabla scrollable)
- Métrica "mejor": índice de escenario con menor valor (excepto P₀ que es máximo)
