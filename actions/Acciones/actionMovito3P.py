from pickle import FALSE
import string
from tokenize import Double
from typing import Any, Text, Dict, List
from numpy import double, integer
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
import json
import random
import requests
from flask import jsonify
import yaml
from actions.Acciones.actionMotivoPP import motivoHabilidad, motivoLenguaje, motivoHabLen
from actions.Acciones.actionVotarPP import diccionarioVotacion, lista_votos, vectorParticipante

def darMotivo(valor_riesgo, valor_optimismo, nombre_partipante, votos, tarea) -> string:
    votos_menores = lista_votos[0:7]
    motivo = motivoHabLen(motivoHabilidad(nombre_partipante), motivoLenguaje(nombre_partipante), votos, valor_riesgo, votos_menores)
    lista_motivos = []
    return ""

class ActionMotivoEstimacion3Puntos(Action):
    def name(self) -> Text:
        return "action_motivo_estimacion_3_puntos"
    
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = str(tracker.get_slot("participante"))
        message = "Vote eso ya que no sabia que votar" #default
        votos = (5,8,13) #Votos default. El primer voto es optimista, luego realistas y por ultimo pesimista
        tarea = ""
        if (nombre_participante != None):
            vector_participante = vectorParticipante(nombre_participante)
            if(vector_participante != None):
                if (diccionarioVotacion[nombre_participante]["Voto"] != []): #Consulto si tiene un valor en la primera votacion
                    votos = diccionarioVotacion[nombre_participante]["Voto3puntos"][len(diccionarioVotacion[nombre_participante]["Voto3puntos"])-1]
                    print("Voto primera votacion: " + str(votos))
                if (diccionarioVotacion[nombre_participante]["Tarea"] != []):
                    tarea = diccionarioVotacion[nombre_participante]["Tarea"][len(diccionarioVotacion[nombre_participante]["Tarea"])-1]
                    print("Tarea: " + str(tarea))
                valor_riesgo = vector_participante["riesgo"]
                valor_optimismo = vector_participante["optimismo"]
                if (valor_riesgo != "" and valor_optimismo != "" and votos != "" and tarea != ""):
                    message = darMotivo(valor_riesgo, valor_optimismo, nombre_participante, votos, tarea)
        dispatcher.utter_message(text=message)
        return []