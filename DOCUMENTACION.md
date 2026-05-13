# Funcionamiento del Sistema Inteligente de Clasificación de Fake News

Este documento detalla el flujo de trabajo, los criterios de evaluación y los métodos de representación del conocimiento que utiliza el **Sistema Inteligente de Clasificación de Fake News** para determinar la veracidad de una noticia.

---

## 1. Flujo de Trabajo del Sistema

El sistema opera en tres fases principales:

### Fase 1: Entrada y Extracción (Scraping)
El usuario proporciona la URL de la noticia. El sistema utiliza la librería `newspaper3k` para acceder a la página, extraer el **título**, el **cuerpo del texto** y detectar el **dominio de origen** (la fuente). Si el sitio web bloquea la extracción automática (común en redes sociales como Facebook o X), el sistema solicita el ingreso manual del texto. Finalmente, se pregunta al usuario si existe algún desmentido oficial.

### Fase 2: Procesamiento y Limpieza
El texto se "limpia" (se eliminan signos de puntuación y se convierte a minúsculas) y se divide en palabras individuales (tokenización). Esto prepara el texto para ser comparado contra nuestra "Red Semántica" de términos clave.

### Fase 3: Evaluación y Salida
El motor de inferencia evalúa los datos obtenidos aplicando **4 reglas heurísticas**. Se suman los "puntos de sospecha" detectados y el sistema emite una clasificación final utilizando **Reglas de Producción**.

---

## 2. Los 4 Pilares Heurísticos (Criterios de Evaluación)

El sistema no "lee" la noticia como un humano, sino que aplica **Heurísticas**: reglas prácticas que buscan señales de alerta. Cada señal suma "Puntos de Sospecha".

### A. Heurística de Verificabilidad (¿Quién lo dice?)
Es el filtro más importante. El sistema analiza el dominio (la dirección web) de donde proviene la información.
*   **¿Cómo funciona?**: Compara la URL contra una lista (Ontología) de medios conocidos.
    *   **Fuentes Oficiales**: (Ej. bbc.com, eluniversal.com.mx). Suma **0 puntos** (es confiable).
    *   **Fuentes Dudosas / Redes**: (Ej. facebook.com, whatsapp.com). Suma **+2 puntos** (alto riesgo de rumor).
    *   **Fuentes Desconocidas**: Sitios que no están en ninguna lista. Suma **+1 punto**.

### B. Heurística de Estilo Lingüístico (¿Cómo lo dice?)
Las noticias falsas suelen usar un lenguaje diseñado para causar una reacción emocional inmediata (pánico o sorpresa).
*   **¿Cómo funciona?**: Analiza el **Título** buscando dos señales:
    1.  **Red Semántica**: Busca palabras "gatillo" como *increíble, urgente, atención, ejecutado, desaparecen*.
    2.  **Gritos Digitales**: Si el título tiene más del 30% de letras MAYÚSCULAS, el sistema lo marca como sospechoso.
*   **Puntaje**: Si encuentra cualquiera de estas señales, suma **+1 punto**.

### C. Heurística de Contexto Local (¿Dónde ocurre?)
En el contexto de Chiapas, los rumores suelen "geolocalizarse" para asustar a la población local, mencionando pueblos o ciudades sin dar detalles técnicos.
*   **¿Cómo funciona?**: El sistema tiene una lista de ciudades (Jiquipilas, Tuxtla, San Cristóbal, etc.).
*   **Lógica**: Si la noticia menciona estos lugares pero proviene de una fuente dudosa, la sospecha aumenta.
*   **Puntaje**: Si menciona un lugar local, suma **+1 punto**.

### D. Heurística de Consistencia (¿Alguien ya lo desmintió?)
Esta es la prueba definitiva. Busca si la información ya fue contrastada con la realidad por autoridades.
*   **¿Cómo funciona?**: Requiere que el usuario confirme si ha visto un desmentido oficial (de la Fiscalía, Gobierno o medios de verificación).
*   **Puntaje**: Si el usuario confirma que hay un desmentido, suma **+2 puntos**. Es el criterio que más peso tiene después de la fuente.

---

## 3. Toma de Decisiones (Representación del Conocimiento)

El sistema utiliza **Reglas de Producción (Condicionales SI $\rightarrow$ ENTONCES)** para procesar la puntuación total y emitir un veredicto.

| Puntos | Regla Activada | Clasificación Final | Descripción |
| :---: | :--- | :--- | :--- |
| **0** | **R3:** Fuente confiable y sin contradicción. | ✅ **PROBABLEMENTE VERDADERA** | El medio es oficial y no usa tácticas alarmistas. |
| **1** | **R0:** Indicadores leves detectados. | 🟡 **LIGERA SOSPECHA / INFO NEUTRAL** | Solo detecta un factor leve (ej. portal de noticias desconocido pero sin sensacionalismo). |
| **2 a 3** | **R1:** Múltiples alertas (Fuente dudosa + Alarmismo). | ⚠️ **NECESITA VERIFICACIÓN ADICIONAL** | La noticia muestra varios síntomas de ser falsa, como provenir de Facebook usando un título alarmista. |
| **4+** | **R2:** Confirmación oficial falsa o múltiples alertas graves. | 🚨 **PROBABLEMENTE FALSA** | Alta probabilidad de desinformación, generalmente confirmada por un desmentido o proveniente de redes con pánico. |

---

## 4. El Árbol de Decisión

Visualmente, el sistema realiza este recorrido lógico en cada ejecución:

1. **¿La fuente es oficial?** (Decide si dar +0, +1, o +2 pts).
2. **¿El título usa lenguaje sensacionalista?** (Decide si dar +1 pt).
3. **¿Menciona lugares locales?** (Decide si dar +1 pt).
4. **¿Hay un desmentido oficial?** (Decide si dar +2 pts).

La suma final de las hojas de este árbol dicta la respuesta del sistema, cumpliendo de forma estricta con el modelo teórico planteado para el diagnóstico de Fake News locales.