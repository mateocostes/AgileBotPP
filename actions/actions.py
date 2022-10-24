# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from tokenize import Double
from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
import json
import random

from sqlalchemy import case

#
#

def readArchivo(dire)-> dict:
        with open(dire,"r") as archivo:
            diccionario = json.loads(archivo.read()) 
            archivo.close()
        return diccionario

def writeArchivo(dire,diccionario):
        with open(dire,"w") as archivo:
            json.dump(diccionario,archivo)
            archivo.close()
        
direcParticipantes = "actions/participantes.json"
diccionarioParticipantes = readArchivo(direcParticipantes)
direcVotacion = "actions/votacion.json"
diccionarioVotacion = readArchivo(direcVotacion)
lista_key = diccionarioParticipantes.keys()
# VOTOS [0,0.5,1,2,3,5,8,20,40,100], 1000 = infinito, -2 = cafe, -3 = signo de pregunta
lista_votos = [0,0.5,1,2,3,5,8,20,40,100]

def tieneHablidad(tarea,nombre_partipante) -> bool:
    for habilidad in diccionarioParticipantes[nombre_partipante]["Habilidades"]: #Recorro todas las habilidades del participante
        if (habilidad in tarea): #Si la habilidad aparece en la tarea quiere decir que tiene conocimiento de la misma
            print("Entro con la habilidad " + habilidad)
            return True
    return False

class ActionVotarPrimeraVot(Action):
    def name(self) -> Text:
        return "action_votar_primeravot"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_partipante = next (tracker.get_latest_entity_values("participante"),None)
        tarea = next (tracker.get_latest_entity_values("tarea"),None)
        voto = ""
        message = ""
        print("Nombre del participante: " + nombre_partipante)
        print("Tarea actual: " + tarea)
        if (nombre_partipante != None and nombre_partipante in lista_key and tarea != None):
            personalidad = diccionarioParticipantes[nombre_partipante]["Personalidad"]
            print("Personalidad del participante: " + personalidad)
            if (personalidad == "Arriesgado"):
                if (tieneHablidad(tarea,nombre_partipante)):
                    voto = random.choice([0,0.5,1])
                    message = "Voto " + str(voto)
                else:
                    voto = random.choice([2,3,5])
                    message = "Voto " + str(voto)
            else:
                if (personalidad == "Precavido"):
                    if (tieneHablidad(tarea,nombre_partipante)):
                        voto = random.choice([2,5])
                        message = "Voto " + str(voto)
                    else:
                        voto = random.choice([8,20])
                        message = "Voto " + str(voto)
                else:
                    if (personalidad == "Neutral"):
                        if (tieneHablidad(tarea,nombre_partipante)):
                            voto = random.choice([1,2,3,5])
                            message = "Voto " + str(voto)
                        else:
                            voto = random.choice([8,13,20])
                            message = "Voto " + str(voto)
                    else:
                        if (personalidad == "Negativo"):
                            if ((tieneHablidad(tarea,nombre_partipante))):
                                voto = random.choice([20,40])
                                message = "Voto " + str(voto)
                            else:
                                voto = random.choice([40,100,1000]) #faltaria ver la votacion -2 (Cafe) -3 (Signo pregunta)
                                message = "Voto " + str(voto)
            (diccionarioVotacion[nombre_partipante]["Voto"]).append(voto) #Agrego a un json el voto
            (diccionarioVotacion[nombre_partipante]["Tarea"]).append(tarea) #Agrego a un json la tarea
            writeArchivo(direcVotacion,diccionarioVotacion)
        else: message = "El participante " + nombre_partipante + " no existe o la tarea esta mal definida"
        dispatcher.utter_message(text=message)
        return []
        
        
class ActionOpinionPrimeraVot(Action):
    def name(self) -> Text:
        return "action_motivo_primeravot"
        
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_partipante = next (tracker.get_latest_entity_values("participante"),None)
        tarea = diccionarioVotacion[nombre_partipante]["Tarea"]
        tarea = str(tarea).replace('[','') #elimino caracteres indeseados
        tarea = tarea.replace(']','') #elimino caracteres indeseados
        voto = diccionarioVotacion[nombre_partipante]["Voto"]
        voto = str(voto).replace('[','') #elimino caracteres indeseados
        voto = voto.replace(']','') #elimino caracteres indeseados
        message = ""
        if (nombre_partipante != None and nombre_partipante in lista_key):
            personalidad = diccionarioParticipantes[nombre_partipante]["Personalidad"]
            if (personalidad == "Arriesgado"):
                if (tieneHablidad(tarea,nombre_partipante)):
                    message = "Vote " + voto + " ya que tengo conocimientos sobre el tema"
                else:
                    message = "Vote " + voto + " a la tarea " + tarea + " ya que creo que puedo resolverla en poco tiempo"
            else:
                if (personalidad == "Precavido"):
                    if (tieneHablidad(tarea,nombre_partipante)):
                        message = "Tengo conocimientos sobre la tarea " + tarea + " y prefiero resolverla tranquilo y llegar a tiempo, por ello vote" + voto
                    else:
                        message = "No tengo conocimiento sobre la tarea y prefiero no arriesgarme"
                else:
                    if (personalidad == "Neutral"):
                        if (tieneHablidad(tarea,nombre_partipante)):
                            message = "Realice algunas tareas similares y se que me puede llevar " + voto + "puntos realizarla"
                        else:
                            message = "Nunca realice algo similar y por ello vote " + voto
                    else:
                        if (personalidad == "Negativo"):
                            if (tieneHablidad(tarea,nombre_partipante)):
                                message = "Tengo conocimientos sobre la tarea " + tarea + " e igualmente voy a tardar mucho, por ello vote " + voto
                            else:
                                if (voto != str(-2) and voto != str(-3) and voto != str(1000)):
                                    message = "No tengo idea de la tarea " + tarea + " y se que no vamos a poder realizarla, por ello vote " + voto
                                else:
                                    if voto == str(-2):
                                         message = "No tengo idea de la tarea " + tarea + " y se que no vamos a poder realizarla, necesito un descanso"
                                    else:
                                        if voto == str(-3):
                                             message = "Sinceramente no entiendo la tarea " + tarea
                                        else:
                                            if voto == str(1000):
                                                 message = "La tarea " + tarea + " es imposible de realizar"
                                            else:
                                                message = "Error al generar el motivo"
        else: message = "El participante " + nombre_partipante + " no existe."
        dispatcher.utter_message(text=message)
        return[]

class ActionVotarSegundaVot(Action):
    def name(self) -> Text:
        return "action_votar_segundavot"

    def votoSiguiente(self, voto) -> Text:
        if voto == 100:
            return 100
        else:
            posicion = lista_votos.index(voto)
            return lista_votos(posicion+1)

    def votoAnterior(self, voto) -> Text:
        if voto == 0:
            return 0
        else:
            posicion = lista_votos.index(voto)
            return lista_votos(posicion-1)

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_partipante = next (tracker.get_latest_entity_values("participante"),None)
        tarea = next (tracker.get_latest_entity_values("tarea"),None)
        voto_minimo = next (tracker.get_latest_entity_values("voto_minimo"),None)
        voto_minimo = str(voto_minimo)
        print("Voto minimo: " + voto_minimo)
        voto_maximo = next (tracker.get_latest_entity_values("voto_maximo"),None)
        voto_maximo = str(voto_maximo)
        print("Voto maximo: " + voto_maximo)
        tarea = diccionarioVotacion[nombre_partipante]["Tarea"]
        tarea = str(tarea).replace('[','') #elimino caracteres indeseados
        tarea = tarea.replace(']','') #elimino caracteres indeseados
        voto = diccionarioVotacion[nombre_partipante]["Voto"]
        voto = str(voto).replace('[','') #elimino caracteres indeseados
        voto = voto.replace(']','') #elimino caracteres indeseados
        message = ""
        if (nombre_partipante != None and nombre_partipante in lista_key and voto_minimo != None and voto_maximo != None):
            personalidad = diccionarioParticipantes[nombre_partipante]["Personalidad"]
            if (personalidad == "Arriesgado"):
                if (voto != voto_minimo):
                    voto = voto_minimo
                else: 
                    voto = self.votoAnterior(voto)
                message = "Voto " + voto
            else:
                if (personalidad == "Precavido"):
                    if (voto != voto_maximo):
                        voto = voto_maximo
                    else: 
                        voto = self.votoSiguiente(voto)
                    message = "Voto " + voto
                else:
                    if (personalidad == "Neutral"):
                        if (voto == voto_minimo):
                            voto = self.votoSiguiente(voto)
                        else: 
                            if (voto == voto_maximo):
                                voto = self.votoAnterior(voto)
                        message = "Voto " + voto
                    else:
                        if (personalidad == "Negativo"):
                            if (voto != str(-2) and voto != str(-3) and voto != str(1000)): #Si no voto las cartas especiales
                                if (voto == voto_minimo):
                                    voto = self.votoSiguiente(voto)  
                            else:
                                voto = voto_maximo
                            message = "Voto " + voto
        else: message = "El participante " + nombre_partipante + " no existe o los votos estan mal definidos - voto:" + voto
        dispatcher.utter_message(text=message)
        return []
        
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
        self.reiniciarVotacion()
        message = "Ceremonia Finalizada"
        dispatcher.utter_message(text=message)
        return []