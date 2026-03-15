# Teoría de Decisiones — Interactivo

Instrucciones rápidas para ejecutar la versión interactiva localmente.

1. (Opcional) Crear y activar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Ejecutar la app (Flask):

Opción A — usando el intérprete del entorno virtual:

```bash
FLASK_APP=app_flask.py ./.venv/bin/python -m flask run --host=127.0.0.1 --port=5000
```

Opción B — con la variable de entorno y `flask` instalado en el entorno activo:

```bash
export FLASK_APP=app_flask.py
flask run --host=127.0.0.1 --port=5000
```

La app permite editar la tabla de pagos, ajustar probabilidades y ver métricas junto con el árbol de decisión y gráficos interactivos. Los resultados pueden exportarse como CSV o PDF desde la interfaz.
