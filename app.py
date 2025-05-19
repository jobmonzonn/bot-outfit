from flask import Flask, render_template, request, jsonify, session
from sistema_experto import SistemaExperto
from base_conocimiento import BaseConocimiento, Estilo, Temporada, colores_recomendados_por_ocasion
from referencias_outfit import buscar_referencia
import json
import re
from uuid import uuid4
import random

app = Flask(__name__)
app.secret_key = 'fashionbot-secret-key'

sistema = SistemaExperto()
base_conocimiento = BaseConocimiento()
feedback_historial = []

# Flujo modular de filtros
FLUJO = [
    {"clave": "ocasion", "pregunta": "¿Para qué ocasión es el outfit?", "opciones": ["Diario", "Trabajo", "Facultad", "Fiesta", "Cita", "Evento formal", "Otro"]},
    {"clave": "genero", "pregunta": "¿Para qué género es el outfit?", "opciones": ["Hombre", "Mujer", "Sin especificar"]},
    {"clave": "temporada", "pregunta": "¿Qué temporada?", "opciones": ["Primavera", "Verano", "Otoño", "Invierno"]},
    {"clave": "estilo", "pregunta": "¿Qué estilo buscás?", "opciones": ["Casual", "Urbano", "Elegante", "Deportivo"]},
    {"clave": "colores", "pregunta": "¿Colores preferidos? (Elige 1 o más)", "opciones": ["Blanco", "Negro", "Gris", "Beige", "Azul", "Rojo", "Verde", "Marrón", "Sin preferencia"], "multiple": True}
]

# Estado de conversación por sesión
conversaciones = {}

BASES_OUTFIT = {
    ("Hombre", "Elegante"): [
        "Camisa celeste, pantalón de vestir gris claro, mocasines marrón claro y reloj sencillo.",
        "Saco azul marino, camisa blanca, pantalón de vestir negro y zapatos oxford.",
        "Camisa blanca, blazer gris, pantalón de vestir azul y zapatos marrón oscuro.",
        "Camisa lila, pantalón de lino beige y mocasines claros.",
        "Camisa rayada, pantalón de vestir marrón y zapatos derby."
    ],
    ("Mujer", "Elegante"): [
        "Blusa blanca, falda midi beige, tacones nude y cartera pequeña.",
        "Vestido tubo azul marino, blazer claro y sandalias de tacón.",
        "Camisa de seda, pantalón palazzo negro y zapatos de punta.",
        "Vestido largo pastel, sandalias doradas y clutch.",
        "Blazer rosa, pantalón sastre blanco y stilettos."
    ],
    ("Hombre", "Casual"): [
        "Remera blanca de algodón, pantalón chino beige, zapatillas blancas y mochila liviana.",
        "Camiseta azul, jeans rectos y zapatillas deportivas.",
        "Polo gris, bermuda caqui y zapatillas urbanas.",
        "Camisa de lino celeste, bermuda blanca y alpargatas.",
        "Camiseta estampada, jogger verde oliva y zapatillas slip-on."
    ],
    ("Mujer", "Casual"): [
        "Top pastel, jeans mom fit celeste, zapatillas blancas y bolso tote.",
        "Remera oversize, short de jean y sandalias planas.",
        "Blusa estampada, pantalón culotte y zapatillas blancas.",
        "Vestido camisero, sandalias bajas y bandolera.",
        "Camiseta básica, falda midi y zapatillas urbanas."
    ],
    ("Hombre", "Urbano"): [
        "Camiseta oversize, jeans rectos azul, zapatillas deportivas y riñonera.",
        "Buzo con capucha, jogger negro y zapatillas chunky.",
        "Camiseta gráfica, pantalón cargo y gorra.",
        "Campera de jean, camiseta blanca y pantalón jogger.",
        "Camiseta negra, pantalón skinny y zapatillas altas."
    ],
    ("Mujer", "Urbano"): [
        "Camiseta crop, pantalón cargo beige, zapatillas chunky y riñonera.",
        "Buzo oversize, biker shorts y zapatillas deportivas.",
        "Top deportivo, jogger gris y campera de jean.",
        "Camiseta tie-dye, pantalón jogger lila y zapatillas urbanas.",
        "Camiseta estampada, falda de jean y zapatillas altas."
    ],
    ("Hombre", "Deportivo"): [
        "Jogger gris, buzo liviano, zapatillas running y mochila deportiva.",
        "Short deportivo, camiseta dry-fit y zapatillas de entrenamiento.",
        "Pantalón deportivo azul, remera técnica y gorra.",
        "Camiseta sin mangas, short negro y zapatillas running.",
        "Buzo deportivo, jogger azul y zapatillas blancas."
    ],
    ("Mujer", "Deportivo"): [
        "Leggings negras, top deportivo, zapatillas running y mochila deportiva.",
        "Short deportivo, remera dry-fit y zapatillas de entrenamiento.",
        "Jogger lila, buzo crop y zapatillas blancas.",
        "Camiseta dry-fit, leggings estampadas y zapatillas running.",
        "Top deportivo, short rosa y zapatillas urbanas."
    ],
    ("Hombre", "Bohemio"): [
        "Camisa de lino beige, pantalón holgado y sandalias de cuero.",
        "Camiseta estampada, pantalón palazzo y alpargatas.",
        "Camisa floral, bermuda blanca y sandalias."
    ],
    ("Mujer", "Bohemio"): [
        "Blusa boho, falda larga estampada y sandalias planas.",
        "Vestido largo floral, sandalias y bolso de rafia.",
        "Top crochet, pantalón palazzo y sandalias de tiras."
    ],
    ("Hombre", "Vintage"): [
        "Camisa rayada, pantalón recto y mocasines.",
        "Camiseta retro, jeans claros y zapatillas blancas.",
        "Chaleco, camisa blanca y pantalón de vestir."
    ],
    ("Mujer", "Vintage"): [
        "Blusa con lazo, falda midi plisada y zapatos mary jane.",
        "Vestido polka dots, cinturón y zapatos bajos.",
        "Camisa de jean, pantalón recto y mocasines."
    ],
    ("Sin especificar", "Elegante"): [
        "Camisa clara, pantalón de vestir y zapatos formales.",
        "Blusa elegante, falda midi y tacones."
    ],
    ("Sin especificar", "Casual"): [
        "Jeans y camiseta básica, zapatillas cómodas.",
        "Remera de algodón, pantalón holgado y sandalias."
    ],
    ("Sin especificar", "Urbano"): [
        "Camiseta gráfica, pantalón cargo y zapatillas urbanas."
    ],
    ("Sin especificar", "Deportivo"): [
        "Jogger, remera técnica y zapatillas deportivas."
    ]
}

PALETAS_COLORES = [
    "blanco, negro, gris",
    "azul, celeste, blanco",
    "beige, marrón, verde oliva",
    "rojo, rosa, blanco",
    "pastel (lila, menta, celeste, rosa)",
    "colores neutros",
    "verde, marrón, beige",
    "naranja, coral, blanco",
    "violeta, lila, gris"
]

FRASES_RECOMENDACION = [
    "Te recomiendo un look {estilo} ideal para {ocasion} en {temporada}: {base} (Colores sugeridos: {colores_txt}). ¡Perfecto para {ocasion}!",
    "¿Buscas destacar en {ocasion}? Prueba este outfit {estilo}: {base} (Colores: {colores_txt}). ¡Vas a lucir increíble!",
    "Mi sugerencia para {ocasion} en {temporada} es: {base} (Colores recomendados: {colores_txt}). ¡Atrévete a probarlo!",
    "Un conjunto {estilo} para {ocasion}: {base}. Los colores {colores_txt} te van a favorecer mucho.",
    "Para {ocasion} en {temporada}, este look {estilo} es ideal: {base}. ¡Comodidad y estilo asegurados!",
    "¿Tienes {ocasion}? Este outfit {estilo} en tonos {colores_txt} es tu mejor opción: {base}",
    "¡Inspírate! Para {ocasion}, te propongo: {base} (Colores: {colores_txt}). ¡Marca tendencia!",
    "Nada mejor que un look {estilo} para {ocasion}: {base}. ¡Te verás genial en {temporada}!",
    "¿Listo para {ocasion}? Este look {estilo} es tu aliado: {base} (Colores: {colores_txt})",
    "¡Este outfit {estilo} para {ocasion} en {temporada} te hará sentir genial! {base} (Colores: {colores_txt})",
    "¡Conquista {ocasion} con este look {estilo}! {base} (Colores: {colores_txt})",
    "¿Quieres algo diferente para {ocasion}? Este outfit {estilo} es la respuesta: {base} (Colores: {colores_txt})",
    "¡Atrévete a lucir {estilo} en {ocasion}! {base} (Colores: {colores_txt})",
    "Para {ocasion}, nada como este look {estilo}: {base}. ¡Colores: {colores_txt}!"
]

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())
    return session['session_id']

def detectar_peticion_outfit(texto):
    texto = texto.lower()
    palabras_clave = ["outfit", "ropa", "qué me pongo", "look", "vestimenta", "conjunto", "facultad", "universidad", "clases"]
    return any(palabra in texto for palabra in palabras_clave)

def detectar_ocasion(texto):
    texto = texto.lower()
    for opcion in FLUJO[0]["opciones"]:
        if opcion.lower() in texto:
            return opcion
    return None

@app.route('/')
def index():
    return render_template('chat.html')

# Procesamiento simple de lenguaje natural
# Extrae prenda base, estilo, paleta y temporada del mensaje

def extraer_info(texto):
    texto = texto.lower()
    prendas = list(base_conocimiento.prendas.keys())
    estilos = [e.value for e in Estilo]
    temporadas = ['primavera', 'verano', 'otoño', 'invierno']
    paletas = ['neutros', 'calidos', 'fríos', 'frias', 'frios', 'pastel']
    info = {'prenda_base': None, 'estilo': None, 'paleta': None, 'temporada': None}
    for prenda in prendas:
        if prenda in texto:
            info['prenda_base'] = prenda
    for estilo in estilos:
        if estilo in texto:
            info['estilo'] = estilo
    for temporada in temporadas:
        if temporada in texto:
            info['temporada'] = temporada
    for paleta in paletas:
        if paleta in texto:
            info['paleta'] = paleta
    return info

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    mensaje = data.get('message', '')
    session_id = get_session_id()
    estado = conversaciones.get(session_id, {"paso": 0, "respuestas": {}})

    # Permitir reiniciar el flujo si el usuario escribe una nueva consulta de outfit
    if detectar_peticion_outfit(mensaje):
        ocasion_detectada = detectar_ocasion(mensaje)
        if ocasion_detectada:
            respuestas = {"ocasion": ocasion_detectada}
            conversaciones[session_id] = {"paso": 2, "respuestas": respuestas}
            paso = FLUJO[1]
            return jsonify({
                "pregunta": paso["pregunta"],
                "opciones": paso["opciones"],
                "multiple": paso.get("multiple", False)
            })
        else:
            conversaciones[session_id] = {"paso": 1, "respuestas": {}}
            paso = FLUJO[0]
            return jsonify({
                "pregunta": paso["pregunta"],
                "opciones": paso["opciones"],
                "multiple": paso.get("multiple", False)
            })

    # Si está en medio del flujo
    if estado["paso"] > 0 and estado["paso"] <= len(FLUJO):
        paso_actual = FLUJO[estado["paso"] - 1]
        clave = paso_actual["clave"]
        # Guardar respuesta
        if paso_actual.get("multiple", False):
            seleccion = data.get("seleccion", [])
        else:
            seleccion = data.get("seleccion", "")
        estado["respuestas"][clave] = seleccion
        # Avanzar al siguiente paso
        if estado["paso"] < len(FLUJO):
            siguiente = FLUJO[estado["paso"]]
            conversaciones[session_id] = {"paso": estado["paso"] + 1, "respuestas": estado["respuestas"]}
            return jsonify({
                "pregunta": siguiente["pregunta"],
                "opciones": siguiente["opciones"],
                "multiple": siguiente.get("multiple", False)
            })
        else:
            # Generar recomendación final
            recomendacion = generar_recomendacion_outfit(estado["respuestas"])
            conversaciones[session_id] = {"paso": 0, "respuestas": {}}  # Resetear
            return jsonify({"respuesta": recomendacion})

    # Si no es una petición de outfit, respuesta normal
    return jsonify({"respuesta": "¡Hola! ¿En qué puedo ayudarte con tu estilo? Pídeme un outfit para cualquier ocasión y te guío paso a paso."})

# Generador de recomendación textual (puedes mejorar la lógica)
def generar_recomendacion_outfit(respuestas):
    from base_conocimiento import colores_recomendados_por_ocasion
    ocasion = respuestas.get("ocasion", "una ocasión especial")
    genero = respuestas.get("genero", "Sin especificar")
    temporada = respuestas.get("temporada", "")
    estilo = respuestas.get("estilo", "")
    colores = respuestas.get("colores", [])
    if isinstance(colores, str):
        colores = [colores]
    colores = [c.lower() for c in colores if c.lower() != "sin preferencia"]
    tipos_necesarios = ["superior", "inferior", "calzado"]
    seleccionadas = {}
    prendas = base_conocimiento.buscar_outfit(genero, Estilo(estilo.lower()), Temporada(temporada.lower()))
    colores_usados = set()
    colores_disponibles = colores.copy()
    explicacion_colores = []
    fuentes_formal = "Fuente: https://www.gq.com.mx/moda/articulo/ropa-basica-para-la-oficina"
    # 1. Priorizar SIEMPRE los colores seleccionados por el usuario, salvo en ocasiones formales estrictas
    for tipo in tipos_necesarios:
        colores_permitidos = colores_recomendados_por_ocasion(ocasion, tipo)
        prendas_tipo = [p for p in prendas if p.tipo == tipo]
        prenda = None
        color = None
        # OCASIONES FORMALES ESTRICTAS
        if ocasion.lower() in ["trabajo", "evento formal"]:
            # Buscar color permitido y seleccionado
            for c in colores:
                if c in colores_permitidos:
                    for p in prendas_tipo:
                        if c in p.colores and c not in colores_usados:
                            prenda = p
                            color = c
                            break
                    if prenda:
                        break
            # Si no hay prenda con color permitido y seleccionado, buscar solo color permitido
            if not prenda:
                for c in colores_permitidos:
                    for p in prendas_tipo:
                        if c in p.colores and c not in colores_usados:
                            prenda = p
                            color = c
                            break
                    if prenda:
                        break
            # Si no hay prenda con color permitido, buscar cualquier color
            if not prenda:
                for p in prendas_tipo:
                    if p.colores[0] not in colores_usados:
                        prenda = p
                        color = p.colores[0]
                        break
            # Explicación solo si el usuario eligió un color no permitido
            if prenda and color and color not in colores and colores:
                colores_no_usados = [c for c in colores if c not in colores_permitidos]
                if colores_no_usados:
                    for c in colores_no_usados:
                        explicacion_colores.append(f"En ocasiones formales como '{ocasion}', el color '{c}' no es habitual para '{prenda.nombre.lower()}'. Se recomienda optar por colores como: {', '.join(colores_permitidos)}. {fuentes_formal}")
        else:
            # OCASIONES NO FORMALES: priorizar SIEMPRE la selección del usuario
            for c in colores:
                for p in prendas_tipo:
                    if c in p.colores and c not in colores_usados:
                        prenda = p
                        color = c
                        break
                if prenda:
                    break
            # Si no hay prenda en el color elegido, buscar cualquier color
            if not prenda:
                for p in prendas_tipo:
                    if p.colores[0] not in colores_usados:
                        prenda = p
                        color = p.colores[0]
                        break
            # Celebrar la autoexpresión si el color es poco común
            if prenda and color and color in colores and color not in colores_permitidos:
                explicacion_colores.append(f"¡Las {prenda.nombre.lower()} {color} son una elección original! La moda es autoexpresión, así que si te gusta, ¡adelante!")
        if prenda and color:
            seleccionadas[tipo] = (prenda, color)
            colores_usados.add(color)
            if color in colores_disponibles:
                colores_disponibles.remove(color)
        else:
            seleccionadas[tipo] = None
    # Armar la frase solo con las prendas seleccionadas
    partes = []
    colores_finales = []
    faltantes = []
    for tipo in tipos_necesarios:
        if seleccionadas.get(tipo):
            prenda, color = seleccionadas[tipo]
            partes.append(f"{prenda.nombre.lower()} {color}")
            colores_finales.append(color)
        else:
            faltantes.append(tipo)
    base = ", ".join(partes)
    colores_txt = ", ".join(sorted(set(colores_finales)))
    explicacion = " " + " ".join(explicacion_colores) if explicacion_colores else ""
    if faltantes:
        return f"No pude encontrar prenda del tipo: {', '.join(faltantes)} para tu selección. Aquí tienes una sugerencia parcial: {base} (Colores: {colores_txt}).{explicacion}"
    frase = random.choice(FRASES_RECOMENDACION)
    return frase.format(
        ocasion=ocasion.lower(),
        estilo=estilo.lower(),
        temporada=temporada.lower(),
        base=base,
        colores_txt=colores_txt
    ) + explicacion

@app.route('/api/prendas', methods=['GET'])
def obtener_prendas():
    return jsonify(list(base_conocimiento.prendas.keys()))

@app.route('/api/estilos', methods=['GET'])
def obtener_estilos():
    return jsonify([estilo.value for estilo in Estilo])

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.json
    prenda = data.get('prenda')
    feedback = data.get('feedback')
    feedback_historial.append({'prenda': prenda, 'feedback': feedback})
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True) 