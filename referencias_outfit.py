referencias_outfit = [
    {
        "imagen": "/static/img/1366_2000.jpg",
        "prenda_base": "camisa",
        "color": ["rosa", "beige"],
        "paleta": "pastel",
        "estilo": "casual elegante",
        "temporada": ["primavera", "verano"],
        "comentario": "Ideal para destacar un estilo veraniego, relajado y sofisticado con colores claros y prendas transpirables."
    },
    {
        "imagen": "/static/img/58181f973dcd771d2e27ee7c213a0214.jpg",
        "prenda_base": "camisa",
        "color": ["celeste", "blanco"],
        "paleta": "fría",
        "estilo": "casual urbano",
        "temporada": ["primavera", "verano"],
        "comentario": "Perfecto para un look simple, limpio y fresco para uso diario con buena armonía de tonos."
    },
    {
        "imagen": "/static/img/a1b1a08bd762f823dbd2d05156a3dca6.jpg",
        "prenda_base": "camisa",
        "color": ["rojo", "beige"],
        "paleta": "cálida",
        "estilo": "smart casual",
        "temporada": ["primavera", "verano"],
        "comentario": "Ideal para quien busque algo clásico pero con carácter, puede usarse como referencia para 'retro moderno' o 'elegancia con personalidad'."
    }
]

def normalizar(texto):
    return texto.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')

def buscar_referencia(prenda_base, estilo, paleta, temporada):
    prenda_base = normalizar(prenda_base)
    estilo = normalizar(estilo)
    paleta = normalizar(paleta)
    temporada = normalizar(temporada)
    for ref in referencias_outfit:
        if (
            normalizar(ref["prenda_base"]) in prenda_base and
            normalizar(ref["estilo"]) in estilo and
            normalizar(ref["paleta"]) in paleta and
            any(normalizar(temporada) == normalizar(t) for t in ref["temporada"])
        ):
            return ref
    return None 