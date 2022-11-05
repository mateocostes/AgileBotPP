# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

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

from sqlalchemy import case, false, true

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
        
api_endpoint_set_vector = "http://181.94.129.186:8088/dispatcher/set-vector"
api_endpoint_get_vector = "http://181.94.129.186:8088/dispatcher/get-vector"
diccionarioParticipantes = ""
direcVotacion = "actions/votacion.json"
diccionarioVotacion = readArchivo(direcVotacion)
lista_votos = ["0","0.5","1","2","3","5","8","13","20","40","100","1000"]
# VOTOS [0,0.5,1,2,3,5,8,20,40,100], 1000 = infinito, -2 = cafe, -3 = signo de pregunta

def vectorParticipante(nombre_participante):
    response = requests.get(url=api_endpoint_get_vector).text
    #print("response: " + response)
    diccionarioParticipantes = json.loads(response)
    for participante in diccionarioParticipantes:
        if (participante["nickname"] == nombre_participante):
            print("Vector: " + str(participante["vector"]))
            return participante["vector"]
    return None

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
    print("Lista votos local: " + str(votos_local))
    if (mayores):
        posicion_max = len(votos_local) - valor
        print("Lista votos local mayores: " + str(votos_local[0:posicion_max]))
        return votos_local[0:posicion_max]
    else:
        posicion_max = len(votos_local)
        print("Lista votos local menores: " + str( votos_local[valor:posicion_max] ))
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

class ActionVotarPrimeraVot(Action):
    def name(self) -> Text:
        return "action_votar_primeravot"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = next (tracker.get_latest_entity_values("participante"),None)
        tarea = next (tracker.get_latest_entity_values("tarea"),None)
        voto = 8 #default
        message = str(voto)
        #Si vectorParticipante(nombre_participante) != None quiere decir que existe el participante
        if (nombre_participante != None and tarea != None):
            vector_participante = vectorParticipante(nombre_participante)
            if (vector_participante != None):
                print("Nombre del participante: " + nombre_participante)
                print("Tarea actual: " + tarea)
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
                message = voto
                (diccionarioVotacion[nombre_participante]["Voto"]).append(voto) #Agrego a un json el voto
                (diccionarioVotacion[nombre_participante]["Tarea"]).append(tarea) #Agrego a un json la tarea
                writeArchivo(direcVotacion,diccionarioVotacion)
        dispatcher.utter_message(text=message)
        return []
        
        
class ActionOpinionPrimeraVot(Action):
    def name(self) -> Text:
        return "action_motivo_primeravot"
    
    def motivoHabilidad(self, nombre_partipante) -> string:
        habilidad = (diccionarioVotacion[nombre_partipante]["Habilidad"])
        if (habilidad != []):
            print("habilidad: " + str(habilidad))
            habilidad = habilidad[0]
            return str(habilidad)
        return ""

    def motivoLenguaje(self, nombre_partipante) -> string:
        lenguaje = (diccionarioVotacion[nombre_partipante]["Lenguaje"])
        if (lenguaje != []):
            lenguaje = lenguaje[0]
            print("lenguaje: " + lenguaje)
            return str(lenguaje)
        return ""

    def motivoRiesgo(self, valor_riesgo) -> string:
        if (valor_riesgo == 0):
            return "precavida"
        elif (valor_riesgo == 1):
            return "bastante precavida"
        elif (valor_riesgo == 2):
            return "poco precavida"
        elif (valor_riesgo == 3):
            return "poco arriesgada"
        elif (valor_riesgo == 4):
            return "bastante arriesgada"
        elif (valor_riesgo == 5):
            return "arriesgada"
    
    def motivoOptimismo(self, valor_optimismo) -> string:
        if (valor_optimismo == 0):
            return "pesimista"
        elif (valor_optimismo == 1):
            return "bastante pesimista"
        elif (valor_optimismo == 2):
            return "un poco pesimista"
        elif (valor_optimismo == 3):
            return "un poco optimista"
        elif (valor_optimismo == 4):
            return "bastante optimista"
        elif (valor_optimismo == 5):
            return "optimista"


    def darMotivo(self, valor_riesgo, valor_optimismo, nombre_partipante, voto, tarea) -> string:
        motivoHabilidad = self.motivoHabilidad(nombre_partipante)
        motivoLenguaje = self.motivoLenguaje(nombre_partipante)
        motivoRiesgo = self.motivoRiesgo(valor_riesgo)
        motivoOptimismo = self.motivoOptimismo(valor_optimismo)
        lista_motivos = []
        if (motivoHabilidad != ""):
            if (motivoLenguaje != ""):
                motivo_1 = "Vote " + str(voto) + " en la tarea, ya que tengo conocimientos sobre " + motivoHabilidad + " en el lenguaje " + motivoLenguaje + " ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_2 = "Al tener experiencia trabajando en " + motivoHabilidad + " con " + motivoLenguaje + " y siendo una persona " + motivoRiesgo + " y " + motivoOptimismo + ", vote " + str(voto) + " en la tarea"
                motivo_3 = "Vote " + str(voto) + " en la tarea " + str(tarea) + ", ya que tengo conocimientos sobre " + motivoHabilidad + " ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_4 = "Al tener experiencia trabajando en " + motivoHabilidad + " con " + motivoLenguaje + " y siendo una persona " + motivoRiesgo + " y " + motivoOptimismo + ", vote " + str(voto) + " en la tarea " + str(tarea)
            else:
                motivo_1 = "Vote " + str(voto) + " en la tarea, ya que tengo conocimientos sobre " + motivoHabilidad + " pero no conozco el lenguaje. Ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_2 = "Al tener experiencia trabajando en " + motivoHabilidad + " pero al no conocer el lenguaje y siendo una persona " + motivoRiesgo + " y " + motivoOptimismo + ", vote " + str(voto) + " en la tarea"
                motivo_3 = "Vote " + str(voto) + " en la tarea" + str(tarea) + ", ya que tengo conocimientos sobre " + motivoHabilidad + " ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_4 = "Al tener experiencia trabajando en " + motivoHabilidad + " y siendo una persona " + motivoRiesgo + " y" + motivoOptimismo + ", vote " + str(voto) + " en la tarea " + str(tarea)
        else:
            if (motivoLenguaje != ""):
                motivo_1 = "Vote " + str(voto) + " en la tarea, ya que trabaje con " + motivoLenguaje + " ,pero no conozco muy bien tema, ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_2 = "Al tener experiencia trabajando con " + motivoLenguaje + " ,pero no conozco muy bien tema, y siendo una persona " + motivoRiesgo + " y " + motivoOptimismo + ", vote " + str(voto) + " en la tarea"
                motivo_3 = "Vote " + str(voto) + " en la tarea " + str(tarea) + ", ya que trabaje con " + motivoLenguaje + " ,ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_4 = "Al tener experiencia trabajando con " + motivoLenguaje + " y siendo una persona " + motivoRiesgo + " y" + motivoOptimismo + ", vote " + str(voto) + " en la tarea " + str(tarea)
            else:
                motivo_1 = "Vote " + str(voto) + " en la tarea, ya que nunca hice nada similar, ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_2 = "Siendo una persona " + motivoRiesgo + " y " + motivoOptimismo + ", vote " + str(voto) + " en la tarea, ya que nunca hice nada similar"
                motivo_3 = "Vote " + str(voto) + " en la tarea" + str(tarea) + ", ademas de ser una persona " + motivoRiesgo + " y " + motivoOptimismo
                motivo_4 = "Siendo una persona " + motivoRiesgo + " y " + motivoOptimismo + ", vote " + str(voto) + " en la tarea " + str(tarea)
        lista_motivos.append(motivo_1)
        lista_motivos.append(motivo_2)
        lista_motivos.append(motivo_3)
        lista_motivos.append(motivo_4)
        return random.choice(lista_motivos)
        
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = next (tracker.get_latest_entity_values("participante"),None)
        message = "Vote eso ya que no sabia que votar" #default
        voto = 8 #default
        tarea = ""
        if (nombre_participante != None):
            vector_participante = vectorParticipante(nombre_participante)
            if(vector_participante != None):
                if (diccionarioVotacion[nombre_participante]["Voto"] != []): #Consulto si tiene un valor en la primera votacion
                    voto = diccionarioVotacion[nombre_participante]["Voto"]
                    voto = voto[0] #Me quedo solo con el numero sin las comillas simples, corchetes y etc
                    print("Voto primera votacion: " + str(voto))
                if (diccionarioVotacion[nombre_participante]["Tarea"] != []):
                    tarea = diccionarioVotacion[nombre_participante]["Tarea"]
                    tarea = tarea[0]
                    print("Tarea: " + str(tarea))
                valor_riesgo = vector_participante["riesgo"]
                valor_optimismo = vector_participante["optimismo"]
                if (valor_riesgo != "" and valor_optimismo != "" and voto != "" and tarea != ""):
                    message = self.darMotivo(valor_riesgo, valor_optimismo, nombre_participante, voto, tarea)
        dispatcher.utter_message(text=message)
        return[]

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