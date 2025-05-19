from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class Estilo(Enum):
    ELEGANTE = "elegante"
    CASUAL = "casual"
    DEPORTIVO = "deportivo"
    URBANO = "urbano"
    VINTAGE = "vintage"
    BOHEMIO = "bohemio"

class Temporada(Enum):
    PRIMAVERA = "primavera"
    VERANO = "verano"
    OTONO = "otoño"
    INVIERNO = "invierno"

@dataclass
class Prenda:
    nombre: str
    tipo: str
    estilo: Estilo
    temporada: List[Temporada]
    colores: List[str]
    generos: List[str]

class BaseConocimiento:
    def __init__(self):
        self.prendas = self._inicializar_prendas()

    def _inicializar_prendas(self) -> List[Prenda]:
        colores_principales = ["blanco", "negro", "gris", "beige", "azul", "rojo", "verde", "marrón", "celeste", "lila", "rosa", "nude"]
        prendas = []
        # Definición de tipos y estilos
        tipos = [
            ("superior", [
                "Camiseta básica", "Camisa", "Buzo", "Blusa", "Top", "Blazer", "Remera deportiva", "Camiseta gráfica", "Camisa rayada", "Blusa boho", "Camisa floral"
            ]),
            ("inferior", [
                "Jeans", "Pantalón de vestir", "Pantalón cargo", "Jogger", "Short", "Falda", "Falda midi", "Falda plisada", "Falda larga", "Leggings", "Bermuda", "Pantalón palazzo", "Vestido"
            ]),
            ("calzado", [
                "Zapatillas", "Zapatos", "Botines", "Sandalias", "Tacones", "Mocasines", "Alpargatas"
            ])
        ]
        estilos = [Estilo.CASUAL, Estilo.ELEGANTE, Estilo.DEPORTIVO, Estilo.URBANO, Estilo.VINTAGE, Estilo.BOHEMIO]
        temporadas = [Temporada.PRIMAVERA, Temporada.VERANO, Temporada.OTONO, Temporada.INVIERNO]
        generos = ["Hombre", "Mujer"]
        # Generar combinaciones
        for estilo in estilos:
            for temporada in temporadas:
                for genero in generos:
                    for tipo, nombres in tipos:
                        for nombre in nombres:
                            for color in colores_principales:
                                # Evitar combinaciones poco realistas (ej: vestido para hombre solo en vintage/bohemio/elegante)
                                if nombre.startswith("Vestido") and genero == "Hombre" and estilo not in [Estilo.VINTAGE, Estilo.BOHEMIO, Estilo.ELEGANTE]:
                                    continue
                                if nombre.startswith("Falda") and genero == "Hombre":
                                    continue
                                if nombre in ["Top", "Leggings"] and genero == "Hombre":
                                    continue
                                if nombre in ["Tacones"] and genero == "Hombre":
                                    continue
                                if nombre in ["Mocasines", "Zapatos", "Botines", "Alpargatas"] and estilo == Estilo.DEPORTIVO:
                                    continue
                                prendas.append(Prenda(
                                    nombre=f"{nombre}",
                                    tipo=tipo,
                                    estilo=estilo,
                                    temporada=[temporada],
                                    colores=[color],
                                    generos=[genero]
                                ))
        return prendas

    def buscar_outfit(self, genero, estilo, temporada):
        prendas = [p for p in self.prendas if genero in p.generos and p.estilo == estilo and temporada in p.temporada]
        return prendas

    def colores_compatibles(self, prendas, colores_usuario):
        # Si el usuario eligió colores, priorizar solo prendas que tengan esos colores
        resultado = []
        prendas_restantes = prendas.copy()
        colores_usuario = [c.lower() for c in colores_usuario] if colores_usuario else []
        # 1. Intentar asignar solo prendas con colores del usuario
        for prenda in prendas:
            color = None
            if colores_usuario:
                colores_validos = [c for c in prenda.colores if c in colores_usuario]
                if colores_validos:
                    color = colores_validos[0]
                    resultado.append((prenda, color))
                    prendas_restantes.remove(prenda)
        # 2. Si faltan prendas para completar el outfit, completar con cualquier color disponible
        for prenda in prendas_restantes:
            color = prenda.colores[0]
            resultado.append((prenda, color))
        return resultado

# Colores recomendados por tipo de prenda y ocasión (según reglas de moda realistas)
COLORES_OCASION = {
    "facultad": {
        "superior": ["blanco", "negro", "gris", "azul", "beige", "verde", "celeste"],
        "inferior": ["azul", "negro", "gris", "beige", "marrón"],
        "calzado": ["blanco", "negro", "gris", "beige", "marrón", "azul"]
    },
    "trabajo": {
        "superior": ["blanco", "negro", "gris", "azul", "beige", "celeste"],
        "inferior": ["negro", "gris", "azul", "beige", "marrón"],
        "calzado": ["negro", "marrón", "beige", "gris"]
    },
    "fiesta": {
        "superior": ["negro", "blanco", "rojo", "azul", "lila", "rosa", "beige", "gris"],
        "inferior": ["negro", "blanco", "gris", "azul", "beige", "lila"],
        "calzado": ["negro", "blanco", "rojo", "beige", "gris", "nude"]
    },
    "diario": {
        "superior": ["blanco", "negro", "gris", "azul", "beige", "verde", "celeste", "rosa"],
        "inferior": ["azul", "negro", "gris", "beige", "marrón", "blanco"],
        "calzado": ["blanco", "negro", "gris", "beige", "marrón", "azul"]
    },
    "evento formal": {
        "superior": ["blanco", "negro", "gris", "azul", "beige", "celeste"],
        "inferior": ["negro", "gris", "azul", "beige"],
        "calzado": ["negro", "marrón", "beige", "gris"]
    },
    "cita": {
        "superior": ["blanco", "negro", "rojo", "azul", "rosa", "beige", "lila"],
        "inferior": ["negro", "azul", "gris", "beige", "blanco"],
        "calzado": ["negro", "blanco", "rojo", "beige", "gris", "nude"]
    },
    "otro": {
        "superior": ["blanco", "negro", "gris", "azul", "beige", "verde", "celeste", "rojo", "lila", "rosa", "marrón", "nude"],
        "inferior": ["azul", "negro", "gris", "beige", "marrón", "blanco", "rojo", "lila", "rosa", "nude"],
        "calzado": ["blanco", "negro", "gris", "beige", "marrón", "azul", "rojo", "lila", "rosa", "nude"]
    }
}

def colores_recomendados_por_ocasion(ocasion, tipo):
    ocasion = ocasion.lower()
    if ocasion in COLORES_OCASION and tipo in COLORES_OCASION[ocasion]:
        return COLORES_OCASION[ocasion][tipo]
    # Si no hay reglas, permitir todos los colores
    return ["blanco", "negro", "gris", "beige", "azul", "rojo", "verde", "marrón", "celeste", "lila", "rosa", "nude"] 