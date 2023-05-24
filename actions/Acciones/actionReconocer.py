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

def reconocerEntidades(texto, tipo) -> Text:
    #tipo puede ser participante o tarea
    if (texto != ""):
        indice_espacio = texto.find(' ') + 1
        texto = texto[indice_espacio:]
        #agrego al nlu el nuevo ejemplo
        """nlu_line = f"- {tipo} [{texto}]({tipo})"
        with open("data/nlu.yml", "r") as nlu_file:
            nlu_data = yaml.safe_load(nlu_file)
        if (tipo == "participante"):
            nlu_data.update([{"intent": "reconocer_participante", "examples": [nlu_line]}])
        else:
            nlu_data.update([{"intent": "votar_primera_votacion", "examples": [nlu_line]}])
        with open("data/nlu.yml", "w") as nlu_file:
            yaml.dump(nlu_data, nlu_file)""" #POR EL MOMENTO NO FUNCIONA
        #fin de agregado
        print("Entro a reconocerEntidades con: " + texto)
        return texto
    return None

class ActionReconocerParticipante(Action):
    def name(self) -> Text:
        return "action_reconocer_participante"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = next (tracker.get_latest_entity_values("participante"),None)
        if (nombre_participante == None): #Si no se reconocio el participante se lo busca en el texto ingresado.
            nombre_participante = reconocerEntidades(tracker.latest_message.get("text", ""), "participante")
        message = "El participante renocido es " + str(nombre_participante)
        dispatcher.utter_message(text=message)
        return [SlotSet("participante",str(nombre_participante))]
    
class ActionReconocerTarea(Action):
    def name(self) -> Text:
        return "action_reconocer_tarea"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tarea = next (tracker.get_latest_entity_values("tarea"),None)
        if (tarea == None): #Si no se reconocio la tarea se lo busca en el texto ingresado.
            tarea = reconocerEntidades(tracker.latest_message.get("text", ""), "tarea")
        message = "La tarea renocida es " + str(tarea)
        dispatcher.utter_message(text=message)
        return [SlotSet("tarea",str(tarea))]