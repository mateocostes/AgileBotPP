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
from actions.Acciones.actionArchivo import vectorParticipante, writeArchivo, diccionarioVotacion, direcVotacion
# VOTOS [0,0.5,1,2,3,5,8,20,40,100], 1000 = infinito, -2 = cafe, -3 = signo de pregunta
lista_votos = ["0","0.5","1","2","3","5","8","13","20","40","100","1000"]

def tieneHablidad(tarea, nombre_participante, vector_participante) -> bool:
    for habilidad in vector_participante["habilidades"]: #Recorro todas las habilidades del participante
        if (habilidad in tarea): #Si la habilidad aparece en la tarea quiere decir que tiene conocimiento de la misma
            (diccionarioVotacion[nombre_participante]["Habilidad"]).append(habilidad) #Agrego la habilidad a un json en caso de tener
            print("Entro con la habilidad " + habilidad)
            return True
    return False

def conoceLenguaje(tarea, nombre_participante, vector_participante) -> bool:
    for lenguaje in vector_participante["lenguajes"]: #Recorro todas los lenguajes del participante
        if (lenguaje in tarea): #Si la habilidad aparece en la tarea quiere decir que tiene conocimiento de la misma
            (diccionarioVotacion[nombre_participante]["Lenguaje"]).append(lenguaje) #Agrego el lenguaje a un json en caso de tener
            print("Entro con el lenguaje " + lenguaje)
            return True
    return False

def acotarVotos(lista_votos, mayores, valor):
    votos_local = lista_votos
    if (mayores):
        posicion_max = len(votos_local) - valor
        return votos_local[0:posicion_max]
    else:
        posicion_max = len(votos_local)
        return votos_local[valor:posicion_max] #Por ej si acoto la lista en 3 posiciones al inicio, la misma comienza en la posicion 3

def acotarVotosPersonalidad(lista_votos, valor):
    votos_local = lista_votos
    if (valor == 0):
        return acotarVotos(votos_local, False, 3)
    elif (valor == 1):
        return acotarVotos(votos_local, False, 2)
    elif (valor == 2):
        return acotarVotos(votos_local, False, 1)
    elif (valor == 3):
        return acotarVotos(votos_local, True, 1)
    elif (valor == 4):
        return acotarVotos(votos_local, True, 2)
    elif (valor == 5):
        return acotarVotos(votos_local, True, 3)

def votarPrimeraVotacionPP(nombre_participante, tarea) -> int:
    voto = 8 #default
    #Si vectorParticipante(nombre_participante) != None quiere decir que existe el participante
    if (nombre_participante != None and tarea != None):
        vector_participante = vectorParticipante(nombre_participante)
        if (vector_participante != None):
            print("Nombre del participante: " + str(nombre_participante))
            print("Tarea actual: " + str(tarea))
            valor_riesgo = vector_participante["riesgo"]
            valor_optimismo = vector_participante["optimismo"]
            print("Riesgo del participante: " + str(valor_riesgo))
            print("Optimismo del participante: " + str(valor_optimismo))
            if (tieneHablidad(tarea, nombre_participante, vector_participante)):
                lista_votos_local = acotarVotos(lista_votos, True, 2)
            else:  
                lista_votos_local = acotarVotos(lista_votos, False, 2)
            if (conoceLenguaje(tarea, nombre_participante, vector_participante)):
                lista_votos_local = acotarVotos(lista_votos_local, True, 2)
            else:  
                lista_votos_local = acotarVotos(lista_votos_local, False, 2)
            lista_votos_local = acotarVotosPersonalidad(lista_votos_local,valor_riesgo)
            lista_votos_local = acotarVotosPersonalidad(lista_votos_local,valor_optimismo)
            voto = random.choice(lista_votos_local)
            (diccionarioVotacion[nombre_participante]["Voto"]).append(voto) #Agrego a un json el voto
            (diccionarioVotacion[nombre_participante]["Tarea"]).append(tarea) #Agrego a un json la tarea
            writeArchivo(direcVotacion,diccionarioVotacion)
    return voto

class ActionVotarPrimeraVot(Action):
    def name(self) -> Text:
        return "action_votar_primeravot"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = str(tracker.get_slot("participante"))
        tarea = str(tracker.get_slot("tarea"))
        voto = votarPrimeraVotacionPP(nombre_participante, tarea)
        message = str(voto)
        dispatcher.utter_message(text=message)
        return []
    

class ActionVotarSegundaVot(Action):
    def name(self) -> Text:
        return "action_votar_segundavot"
    
    def acotarVotosMenorMayor(self, voto_minimo, voto_maximo):
        votos_local = lista_votos
        posmin = votos_local.index(voto_minimo)
        posmax = votos_local.index(voto_maximo) + 1
        return votos_local[posmin:posmax]

    def acotarVotosAdaptabilidad(self, lista_votos, valor_adaptabilidad, voto):
        votos_local = lista_votos
        if (voto != votos_local[0]) or (valor_adaptabilidad != 0):
            distancia = self.calcularDistanciaVoto(votos_local, voto)
            print("Distancia: " + str(distancia))
            if (distancia != -1):
                if (valor_adaptabilidad == 1):
                    if (distancia > 4):
                        voto = votos_local[4]
                elif (valor_adaptabilidad == 2):
                    if (distancia > 3):
                        voto = votos_local[3]
                elif (valor_adaptabilidad == 3):
                    if (distancia > 2):
                        voto = votos_local[2]
                elif (valor_adaptabilidad == 4):
                    voto = votos_local[1]
                elif (valor_adaptabilidad == 5):
                    voto = votos_local[0]
        return voto

    def calcularDistanciaVoto(self, lista_votos, voto):
        distancia = 0
        for voto_local in lista_votos:
            if (voto_local == voto): #Utilizo in ya que voto es string
                return distancia
            else: distancia += 1
        return -1 #Error al calcular distancia

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = next (tracker.get_latest_entity_values("participante"),None)
        voto_minimo = next (tracker.get_latest_entity_values("voto_minimo"),None)
        voto_maximo = next (tracker.get_latest_entity_values("voto_maximo"),None)
        print("Voto minimo: " + str(voto_minimo))
        print("Voto maximo: " + str(voto_maximo))
        lista_votos_local = self.acotarVotosMenorMayor(voto_minimo, voto_maximo)
        print("lista votos local:" + str(lista_votos_local))
        if (voto_maximo == "1000"): #Para que no haya voto 1000
            voto_maximo = "100"
        voto = voto_minimo #default
        message = str(voto) #default
        if (nombre_participante != None and voto_minimo != None and voto_maximo != None):
            vector_participante = vectorParticipante(nombre_participante)
            if(vector_participante != None):
                if (diccionarioVotacion[nombre_participante]["Voto"] != []): #Consulto si tiene un valor en la primera votacion
                    voto = diccionarioVotacion[nombre_participante]["Voto"]
                    voto = voto[0] #Me quedo solo con el numero sin las comillas simples, corchetes y etc
                    print("Voto primera votacion: " + str(voto))
                valor_adaptabilidad = vector_participante["adaptabilidad"]
                print("Adaptabilidad del participante: " + str(valor_adaptabilidad))
                voto = self.acotarVotosAdaptabilidad(lista_votos_local, valor_adaptabilidad, voto)
                message = voto
        dispatcher.utter_message(text=message)
        return []