# Clasificación de Fake News - Sistema Inteligente

Este proyecto es un prototipo basado en Python para la clasificación de noticias falsas utilizando heurísticas, redes semánticas y árboles de decisión. Desarrollado para la materia de Inteligencia Artificial (7°M) en la Universidad Autónoma de Chiapas.

## 🚀 Cómo ejecutar el programa (Paso a paso)

Si acabas de descargar el repositorio y no tienes configurado un entorno, sigue estos pasos según tu sistema operativo:

### 1. Requisitos previos
- Tener instalado **Python 3.8** o superior.

### 2. Configuración inicial (Entorno Virtual)
Es recomendable usar un entorno virtual para no interferir con otras instalaciones de Python.

**En Windows:**
```powershell
# Crear el entorno virtual
python -m venv venv

# Activar el entorno
.\venv\Scripts\activate
```

**En macOS/Linux:**
```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate
```

### 3. Instalación de dependencias
Una vez activado el entorno, instala las librerías necesarias:
```bash
pip install -r requirements.txt
```

### 4. Ejecución del programa
Para iniciar el análisis de noticias, ejecuta:
```bash
python prototipo.py
```

## 🛠️ Funcionamiento
1. **URL de la noticia**: El sistema intentará extraer automáticamente el título y contenido usando `newspaper3k`.
2. **Heurísticas**: Se evalúa la fuente (Verificabilidad), el estilo lingüístico (Sensacionalismo) y el contexto local (Chiapas).
3. **Resultado**: El sistema mostrará un recorrido lógico por el **Árbol de Decisión** y una tabla de puntuación con la clasificación final.

---
**Nota**: Si el scraping automático es bloqueado por el sitio web (común en redes sociales), el sistema te permitirá ingresar el título y contenido de forma manual.
