from pickle import FALSE
import string
from tokenize import Double
from typing import Any, Text, Dict, List
from numpy import double, integer
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from actions.Acciones.actionArchivo import writeArchivo, diccionarioErroresReconocimiento, direcErroresReconocimiento
tarea = None

def reconocerEntidades(texto) -> Text:
    #tipo puede ser participante o tarea
    if (texto != ""):
        indice_espacio = texto.find(' ') + 1
        texto = texto[indice_espacio:]
        #print("Entro a reconocerEntidades con: " + texto)
        return texto
    return None

class ActionReconocerParticipante(Action):
    def name(self) -> Text:
        return "action_reconocer_participante"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = next (tracker.get_latest_entity_values("participante"),None)
        if (nombre_participante == None): #Si no se reconocio el participante se lo busca en el texto ingresado.
            nombre_participante = reconocerEntidades(tracker.latest_message.get("text", ""))
            (diccionarioErroresReconocimiento["participantes"]["participantes_no_reconocidos"]).append(nombre_participante)
            writeArchivo(direcErroresReconocimiento,diccionarioErroresReconocimiento)
        else:
            nombre_participante_ingresado = reconocerEntidades(tracker.latest_message.get("text", ""))
            if (nombre_participante != nombre_participante_ingresado): #Si lo reconocido es no igual a lo ingresado
                 (diccionarioErroresReconocimiento["participantes"]["participantes_mal_reconocidos"]).append((nombre_participante, nombre_participante_ingresado))
                 writeArchivo(direcErroresReconocimiento,diccionarioErroresReconocimiento)
        message = "El participante renocido es " + str(nombre_participante)
        dispatcher.utter_message(text=message)
        return [SlotSet("participante",str(nombre_participante))]
    
class ActionReconocerTarea(Action):
    def name(self) -> Text:
        return "action_reconocer_tarea"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global tarea
        tarea = next (tracker.get_latest_entity_values("tarea"),None)
        print("tarea identificada: " + tarea)
        if (tarea == None): #Si no se reconocio la tarea se lo busca en el texto ingresado.
            tarea = reconocerEntidades(tracker.latest_message.get("text", ""))
            (diccionarioErroresReconocimiento["tareas"]["tareas_no_reconocidas"]).append(tarea)
            writeArchivo(direcErroresReconocimiento,diccionarioErroresReconocimiento)
        else:
            tarea_ingresada = reconocerEntidades(tracker.latest_message.get("text", ""))
            print("tarea ingresada: " + tarea_ingresada)
            if (tarea != tarea_ingresada): #Si lo reconocido es no igual a lo ingresado
                 (diccionarioErroresReconocimiento["tareas"]["tareas_mal_reconocidas"]).append((tarea, tarea_ingresada))
                 writeArchivo(direcErroresReconocimiento,diccionarioErroresReconocimiento)
        message = "La tarea renocida es " + str(tarea)
        dispatcher.utter_message(text=message)
        writeArchivo(direcErroresReconocimiento,diccionarioErroresReconocimiento)
        #De momento no se usa el slot
        return [SlotSet("tarea",str(tarea))]