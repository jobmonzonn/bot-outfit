# Sistema Experto para Asistencia en Diseño de Indumentaria

## Descripción
Este sistema experto está diseñado para asistir a estudiantes de la carrera de Diseño de Indumentaria en la selección y combinación de outfits, considerando principios estéticos, estilos predefinidos y preferencias individuales.

## Características Principales
- Sistema Multiagente con Agente Difuso y Agente Probabilístico
- Evaluación estética basada en lógica difusa
- Aprendizaje por refuerzo basado en feedback del usuario
- Recomendaciones personalizadas de outfits
- Implementación siguiendo la metodología CommonKADS

## Requisitos
- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación
1. Clonar el repositorio
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Estructura del Proyecto
- `sistema_experto.py`: Implementación principal del sistema experto
- `requirements.txt`: Dependencias del proyecto
- `README.md`: Documentación del proyecto

## Uso
```python
from sistema_experto import SistemaExperto

# Crear instancia del sistema
sistema = SistemaExperto()

# Evaluar un outfit
caracteristicas = {
    'elegancia': 8,
    'casualidad': 3
}
resultado = sistema.evaluar_outfit(caracteristicas)
print(resultado)
```

## Modelado CommonKADS
El sistema implementa las 7 capas de CommonKADS:
1. Modelo de organización
2. Modelo de tareas
3. Modelo de agentes
4. Modelo de conocimiento
5. Modelo de comunicación
6. Modelo de diseño
7. Nivel de implementación

## Contribución
Las contribuciones son bienvenidas. Por favor, asegúrate de:
1. Hacer fork del proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## Licencia
Este proyecto está bajo la Licencia MIT. 