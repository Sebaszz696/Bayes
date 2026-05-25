from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime
import subprocess
import os

doc = Document()

# --- Estilos generales ---
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

# Función para aplicar color a párrafo
def set_heading_color(paragraph, r, g, b):
    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(r, g, b)

def add_heading(doc, text, level=1, color=(31, 73, 125)):
    h = doc.add_heading(text, level=level)
    set_heading_color(h, *color)
    return h

def add_table_styled(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    # Encabezado
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        run = hdr[i].paragraphs[0].runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        # fondo azul oscuro
        tc = hdr[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1F497D')
        tcPr.append(shd)
    # Filas
    for ri, row_data in enumerate(rows):
        row = table.rows[ri + 1].cells
        for ci, val in enumerate(row_data):
            row[ci].text = str(val)
    return table

# ============================================================
# PORTADA
# ============================================================
doc.add_paragraph()
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('INFORME TÉCNICO')
run.bold = True
run.font.size = Pt(24)
run.font.color.rgb = RGBColor(31, 73, 125)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = subtitle.add_run('Aplicación de Soporte a Decisiones — PETI 2025-2028')
run2.bold = True
run2.font.size = Pt(16)
run2.font.color.rgb = RGBColor(68, 114, 196)

doc.add_paragraph()
meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run(f'Fecha: {datetime.date.today().strftime("%d de %B de %Y")}\n').font.size = Pt(12)
run_authors = meta.add_run('Autores: Sebastian Velasquez · Camila Bermudez · Diego Zabaleta · Simon Cortes · Sara Patiño')
run_authors.font.size = Pt(12)

doc.add_page_break()

# ============================================================
# ÍNDICE (manual)
# ============================================================
add_heading(doc, 'Tabla de Contenido', level=1)
toc_items = [
    '1. Descripción General',
    '2. Stack Tecnológico',
    '3. Estructura del Proyecto',
    '4. Módulo 1: Teoría de Decisiones de Bayes',
    '   4.1 Contexto y Propósito',
    '   4.2 Funcionalidades y Tabs',
    '   4.3 Fórmulas Clave',
    '   4.4 KPIs Principales',
    '5. Módulo 2: Teoría de Juegos',
    '   5.1 Contexto Empresarial',
    '   5.2 Matriz de Pagos',
    '   5.3 Reducción por Dominancia',
    '   5.4 Estrategias Mixtas',
    '   5.5 Fórmulas Clave',
    '6. Módulo 3: Líneas de Espera (Teoría de Colas)',
    '   6.1 Contexto y Decisión Clave',
    '   6.2 Tres Escenarios',
    '   6.3 Fórmulas M/M/1 y M/M/2',
    '   6.4 Resultados de Referencia',
    '7. Módulo 4: Programación de Proyectos — PERT/CPM',
    '   7.1 Contexto y Objetivos',
    '   7.2 Estructura de Tabs',
    '   7.3 Algoritmo y Procedimiento',
    '   7.4 Fórmulas Clave',
    '   7.5 Ejercicios Predefinidos',
    '   7.6 Red PERT/CPM',
    '8. Características Transversales',
    '9. Flujo de Uso',
    '10. Requisitos de Ejecución',
    '11. Limitaciones y Notas Técnicas',
]
for item in toc_items:
    p = doc.add_paragraph(item, style='List Bullet' if item.startswith('   ') else 'Normal')
    p.paragraph_format.left_indent = Cm(1) if item.startswith('   ') else Cm(0)

doc.add_page_break()

# ============================================================
# 1. DESCRIPCIÓN GENERAL
# ============================================================
add_heading(doc, '1. Descripción General', level=1)
doc.add_paragraph(
    'Esta es una aplicación web interactiva de análisis de decisiones empresariales desarrollada para soportar '
    'la evaluación e implementación del Plan Estratégico de Tecnología de la Información (PETI) 2025-2028. '
    'Integra tres módulos especializados de investigación operativa:'
)
modules_list = [
    'Teoría de Decisiones de Bayes — Análisis bajo incertidumbre',
    'Teoría de Juegos — Negociación estratégica entre JW y el Sindicato',
    'Líneas de Espera — Optimización de operaciones de despacho logístico',
    'PERT/CPM — Programación de proyectos y ruta crítica',
]
for m in modules_list:
    doc.add_paragraph(m, style='List Bullet')

# ============================================================
# 2. STACK TECNOLÓGICO
# ============================================================
add_heading(doc, '2. Stack Tecnológico', level=1)
add_table_styled(doc,
    ['Componente', 'Tecnología'],
    [
        ['Backend', 'Flask (Python)'],
        ['Frontend', 'HTML5 + Bootstrap 5 + Vanilla JS'],
        ['Visualización', 'Plotly.js (gráficas interactivas), D3.js v7 (árbol de decisión)'],
        ['Matemáticas', 'NumPy (Python), funciones puras'],
        ['Exportación', 'html2pdf.js (descarga PDF)'],
    ]
)
doc.add_paragraph()

# ============================================================
# 3. ESTRUCTURA DEL PROYECTO
# ============================================================
add_heading(doc, '3. Estructura del Proyecto', level=1)
files = [
    ('app_flask.py', 'Punto de entrada Flask'),
    ('routes.py', 'Rutas HTTP (/compute, /compute_queueing, /compute_game_theory)'),
    ('compute.py', 'Lógica de Teoría de Bayes'),
    ('game_theory.py', 'Lógica de Teoría de Juegos'),
    ('queueing.py', 'Lógica de Análisis de Colas'),
    ('tree_render.py', 'Renderizado de árbol de decisión (graphviz → PNG)'),
    ('templates/index.html', 'Interfaz única (HTML5 + Bootstrap)'),
    ('static/css/style.css', 'Estilos personalizados'),
    ('static/js/main.js', 'Lógica principal del frontend (2,000+ líneas)'),
    ('static/js/tree-d3.js', 'Renderizado D3 del árbol de decisión'),
    ('requirements.txt', 'Dependencias Python'),
]
add_table_styled(doc, ['Archivo / Carpeta', 'Descripción'], files)
doc.add_paragraph()

doc.add_page_break()

# ============================================================
# 4. MÓDULO 1: TEORÍA DE DECISIONES DE BAYES
# ============================================================
add_heading(doc, '4. Módulo 1: Teoría de Decisiones de Bayes', level=1)

add_heading(doc, '4.1 Contexto y Propósito', level=2)
doc.add_paragraph(
    'Este módulo analiza decisiones empresariales bajo incertidumbre utilizando la Teoría de Bayes. '
    'Es fundamental para la evaluación del PETI 2025-2028 porque permite cuantificar cómo la información '
    'adicional (estudios de mercado, pruebas técnicas) mejora la calidad de las decisiones de inversión tecnológica.'
)
doc.add_paragraph('Preguntas que responde:')
questions = [
    '¿Cuál alternativa maximiza el valor esperado?',
    '¿Vale la pena realizar un estudio de mercado?',
    '¿Cuánto puedo pagar por información adicional?',
]
for q in questions:
    doc.add_paragraph(q, style='List Bullet')

add_heading(doc, '4.2 Funcionalidades y Tabs', level=2)
tabs = [
    ('Tab 1 – Variables', 'Definición de estados, probabilidades y tabla de pagos'),
    ('Tab 2 – Tablas', 'Muestra 6 análisis de decisión (MAXIMAX, MAXIMIN, Regret, EV, Bayesiano, Muestral)'),
    ('Tab 3 – Árbol de Bayes', 'Visualización gráfica interactiva del árbol de decisión'),
    ('Tab 4 – Gráficas', 'Análisis de sensibilidad — cómo varía el EV con P(S1)'),
    ('Tab 5 – Resumen', 'Síntesis ejecutiva con KPIs'),
]
add_table_styled(doc, ['Tab', 'Descripción'], tabs)
doc.add_paragraph()

add_heading(doc, '4.3 Fórmulas Clave', level=2)
formulas = [
    ('P(F)', 'P(F|S1)·P(S1) + P(F|S2)·P(S2)', 'Ley total de probabilidad'),
    ('P(S1|F)', 'P(F|S1)·P(S1) / P(F)', 'Teorema de Bayes'),
    ('EV(Ai)', 'Σ V(Ai, Sj) · P(Sj)', 'Valor esperado'),
    ('VE Muestral', 'EV|F · P(F) + EV|U · P(U)', 'VE con estudio'),
    ('EVPI', 'EVwPI − EV(óptima)', 'Valor de información perfecta'),
    ('EVSI', 'VE Muestral − EV(óptima)', 'Valor del estudio muestral'),
]
add_table_styled(doc, ['Métrica', 'Fórmula', 'Descripción'], formulas)
doc.add_paragraph()

add_heading(doc, '4.4 KPIs Principales', level=2)
kpis = [
    ('EV óptimo', 'Mejor valor esperado sin información adicional'),
    ('EVPI', 'Máximo a pagar por información perfecta'),
    ('EVSI', 'Máximo a pagar por el estudio muestral'),
    ('Eficiencia', 'EVSI / EVPI × 100% — calidad del estudio'),
]
add_table_styled(doc, ['KPI', 'Significado'], kpis)
doc.add_paragraph()

doc.add_page_break()

# ============================================================
# 5. MÓDULO 2: TEORÍA DE JUEGOS
# ============================================================
add_heading(doc, '5. Módulo 2: Teoría de Juegos — Negociación Estratégica', level=1)

add_heading(doc, '5.1 Contexto Empresarial', level=2)
doc.add_paragraph(
    'Este módulo modela la negociación estratégica entre JW (empresa) y el sindicato de trabajadores '
    'en el marco del PETI 2025-2028. Determina la viabilidad de la Alternativa B (Inversión Media — Proyecto TI-01) '
    'y el nivel de adopción digital esperado. Se trata de un juego de suma cero resuelto mediante reducción '
    'por dominancia y estrategias mixtas óptimas.'
)
doc.add_paragraph('Valor del juego: V = 17.5 millones de COP').runs[0].bold = True

add_heading(doc, '5.2 Matriz de Pagos (Predeterminada)', level=2)
matrix_rows = [
    ['E1', '10', '30', '25', '15'],
    ['E2', '5',  '40', '10', '30'],
    ['E3', '15', '25', '5',  '10'],
    ['E4', '20', '20', '15', '40'],
]
add_table_styled(doc, ['JW \\ Sindicato', 'U1', 'U2', 'U3', 'U4'], matrix_rows)
doc.add_paragraph()

add_heading(doc, '5.3 Reducción por Dominancia', level=2)
steps = [
    ('Paso 1', 'Columna U2 dominada por U4 → eliminar U2'),
    ('Paso 2', 'Columna U3 dominada por U4 → eliminar U3'),
    ('Resultado', 'Matriz reducida 2×2 (E1, E4 × U1, U4)'),
]
add_table_styled(doc, ['Paso', 'Acción'], steps)
doc.add_paragraph()

add_heading(doc, '5.4 Estrategias Mixtas Óptimas', level=2)
results = [
    ('JW', 'E1 (50%) y E4 (50%)'),
    ('Sindicato', 'U1 (25%) y U4 (75%)'),
    ('Valor del juego V', '17.5 millones de COP'),
]
add_table_styled(doc, ['Jugador', 'Estrategia óptima'], results)
doc.add_paragraph()

add_heading(doc, '5.5 Fórmulas Clave', level=2)
game_formulas = [
    ('Dominancia columna (minimizador)', '∀i: A[i] ≤ B[i] → eliminar B'),
    ('Dominancia fila (maximizador)', '∀j: A[j] ≥ B[j] → eliminar B'),
    ('Indiferencia (q)', 'q = (d − b) / (a − b − c + d)'),
    ('Indiferencia (p)', 'p = (d − c) / (a − b − c + d)'),
    ('Valor del juego', 'V = a·p + c·(1−p)'),
]
add_table_styled(doc, ['Concepto', 'Fórmula'], game_formulas)
doc.add_paragraph()

doc.add_page_break()

# ============================================================
# 6. MÓDULO 3: LÍNEAS DE ESPERA
# ============================================================
add_heading(doc, '6. Módulo 3: Líneas de Espera (Teoría de Colas)', level=1)

add_heading(doc, '6.1 Contexto y Decisión Clave', level=2)
doc.add_paragraph(
    'Este módulo cuantifica el impacto de la inversión tecnológica (Alternativa B — PETI 2025-2028) '
    'en los tiempos de espera del sistema de despacho de vehículos. La tasa de llegada base es λ = 10 vehículos/hora. '
    'La decisión central es: ¿Invertir en tecnología (μ: 12→18) o agregar un servidor (c: 1→2)?'
)

add_heading(doc, '6.2 Tres Escenarios', level=2)
scenarios = [
    ('A — Canal Simple (M/M/1 actual)', 'Sin inversión. μ = 12 veh/hora. Caso base.'),
    ('B — Canal Mejorado (M/M/1 mejorado)', 'Con inversión tecnológica. μ = 18 veh/hora.'),
    ('C — Canal Múltiple (M/M/2)', 'Agregar servidor. c = 2, μ = 12 veh/hora por servidor.'),
]
add_table_styled(doc, ['Escenario', 'Descripción'], scenarios)
doc.add_paragraph()

add_heading(doc, '6.3 Fórmulas M/M/1 y M/M/2', level=2)
queue_formulas = [
    ('ρ (M/M/1)', 'λ/μ', 'Factor de utilización'),
    ('P₀ (M/M/1)', '1 − ρ', 'Probabilidad sistema vacío'),
    ('L (M/M/1)', 'ρ/(1−ρ)', 'Clientes promedio en sistema'),
    ('Lq (M/M/1)', 'ρ²/(1−ρ)', 'Clientes promedio en cola'),
    ('W', 'L/λ', 'Tiempo promedio en sistema'),
    ('Wq', 'Lq/λ', 'Tiempo promedio en cola'),
    ('P₀ (M/M/2)', '[1 + r + r²/(2(1−ρ))]⁻¹', 'Erlang-C, c=2'),
    ('Lq (M/M/2)', 'P₀·r²·ρ / (2(1−ρ)²)', 'Cola en servidor dual'),
]
add_table_styled(doc, ['Métrica', 'Fórmula', 'Descripción'], queue_formulas)
doc.add_paragraph()

add_heading(doc, '6.4 Resultados de Referencia (λ = 10 veh/hora)', level=2)
ref_results = [
    ('ρ', '0.833', '0.556', '0.417'),
    ('P₀', '0.167', '0.444', '0.410'),
    ('L (sistema)', '5.00', '1.25', '1.01'),
    ('Lq (cola)', '4.17', '0.69', '0.17'),
    ('W (horas)', '0.50', '0.13', '0.10'),
    ('Wq (horas)', '0.42', '0.07', '0.02'),
]
add_table_styled(doc,
    ['Indicador', 'M/M/1 Actual (μ=12)', 'M/M/1 Mejorado (μ=18)', 'M/M/2 (c=2, μ=12)'],
    ref_results
)
doc.add_paragraph()
doc.add_paragraph(
    'Conclusión automática del módulo: "El escenario Canal Mejorado es el más eficiente: '
    'W = 0.1296 h (7.8 min) por vehículo, con L = 1.2963 y ρ = 0.5556. '
    'Se recomienda su implementación para el horizonte PETI 2025-2028."'
).italic = True

doc.add_page_break()

# ============================================================
# 7. MÓDULO 4: PERT/CPM
# ============================================================
add_heading(doc, '7. Módulo 4: Programación de Proyectos — PERT/CPM', level=1)

add_heading(doc, '7.1 Contexto y Objetivos', level=2)
doc.add_paragraph(
    'Este módulo aplica la metodología PERT/CPM para la planificación de proyectos logísticos '
    'asociados al PETI 2025-2028. El objetivo es modelar y optimizar la implementación de un nuevo '
    'nodo logístico y tecnológico dentro de la organización, identificando actividades críticas, '
    'calculando tiempos mínimos de ejecución y detectando retrasos potenciales.'
)
doc.add_paragraph('Preguntas que responde:')
pert_questions = [
    '¿Cuál es la duración mínima del proyecto?',
    '¿Qué actividades no pueden retrasarse sin afectar la fecha final?',
    '¿Cuánto margen de flexibilidad tiene cada actividad no crítica?',
    '¿Cuál es la secuencia óptima de ejecución del proyecto?',
]
for q in pert_questions:
    doc.add_paragraph(q, style='List Bullet')

add_heading(doc, '7.2 Estructura de Tabs', level=2)
pert_tabs = [
    ('Tab 1 – Actividades', 'Tabla editable de actividades con presets. Botón Calcular ejecuta el análisis completo.'),
    ('Tab 2 – Forward Pass', 'Tabla IP/TP por actividad. Filas críticas resaltadas en rojo.'),
    ('Tab 3 – Backward Pass', 'Tabla TL/IL por actividad en orden inverso al topológico.'),
    ('Tab 4 – Holguras', 'Tabla H=IL−IP con badge Crítica/No. Alerta con ruta crítica y duración total.'),
    ('Tab 5 – Red PERT', 'Diagrama de red interactivo (Plotly) con nodos PERT clásicos: IP|ID|TP y IL|H|TL.'),
]
add_table_styled(doc, ['Tab', 'Descripción'], pert_tabs)
doc.add_paragraph()

add_heading(doc, '7.3 Algoritmo y Procedimiento', level=2)
pert_steps = [
    ('Ordenamiento Topológico', 'Algoritmo de Kahn (BFS) para determinar el orden de ejecución de actividades sin ciclos.'),
    ('Forward Pass', 'Recorrido de izquierda a derecha. IP = max(TP de predecesores); TP = IP + Duración.'),
    ('Backward Pass', 'Recorrido de derecha a izquierda. TL = min(IL de sucesoras); IL = TL − Duración.'),
    ('Holgura', 'H = IL − IP. Si H = 0, la actividad es crítica.'),
    ('Ruta Crítica', 'Secuencia de actividades con H = 0. Determina la duración mínima del proyecto.'),
]
add_table_styled(doc, ['Paso', 'Descripción'], pert_steps)
doc.add_paragraph()

add_heading(doc, '7.4 Fórmulas Clave', level=2)
pert_formulas = [
    ('IP (Inicio Próximo)', 'max(TP de predecesores)', 'Tiempo más temprano de inicio'),
    ('TP (Terminación Próxima)', 'IP + Duración', 'Tiempo más temprano de finalización'),
    ('TL (Terminación Lejana)', 'min(IL de sucesoras)', 'Último tiempo posible de finalización'),
    ('IL (Inicio Lejano)', 'TL − Duración', 'Último tiempo posible de inicio'),
    ('Holgura (H)', 'IL − IP', 'Margen de flexibilidad de la actividad'),
    ('Ruta Crítica', 'H = 0', 'Actividades que determinan la duración del proyecto'),
]
add_table_styled(doc, ['Métrica', 'Fórmula', 'Descripción'], pert_formulas)
doc.add_paragraph()

add_heading(doc, '7.5 Ejercicios Predefinidos', level=2)
pert_presets = [
    ('Proyecto Logístico (A–H)', '8 actividades', '21 días', 'A → C → F → H'),
    ('Automatización Inventarios RFID (I–P)', '8 actividades', '21 días', 'I → K → L → M → O → P'),
]
add_table_styled(doc, ['Ejercicio', 'Actividades', 'Duración total', 'Ruta crítica'], pert_presets)
doc.add_paragraph()

add_heading(doc, '7.6 Red PERT/CPM — Estructura de Nodos', level=2)
doc.add_paragraph(
    'El diagrama de red presenta cada actividad como un nodo rectangular con tres filas:'
)
node_layout = [
    ('Fila superior', 'IP | ID de actividad | TP', 'Tiempos tempranos e identificador'),
    ('Fila media', 'Descripción truncada (20 chars)', 'Nombre de la actividad'),
    ('Fila inferior', 'IL | H=n | TL', 'Tiempos lejanos y holgura'),
]
add_table_styled(doc, ['Fila', 'Contenido', 'Significado'], node_layout)
doc.add_paragraph()
doc.add_paragraph(
    'Código de colores: nodos en rojo (#dc3545) pertenecen a la ruta crítica (H=0); '
    'nodos en azul (#0d6efd) tienen holgura (H>0). Las flechas rojas gruesas '
    'indican aristas de la ruta crítica. El tooltip al pasar el cursor muestra '
    'todos los valores IP, TP, IL, TL y Holgura de la actividad.'
)

doc.add_page_break()

# ============================================================
# 8. CARACTERÍSTICAS TRANSVERSALES
# ============================================================
add_heading(doc, '8. Características Transversales', level=1)
features = [
    ('Glosario interactivo', 'Cada módulo dispone de un botón "Glosario" que abre un modal con definiciones, fórmulas y pasos de uso.'),
    ('Exportación a PDF', 'Botón "Descargar PDF" en cada tab-pane usando html2pdf.js. Exporta tablas, gráficas y conclusiones.'),
    ('Interfaz responsive', 'Sidebar colapsable en móviles, tablas scrolleables y gráficas responsivas.'),
    ('Validación y alertas', 'Validación ρ < 1 para colas, alerta de matriz degenerada en juegos, mensajes de error amigables.'),
]
add_table_styled(doc, ['Característica', 'Descripción'], features)
doc.add_paragraph()

# ============================================================
# 8. FLUJO DE USO
# ============================================================
add_heading(doc, '9. Flujo de Uso Típico', level=1)
add_heading(doc, '9.1 Usuario Empresarial', level=2)
steps_user = [
    'Abrir la aplicación web.',
    'Seleccionar módulo (Bayes, Juegos o Colas) en la barra lateral.',
    'Ingresar parámetros: probabilidades, matriz de pagos, λ, μ.',
    'Hacer clic en "Calcular".',
    'Revisar tablas, gráficas y árbol de decisión.',
    'Leer conclusión y recomendaciones.',
    'Descargar PDF con el análisis.',
    'Tomar decisión respecto al PETI 2025-2028.',
]
for s in steps_user:
    doc.add_paragraph(s, style='List Number')

add_heading(doc, '9.2 Desarrollador', level=2)
steps_dev = [
    'Modificar parámetros en compute.py, game_theory.py o queueing.py.',
    'Agregar nuevas rutas en routes.py.',
    'Actualizar main.js para renderizar nuevos campos.',
    'Actualizar style.css si hay nuevos estilos.',
    'Ejecutar tests y verificar en el navegador.',
]
for s in steps_dev:
    doc.add_paragraph(s, style='List Number')

# ============================================================
# 9. REQUISITOS DE EJECUCIÓN
# ============================================================
add_heading(doc, '10. Requisitos de Ejecución', level=1)
add_heading(doc, '10.1 Backend', level=2)
doc.add_paragraph('Python 3.x con las siguientes dependencias (requirements.txt):')
deps = ['Flask', 'NumPy', 'Graphviz (Python + sistema)', 'python-docx (opcional)']
for d in deps:
    doc.add_paragraph(d, style='List Bullet')
doc.add_paragraph('Comandos de instalación y ejecución:')
p = doc.add_paragraph()
run = p.add_run('pip install -r requirements.txt\npython app_flask.py')
run.font.name = 'Courier New'
run.font.size = Pt(10)

add_heading(doc, '10.2 Navegador', level=2)
browsers = ['Chrome, Firefox, Edge, Safari (versión reciente)', 'Soporte para ES6 (vanilla JS moderno)', 'Cookies habilitadas (sesiones Flask)']
for b in browsers:
    doc.add_paragraph(b, style='List Bullet')

# ============================================================
# 10. LIMITACIONES Y NOTAS TÉCNICAS
# ============================================================
add_heading(doc, '11. Limitaciones y Notas Técnicas', level=1)

add_heading(doc, '11.1 Limitaciones', level=2)
limitations = [
    'Teoría de Juegos: solo resuelve matrices 2×2 tras dominancia (sin LP para matrices mayores).',
    'Teoría de Juegos: solo soporta juegos de suma cero.',
    'Colas: M/M/2 con c=2 fijo (no generalizable a c>2).',
    'Colas: modelo Poisson puro (puede no reflejar llegadas reales).',
    'Sin análisis costo/beneficio integrado en el módulo de colas.',
]
for lim in limitations:
    doc.add_paragraph(lim, style='List Bullet')

add_heading(doc, '11.2 Notas Técnicas', level=2)
notes = [
    'Conversión numpy.float64 → float nativo con .tolist() para serialización JSON correcta.',
    'Árbol de decisión generado en Python (graphviz → PNG → data:image) y renderizado con D3.js.',
    'Modales de glosario usando data-bs-toggle="modal" de Bootstrap 5.',
    'Todos los valores monetarios expresados en millones de COP.',
    'Redondeo: ρ a 3 decimales; L, Lq, W, Wq a 4 decimales.',
]
for n in notes:
    doc.add_paragraph(n, style='List Bullet')

# ============================================================
# CIERRE
# ============================================================
doc.add_page_break()
add_heading(doc, 'Autores', level=1)
authors = ['Sebastian Velasquez', 'Camila Bermudez', 'Diego Zabaleta', 'Simon Cortes', 'Sara Patiño']
for a in authors:
    doc.add_paragraph(a, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph('Uso interno — PETI 2025-2028')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].italic = True
p.runs[0].font.color.rgb = RGBColor(128, 128, 128)

# Guardar Word
output_path = '/home/svelasquez/Downloads/Bayes/Informe_PETI_2025-2028.docx'
doc.save(output_path)
print(f'Word guardado en: {output_path}')

# Convertir a PDF con LibreOffice
output_dir = os.path.dirname(output_path)
try:
    result = subprocess.run(
        ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, output_path],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        pdf_path = output_path.replace('.docx', '.pdf')
        print(f'PDF guardado en: {pdf_path}')
    else:
        print(f'Error al convertir a PDF: {result.stderr}')
except Exception as e:
    print(f'No se pudo convertir a PDF: {e}')
