import string
import urllib.parse
from newspaper import Article, ArticleException

# ==========================================
# ONTOLOGÍA DEL SISTEMA
# Define relaciones entre conceptos clave:
#   Noticia → Fuente → Credibilidad
#   Noticia → Palabras Clave → Sensacionalismo → Fake News
# ==========================================
ONTOLOGIA = {
    "fuente_oficial":    {"credibilidad": "alta",  "peso": 0},
    "fuente_desconocida":{"credibilidad": "media", "peso": 1},
    "fuente_dudosa":     {"credibilidad": "baja",  "peso": 2},
}

# Red semántica: términos asociados a patrones de desinformación
# Noticia → Palabras Clave → Sensacionalismo → Fake News
RED_SEMANTICA_SENSACIONALISMO = [
    # Violencia / nota roja (casos locales Chiapas)
    'mutilaciones', 'ejecución', 'ejecutado', 'decapitado',
    'violencia', 'hallazgo', 'cadáver', 'cuerpos','desaparecen',
    # Alarmismo general
    'increíble', 'urgente', 'atención', 'difundir', 'ocultan',
    'nunca visto', 'impactante', 'exclusiva', 'revelación',
    # Contexto político local
    'gasolinazo', 'desabasto', 'quiebra',
]

# Lugares locales de Chiapas para heurística de Contexto Local
LUGARES_LOCALES_CHIAPAS = [
    'jiquipilas', 'tuxtla', 'chiapas', 'san cristóbal',
    'tapachula', 'comitán', 'ocosingo', 'palenque',
    'tonalá', 'arriaga', 'villaflores', 'cintalapa',
    'suchiapa', 'berriozábal', 'chiapa de corzo',
]

# ==========================================
# FASE 1: PROCESAMIENTO DE TEXTO (Limpieza)
# ==========================================
def limpiar_texto(texto):
    """Convierte a minúsculas y elimina signos de puntuación."""
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

def tokenizar(texto):
    """Divide el texto en una lista de palabras (tokens)."""
    return texto.split()

# ==========================================
# FASE 2: MOTOR DE INFERENCIA (Heurísticas)
# ==========================================

def heuristica_sensacionalismo(titulo, cuerpo):
    """
    Heurística de Estilo Lingüístico.
    Evalúa lenguaje alarmista usando la red semántica.
    Se evalúa principalmente el título, ya que el cuerpo extenso puede incluir
    estas palabras en contextos legítimos.
    Peso máximo: +1
    """
    peso = 0
    titulo_limpio = limpiar_texto(titulo)
    tokens_titulo = set(tokenizar(titulo_limpio))

    # Verificar contra red semántica (Noticia → Palabras Clave → Sensacionalismo)
    for palabra in RED_SEMANTICA_SENSACIONALISMO:
        if palabra in tokens_titulo:
            peso = 1
            break

    # Exceso de mayúsculas en el título original (señal de alarmismo)
    mayusculas = sum(1 for c in titulo if c.isupper())
    if len(titulo) > 0 and (mayusculas / len(titulo)) > 0.3:
        peso = 1

    return peso


def extraer_dominio(url):
    """Extrae el dominio de una URL."""
    try:
        parsed_uri = urllib.parse.urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        return domain.replace('www.', '')
    except Exception:
        return 'desconocida'


def heuristica_verificabilidad(fuente):
    """
    Heurística de Verificabilidad (Nodo Raíz del Árbol de Decisión).
    Evalúa la credibilidad de la fuente usando la ontología del sistema.
    Fuente oficial → 0 pts | Desconocida → +1 pt | Dudosa/Redes → +2 pts
    """
    fuentes_oficiales = [
        # Medios de Chiapas y nacionales reconocidos
        'diariodechiapas.com', 'eluniversal.com.mx', 'gob.mx',
        'fiscalia.gob.mx', 'bbc.com', 'elpais.com', 'reforma.com',
        'animalpolitico.com', 'proceso.com.mx', 'excelsior.com.mx',
        'milenio.com', 'jornada.com.mx', 'cronica.com.mx',
    ]
    fuentes_dudosas = [
        # Redes sociales y sitios de baja credibilidad (ontología: credibilidad baja)
        'facebook.com', 'whatsapp.com', 'twitter.com', 'x.com',
        'costanews.com', 'codigorojo.com', 'tiktok.com', 'instagram.com',
        'youtube.com', 't.me', 'telegram.org',
    ]

    fuente_limpia = fuente.lower().strip()

    if any(f in fuente_limpia for f in fuentes_dudosas):
        credibilidad = ONTOLOGIA["fuente_dudosa"]
    elif any(f in fuente_limpia for f in fuentes_oficiales):
        credibilidad = ONTOLOGIA["fuente_oficial"]
    else:
        credibilidad = ONTOLOGIA["fuente_desconocida"]

    return credibilidad["peso"]


def heuristica_contexto_local(titulo, cuerpo):
    """
    Heurística de Contexto Local (nueva, requerida por el PDF).
    Detecta si la noticia menciona lugares locales de Chiapas
    sin respaldo verificable (indicador de rumor local).
    Peso: +1
    """
    texto_unido = limpiar_texto(titulo + " " + cuerpo)
    tokens = set(tokenizar(texto_unido))

    menciona_lugar_local = any(lugar in texto_unido for lugar in LUGARES_LOCALES_CHIAPAS)

    # Si menciona un lugar local pero proviene de fuente no oficial, es sospechoso
    if menciona_lugar_local:
        return 1
    return 0


def heuristica_consistencia(desmentido_oficial):
    """
    Heurística de Consistencia (Nodo de Decisión 2 del Árbol).
    Si hay datos oficiales que contradigan la noticia → peso crítico +2.
    """
    if desmentido_oficial.strip().lower() in ('si', 'sí', 's'):
        return 2
    return 0

# ==========================================
# ÁRBOL DE DECISIÓN
# Nodo Raíz: ¿La fuente es oficial?
#   → No: ¿Usa lenguaje sensacionalista?
#       → Sí: ¿Menciona lugares locales sin respaldo?
#           → Sí/No: ¿Existe desmentido oficial?
#   → Sí: ¿Existe desmentido oficial?
# ==========================================
def arbol_de_decision(p_verificabilidad, p_sensacionalismo,
                      p_contexto_local, p_consistencia):
    """
    Visualiza el recorrido lógico del árbol de decisión del sistema.
    """
    print("\n" + "="*50)
    print("  ÁRBOL DE DECISIÓN - RECORRIDO LÓGICO")
    print("="*50)

    print("\n[Nodo Raíz] ¿La fuente es un medio oficial?")
    if p_verificabilidad == 0:
        print("  → SÍ  (Fuente confiable, peso: 0)")
    elif p_verificabilidad == 1:
        print("  → PARCIAL (Fuente desconocida, peso: +1)")
    else:
        print("  → NO  (Fuente dudosa/redes sociales, peso: +2)")

    print("\n[Nodo 1] ¿El título usa lenguaje sensacionalista o alarmista?")
    if p_sensacionalismo > 0:
        print(f"  → SÍ  (Palabras de alerta detectadas, peso: +{p_sensacionalismo})")
    else:
        print("  → NO  (Sin lenguaje alarmista, peso: 0)")

    print("\n[Nodo 2] ¿Menciona lugares locales sin reportes verificables?")
    if p_contexto_local > 0:
        print(f"  → SÍ  (Contexto local sin respaldo, peso: +{p_contexto_local})")
    else:
        print("  → NO  (Sin contexto local sospechoso, peso: 0)")

    print("\n[Nodo 3] ¿Existen datos oficiales que desmientan la información?")
    if p_consistencia > 0:
        print(f"  → SÍ  (Desmentido oficial confirmado, peso: +{p_consistencia})")
    else:
        print("  → NO  (Sin desmentido encontrado, peso: 0)")


# ==========================================
# TABLA HEURÍSTICA (según PDF, pág. 15-16)
# ==========================================
def mostrar_tabla_heuristica(p_verif, p_sens, p_ctx, p_cons):
    print("\n" + "="*65)
    print("  TABLA HEURÍSTICA DE EVALUACIÓN")
    print("="*65)
    print(f"  {'Criterio Heurístico':<25} {'Indicador':<20} {'Peso':>6}")
    print("-"*65)
    print(f"  {'Verificabilidad':<25} {'Fuente analizada':<20} {'+'+str(p_verif):>6}")
    print(f"  {'Estilo Lingüístico':<25} {'Sensacionalismo':<20} {'+'+str(p_sens):>6}")
    print(f"  {'Contexto Local':<25} {'Lugar local s/respaldo':<20} {'+'+str(p_ctx):>6}")
    print(f"  {'Consistencia':<25} {'Desmentido oficial':<20} {'+'+str(p_cons):>6}")
    print("-"*65)
    total = p_verif + p_sens + p_ctx + p_cons
    print(f"  {'TOTAL DE PUNTOS DE SOSPECHA':<46} {'+'+str(total):>6}")
    print("="*65)


# ==========================================
# FASE 3: SALIDA (Reglas de Producción)
# SI condición → ENTONCES resultado
# ==========================================
def clasificar_noticia(peso_total):
    """
    Reglas de producción para la clasificación final.

    R1: SI fuente dudosa Y contenido alarmista → Sospechosa
    R2: SI confirmación_oficial == FALSO       → Probablemente Falsa
    R3: SI fuente reconocida Y sin contradicción → Probablemente Verdadera
    """
    print("\n" + "="*50)
    print("  REGLAS DE PRODUCCIÓN APLICADAS (SI → ENTONCES)")
    print("="*50)

    if peso_total >= 4:
        print("  R1 + R2 activadas: Múltiples alertas graves (fuente, desmentido, etc.)")
        return "\n[RESULTADO] 🚨  Clasificación: PROBABLEMENTE FALSA"
    elif peso_total >= 2:
        print("  R1 activada: Múltiples indicadores de sospecha detectados")
        return "\n[RESULTADO] ⚠️  Clasificación: NECESITA VERIFICACIÓN ADICIONAL"
    elif peso_total == 1:
        print("  Indicadores leves detectados (ej. solo fuente desconocida).")
        return "\n[RESULTADO] 🟡  Clasificación: LIGERA SOSPECHA / INFO NEUTRAL"
    else:
        print("  R3 activada: Fuente confiable, sin indicadores de alerta")
        return "\n[RESULTADO] ✅  Clasificación: PROBABLEMENTE VERDADERA"


# ==========================================
# FLUJO PRINCIPAL
# ==========================================
def main():
    print("\n" + "="*60)
    print("  SISTEMA INTELIGENTE DE CLASIFICACIÓN DE FAKE NEWS")
    print("  Universidad Autónoma de Chiapas — IA 7°M")
    print("="*60)
    print("\nPor favor, ingresa el enlace de la noticia a analizar:\n")

    # --- ENTRADA ---
    url = input("1. Enlace (URL) de la noticia: ").strip()

    # Scraping con newspaper3k
    print("\nExtrayendo información de la URL...")
    titulo = ""
    cuerpo = ""
    fuente = extraer_dominio(url)

    try:
        article = Article(url, language='es')
        article.download()
        article.parse()

        titulo = article.title
        cuerpo = article.text

    except ArticleException as e:
        print(f"\n⚠️  Advertencia: No se pudo acceder automáticamente al enlace (común en redes sociales o sitios protegidos).")
    except Exception as e:
        print(f"\n⚠️  Advertencia: Error inesperado al procesar la URL.")

    # Fallback manual si el scraping falla (ej. Facebook, Twitter o sitios que bloquean bots)
    if not titulo or not cuerpo:
        print("\n[!] El sistema requiere el contenido para analizar el sensacionalismo y contexto local.")
        print("⚠️  IMPORTANTE: Pega el texto en UN SOLO PÁRRAFO (sin saltos de línea) para evitar errores en la consola.")
        titulo_manual = input("Por favor, ingresa SOLO EL TÍTULO de la publicación: ").strip()
        if titulo_manual:
            titulo = titulo_manual
        cuerpo_manual = input("Opcional - Ingresa texto adicional (en un solo bloque sin dar Enter): ").strip()
        if cuerpo_manual:
            cuerpo = cuerpo_manual

    print(f"\n[+] Título  : {titulo if titulo else '(Sin título)'}")
    print(f"[+] Dominio : {fuente}")

    desmentido = input(
        "\n2. ¿Ha sido desmentida oficialmente por algún medio reconocido? (escribe solo 'si' o 'no'): "
    ).strip()

    # --- PROCESAMIENTO ---
    print("\nAplicando heurísticas y representación del conocimiento...")

    p_sens  = heuristica_sensacionalismo(titulo, cuerpo)
    p_verif = heuristica_verificabilidad(fuente)
    p_ctx   = heuristica_contexto_local(titulo, cuerpo)
    p_cons  = heuristica_consistencia(desmentido)

    peso_total = p_verif + p_sens + p_ctx + p_cons

    # --- SALIDA ---
    arbol_de_decision(p_verif, p_sens, p_ctx, p_cons)
    mostrar_tabla_heuristica(p_verif, p_sens, p_ctx, p_cons)
    resultado = clasificar_noticia(peso_total)
    print(resultado)
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()