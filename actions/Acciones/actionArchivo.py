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

def readArchivo(dire)-> dict:
        with open(dire,"r") as archivo:
            diccionario = json.loads(archivo.read()) 
            archivo.close()
        return diccionario

def writeArchivo(dire,diccionario):
        with open(dire,"w") as archivo:
            json.dump(diccionario,archivo, indent=4)
            archivo.close()
        
api_endpoint_set_vector = "http://9742-201-235-167-187.ngrok-free.app/dispatcher/set-vector"
api_endpoint_get_vector = "http://9742-201-235-167-187.ngrok-free.app/dispatcher/get-vector"
diccionarioParticipantes = ""
direcVotacion = "actions/votacion.json"
diccionarioVotacion = readArchivo(direcVotacion)
direcErroresReconocimiento = "actions/erroresReconocimiento.json"
diccionarioErroresReconocimiento = readArchivo(direcErroresReconocimiento)

def vectorParticipante(nombre_participante):
    response = requests.get(url=api_endpoint_get_vector).text
    diccionarioParticipantes = json.loads(response)
    for participante in diccionarioParticipantes:
        if (participante["nickname"] == nombre_participante):
            return participante["vector"]
    return None

def reiniciarVotacion(diccionario, direcion):
    for nombre in diccionario.keys():
        for valor in diccionario[nombre]:
            (diccionario[nombre][valor]).clear()
    writeArchivo(direcion, diccionario)

class ActionFinalizarCeremonia(Action):
    def name(self) -> Text:
        return "action_finalizar_ceremonia"
    
    def reiniciarVotacion(self):
        for nombre in diccionarioVotacion.keys():
            for valor in diccionarioVotacion[nombre]:
                (diccionarioVotacion[nombre][valor]).clear()
        writeArchivo(direcVotacion, diccionarioVotacion)

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        reiniciarVotacion(diccionarioVotacion, direcVotacion)
        message = "Ceremonia Finalizada"
        dispatcher.utter_message(text=message)
        return []
    
class ActionInicializarErrores(Action):
    def name(self) -> Text:
        return "action_inicializar_errores"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        reiniciarVotacion(diccionarioErroresReconocimiento, direcErroresReconocimiento)
        message = "Json de errores reconocidos inicializado"
        dispatcher.utter_message(text=message)
        return []