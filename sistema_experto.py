import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
from sklearn.naive_bayes import GaussianNB
import json
import logging

class AgenteDifuso:
    def __init__(self):
        self.setup_fuzzy_system()
        
    def setup_fuzzy_system(self):
        # Variables lingüísticas para evaluación estética
        self.elegancia = ctrl.Antecedent(np.arange(0, 11, 1), 'elegancia')
        self.casualidad = ctrl.Antecedent(np.arange(0, 11, 1), 'casualidad')
        self.adecuacion = ctrl.Consequent(np.arange(0, 11, 1), 'adecuacion')
        
        # Definición de conjuntos difusos
        self.elegancia['baja'] = fuzz.trimf(self.elegancia.universe, [0, 0, 5])
        self.elegancia['media'] = fuzz.trimf(self.elegancia.universe, [0, 5, 10])
        self.elegancia['alta'] = fuzz.trimf(self.elegancia.universe, [5, 10, 10])
        
        self.casualidad['baja'] = fuzz.trimf(self.casualidad.universe, [0, 0, 5])
        self.casualidad['media'] = fuzz.trimf(self.casualidad.universe, [0, 5, 10])
        self.casualidad['alta'] = fuzz.trimf(self.casualidad.universe, [5, 10, 10])
        
        self.adecuacion['baja'] = fuzz.trimf(self.adecuacion.universe, [0, 0, 5])
        self.adecuacion['media'] = fuzz.trimf(self.adecuacion.universe, [0, 5, 10])
        self.adecuacion['alta'] = fuzz.trimf(self.adecuacion.universe, [5, 10, 10])
        
        # Reglas difusas
        self.reglas = [
            ctrl.Rule(self.elegancia['alta'] & self.casualidad['baja'], self.adecuacion['alta']),
            ctrl.Rule(self.elegancia['media'] & self.casualidad['media'], self.adecuacion['media']),
            ctrl.Rule(self.elegancia['baja'] & self.casualidad['alta'], self.adecuacion['alta'])
        ]
        
        self.sistema_control = ctrl.ControlSystem(self.reglas)
        self.simulador = ctrl.ControlSystemSimulation(self.sistema_control)

class AgenteProbabilistico:
    def __init__(self):
        self.modelo = GaussianNB()
        self.historial = []
        
    def actualizar_modelo(self, caracteristicas, feedback):
        self.historial.append((caracteristicas, feedback))
        X = np.array([c for c, _ in self.historial])
        y = np.array([f for _, f in self.historial])
        self.modelo.fit(X, y)
        
    def predecir_probabilidad(self, caracteristicas):
        return self.modelo.predict_proba([caracteristicas])[0]

class SistemaExperto:
    def __init__(self):
        self.agente_difuso = AgenteDifuso()
        self.agente_probabilistico = AgenteProbabilistico()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('SistemaExperto')
    
    def evaluar_outfit(self, caracteristicas):
        try:
            # Evaluación difusa
            self.agente_difuso.simulador.input['elegancia'] = caracteristicas['elegancia']
            self.agente_difuso.simulador.input['casualidad'] = caracteristicas['casualidad']
            self.agente_difuso.simulador.compute()
            evaluacion_difusa = self.agente_difuso.simulador.output['adecuacion']
            
            # Evaluación probabilística
            prob_exito = self.agente_probabilistico.predecir_probabilidad(
                [caracteristicas['elegancia'], caracteristicas['casualidad']]
            )
            
            return {
                'evaluacion_difusa': evaluacion_difusa,
                'probabilidad_exito': prob_exito[1],
                'recomendacion': self._generar_recomendacion(evaluacion_difusa, prob_exito[1])
            }
        except Exception as e:
            self.logger.error(f"Error en evaluación de outfit: {str(e)}")
            return None
    
    def _generar_recomendacion(self, evaluacion_difusa, prob_exito):
        if evaluacion_difusa > 7 and prob_exito > 0.7:
            return "Outfit altamente recomendado"
        elif evaluacion_difusa > 5 and prob_exito > 0.5:
            return "Outfit moderadamente recomendado"
        else:
            return "Considerar ajustes en la combinación"

if __name__ == "__main__":
    # Ejemplo de uso
    sistema = SistemaExperto()
    caracteristicas_ejemplo = {
        'elegancia': 8,
        'casualidad': 3
    }
    resultado = sistema.evaluar_outfit(caracteristicas_ejemplo)
    print(json.dumps(resultado, indent=2)) 