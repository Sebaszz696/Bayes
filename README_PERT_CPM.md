# 📅 Módulo: Programación de Proyectos — PERT/CPM

## Contexto empresarial

Este módulo aplica la metodología **PERT/CPM** para la planificación de proyectos logísticos y tecnológicos del **PETI 2025-2028**. Permite modelar la ejecución de proyectos complejos con múltiples actividades dependientes, identificando cuáles son críticas y cuáles tienen margen de flexibilidad.

Incluye dos casos de aplicación reales:

- **Proyecto Logístico (A–H)**: implementación de un nuevo nodo de despacho y transporte de mercancías
- **Automatización de Inventarios RFID (I–P)**: integración de lectores RFID con el sistema TMS del almacén

---

## Estructura del módulo

### 1. **Actividades** (Tab 1)
Tabla editable con todas las actividades del proyecto:

| Campo | Descripción |
|-------|-------------|
| **ID** | Identificador único de la actividad (letra o código) |
| **Descripción** | Nombre de la tarea |
| **Predecesores** | IDs separados por coma de actividades que deben terminar antes |
| **Duración (días)** | Tiempo estimado de ejecución |

- Botones para cargar ejercicios predefinidos o ingresar actividades manualmente
- Botón **"+ Agregar actividad"** para ampliar la tabla
- Botón **"🗑 Limpiar tabla"** para resetear todo
- Botón **"Calcular"** que ejecuta el análisis completo y rellena los 4 tabs restantes

### 2. **Forward Pass** (Tab 2)
Recorrido hacia adelante en orden topológico:

| Columna | Significado |
|---------|-------------|
| **IP** | Inicio Próximo — tiempo más temprano de inicio |
| **TP** | Terminación Próxima — TP = IP + Duración |

- Filas críticas (H = 0) resaltadas en **rojo**
- Actidades en orden topológico (de inicio a fin)

### 3. **Backward Pass** (Tab 3)
Recorrido hacia atrás en orden topológico inverso:

| Columna | Significado |
|---------|-------------|
| **TL** | Terminación Lejana — último tiempo posible de finalización |
| **IL** | Inicio Lejano — IL = TL − Duración |

- Tabla en **orden inverso** al topológico (de fin a inicio)
- Filas críticas resaltadas en rojo

### 4. **Holguras** (Tab 4)
Análisis de margen de cada actividad:

| Columna | Fórmula | Significado |
|---------|---------|-------------|
| **IP** | — | Inicio Próximo (del Forward Pass) |
| **IL** | — | Inicio Lejano (del Backward Pass) |
| **Holgura** | `H = IL − IP` | Días de margen disponibles |
| **¿Crítica?** | `H = 0` | Badge rojo = crítica, verde = con margen |

- Alerta con la **ruta crítica** y duración total del proyecto
- Conclusión textual del análisis

### 5. **Red PERT** (Tab 5)
Diagrama de red interactivo generado con **Plotly.js**:

- Cada nodo es un rectángulo con 3 filas:
  ```
  ┌──────────────────────────┐
  │  IP  │   ID (grande)  │ TP  │
  │      Descripción         │
  │  IL  │   H = n        │ TL  │
  └──────────────────────────┘
  ```
- **Nodos rojos**: actividades críticas (H = 0)
- **Nodos azules**: actividades con holgura (H > 0)
- **Flechas rojas gruesas**: aristas de la ruta crítica
- **Flechas grises**: aristas normales
- **Badge** sobre cada flecha con la duración en días
- **Tooltip** al pasar el cursor: muestra IP, TP, IL, TL, Holgura

---

## Algoritmo

### Ordenamiento Topológico (Kahn)
Se usa BFS para determinar el orden de ejecución sin ciclos:

```python
in_degree = {i: len(predecesores[i]) for i in actividades}
queue = [i for i in actividades if in_degree[i] == 0]
while queue:
    node = queue.pop(0)
    topo_order.append(node)
    for sucesor in sucesores[node]:
        in_degree[sucesor] -= 1
        if in_degree[sucesor] == 0:
            queue.append(sucesor)
```

### Forward Pass (izquierda → derecha)
```
Para actividades sin predecesor:  IP = 0
Para el resto:                    IP = max(TP de todos sus predecesores)
Siempre:                          TP = IP + Duración
Duración total del proyecto = max(TP de todas las actividades)
```

### Backward Pass (derecha → izquierda)
```
Para actividades sin sucesor:  TL = duración total del proyecto
Para el resto:                 TL = min(IL de todos sus sucesores)
Siempre:                       IL = TL − Duración
```

### Holgura y Ruta Crítica
```
H = IL − IP
Actividad crítica ↔ H = 0
Ruta crítica = secuencia de actividades críticas de inicio a fin
```

---

## Fórmulas clave

```
IP  = max(TP de predecesores)      [Inicio Próximo]
TP  = IP + Duración                [Terminación Próxima]
TL  = min(IL de sucesores)         [Terminación Lejana]
IL  = TL − Duración                [Inicio Lejano]
H   = IL − IP                      [Holgura]
RC  = {actividades | H = 0}        [Ruta Crítica]
```

---

## Ejercicios predefinidos

### Ejercicio 1 — Proyecto Logístico (A–H)

| ID | Descripción | Predecesores | Duración |
|----|-------------|--------------|----------|
| A | Planificación de rutas y red de transporte | — | 3 |
| B | Contratación de proveedores de carga | A | 4 |
| C | Adecuación física del centro de despacho | A | 6 |
| D | Mantenimiento y revisión de flota vehicular | B | 6 |
| E | Capacitación de conductores | B | 4 |
| F | Instalación del software TMS | C | 4 |
| G | Despacho del primer lote de prueba | D | 6 |
| H | Auditoría final de entrega | E, F | 8 |

**Resultado**: Duración total = **21 días** — Ruta crítica: **A → C → F → H**

### Ejercicio 2 — Automatización de Inventarios RFID (I–P)

**RFID** (*Radio Frequency Identification*): tecnología de identificación automática mediante ondas de radio. Permite rastrear productos en tiempo real sin contacto físico, reemplazando los lectores de código de barras en el almacén.

**TMS** (*Transportation Management System*): software de gestión de transporte integrado con los lectores RFID para visibilidad total del inventario en tránsito.

| ID | Descripción | Predecesores | Duración |
|----|-------------|--------------|----------|
| I | Análisis de requerimientos | — | 4 |
| J | Selección de proveedor RFID | I | 3 |
| K | Adecuación del almacén | I | 5 |
| L | Instalación de lectores y antenas | J, K | 4 |
| M | Configuración del software | L | 3 |
| N | Pruebas piloto | M | 2 |
| O | Capacitación del personal | M | 3 |
| P | Integración con TMS | N, O | 2 |

**Resultado**: Duración total = **21 días** — Ruta crítica: **I → K → L → M → O → P**

---

## Requisitos

### Entradas
- Lista de actividades con ID, descripción, predecesores y duración en días
- El grafo de precedencias debe ser un DAG (sin ciclos)

### Salidas
- Tabla Forward Pass (IP, TP por actividad)
- Tabla Backward Pass (IL, TL por actividad, orden inverso)
- Tabla Holguras (H = IL − IP, badge crítica/no)
- Duración total del proyecto
- Ruta crítica (lista de IDs con H = 0)
- Red PERT interactiva (Plotly)
- Conclusión textual automática

### Stack
- **Backend**: Flask + Python (`pert_cpm.py`, `routes.py`)
  - `compute_pert_cpm(cfg)`: orquestador principal
  - Kahn's BFS para ordenamiento topológico
- **Frontend**: HTML + Bootstrap 5 + Plotly.js
  - `renderPertForward(data)`: tabla Forward Pass
  - `renderPertBackward(data)`: tabla Backward Pass
  - `renderPertHolguras(data)`: tabla holguras + alertas
  - `renderPertNetwork(data)`: red PERT con Plotly shapes + annotations

---

## Casos de uso

1. **Planificación de proyectos TI**: definir cronograma mínimo y actividades críticas
2. **Gestión de riesgos**: identificar qué retrasos impactan la fecha final
3. **Asignación de recursos**: concentrar esfuerzos en la ruta crítica
4. **Comunicación ejecutiva**: diagrama de red para presentaciones del PETI

---

## Limitaciones

- Solo soporta duraciones determinísticas (CPM puro, no distribuciones probabilísticas de PERT estocástico)
- El grafo debe ser un DAG válido; ciclos de dependencia no son detectados con mensaje de error explícito
- La red Plotly posiciona nodos por nivel topológico (layout automático, no manual)

---

## Notas técnicas

- El ordenamiento topológico garantiza que Forward Pass procese siempre los predecesores antes que los sucesores
- El Backward Pass recorre `reversed(topo_order)` para garantizar el mismo orden inverso
- `_currentPertPreset` rastrea el ejercicio activo para titular correctamente la Red PERT
- `lastPertCpmData` cachea el último resultado para re-renderizar al cambiar de tab sin recalcular
- Posicionamiento de nodos en la red: `level[id] = max(level[predecesor]) + 1`, distribuidos verticalmente por nivel
