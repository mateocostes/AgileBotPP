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
from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')
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
        
api_endpoint_set_vector = "http://IP/dispatcher/set-vector"
api_endpoint_get_vector = "http://IP/dispatcher/get-vector"
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
        print("Nombre del participante: " + str(nombre_participante))
        print("Tarea actual: " + str(tarea))
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

    def motivoHabLen(self, motivoHabilidad, motivoLenguaje, voto, valor_riesgo, votos_menores) -> string:
        lista_motivosHabLen = []
        if (voto in votos_menores): #0,0.5,1,2,3,5,8
            if (motivoHabilidad != ""):
                if (motivoLenguaje != ""):
                    motivoHabLen_1 = "tengo habilidad trabajando en " + motivoHabilidad + " y conocimientos de " + motivoLenguaje
                    motivoHabLen_2 = "trabaje en " + motivoHabilidad + " con " + motivoLenguaje
                    motivoHabLen_3 = "tengo conocimientos sobre " + motivoHabilidad + "en el lenguaje " + motivoLenguaje
                    motivoHabLen_4 = "ya he trabajado en " + motivoHabilidad + " con " + motivoLenguaje
                    motivoHabLen_5 = "tengo experiencia en " + motivoHabilidad + " con " + motivoLenguaje
                else:
                    motivoHabLen_1 = "tengo habilidad trabajando en " + motivoHabilidad + " sin conocer el lenguaje, pero se que puedo aprenderlo rapido"
                    motivoHabLen_2 = "trabaje en " + motivoHabilidad + " sin conocer el lenguaje, pero lo voy a aprender rapido"
                    motivoHabLen_3 = "conozco de " + motivoHabilidad + " aunque no sepa el lenguaje, no creo que tome mucho tiempo"
                    motivoHabLen_4 = "aunque no conozca el lenguaje, se bastante de " + motivoHabilidad
                    motivoHabLen_5 = "habiendo trabajado en " + motivoHabilidad + " creo que podemos sobrellevar esta tarea"
            else:
                if (motivoLenguaje != ""):
                    motivoHabLen_1 = "he usado " + motivoLenguaje + "antes"
                    motivoHabLen_2 = "se programar en " + motivoLenguaje
                    motivoHabLen_3 = "domino el lenguaje " + motivoLenguaje
                    motivoHabLen_4 = "se me da bien el lenguaje " + motivoLenguaje
                    motivoHabLen_5 = motivoLenguaje + " es un lenguaje con el que estoy familiarizado"
                else:
                    if (valor_riesgo == 4) or (valor_riesgo == 5):
                        motivoHabLen_1 = "nunca trabaje con ese lenguaje, pero se que lo voy a lograr"
                        motivoHabLen_2 = "no tengo conocimientos del tema pero voy a aprender rapido"
                        motivoHabLen_3 = "me parece sencillo aunque no sepa mucho de eso"
                        motivoHabLen_4 = "el no saber de esta area no me parece un inconveniente para la finalizacion de la tarea"
                        motivoHabLen_5 = "creo que el tema no es algo que me tome mucho tiempo para aprender"
                    else:
                        motivoHabLen_1 = "nunca he trabajado en esa area"
                        motivoHabLen_2 = "no tengo conocimientos del tema"
                        motivoHabLen_3 = "no trabaje con ese lenguaje de programacion"
                        motivoHabLen_4 = "no estoy familiarizado con esa area"
                        motivoHabLen_5 = "voy a tener que capacitarme para poder realizarla"
        else:    #13,20,40,100,1000
            if (motivoHabilidad != ""):
                if (motivoLenguaje != ""):
                    motivoHabLen_1 = "tengo habilidad trabajando en " + motivoHabilidad + " y conocimientos de " + motivoLenguaje
                    motivoHabLen_2 = "trabaje en " + motivoHabilidad + " con " + motivoLenguaje
                    motivoHabLen_3 = "tengo conocimientos sobre " + motivoHabilidad + "en el lenguaje " + motivoLenguaje
                    motivoHabLen_4 = "ya he trabajado en " + motivoHabilidad + " con " + motivoLenguaje
                    motivoHabLen_5 = "tengo experiencia en " + motivoHabilidad + " con " + motivoLenguaje
                else:
                    motivoHabLen_1 = "tengo habilidad trabajando en " + motivoHabilidad + "pero no conocer el lenguaje me juega en contra"
                    motivoHabLen_2 = "trabaje en " + motivoHabilidad + ", pero no saber el lenguaje dificulta las cosas"
                    motivoHabLen_3 = "conozco de " + motivoHabilidad + " pero tengo que aprender el lenguaje"
                    motivoHabLen_4 = "debo destacar que no conozco el lenguaje, aunque se bastante de " + motivoHabilidad
                    motivoHabLen_5 = "aun habiendo trabajado en " + motivoHabilidad + " creo que la falta de conocimiento del lenguaje va a hacer dificil de completar esta tarea"
            else:
                if (motivoLenguaje != ""):
                    motivoHabLen_1 = "he usado " + motivoLenguaje + "antes"
                    motivoHabLen_2 = "se programar en " + motivoLenguaje + "aunque quiza eso no sea suficiente"
                    motivoHabLen_3 = "domino el lenguaje " + motivoLenguaje + ", pero esto no trivializa la tarea planteada"
                    motivoHabLen_4 = "se me da bien el lenguaje " + motivoLenguaje + " pero la tarea es algo complicada"
                    motivoHabLen_5 = motivoLenguaje + " es un lenguaje con el que estoy familiarizado, pero la tarea sigue pareciendo dificil"
                else:
                    if (valor_riesgo == 4) or (valor_riesgo == 5):
                        motivoHabLen_1 = "el no haber trabajado con lo pedido me hace dudar de que podamos hacerlo, aun si me gusta arriesgarme"
                        motivoHabLen_2 = "no tengo conocimientos del tema aunque puedo intentar aprender de ser necesario"
                        motivoHabLen_3 = "no es algo en lo que este familiarizado"
                        motivoHabLen_4 = "el no saber de este lenguaje puede ser un inconveniente para la finalizacion de la tarea"
                        motivoHabLen_5 = "creo que me va a llevar algo de tiempo para aprender"
                    else:
                        motivoHabLen_1 = "nunca he trabajado en esa area"
                        motivoHabLen_2 = "no tengo conocimientos del tema"
                        motivoHabLen_3 = "no trabaje con ese lenguaje de programacion"
                        motivoHabLen_4 = "no estoy familiarizado con esa area"
                        motivoHabLen_5 = "voy a tener que capacitarme para poder realizarla"
        lista_motivosHabLen.append(motivoHabLen_1)
        lista_motivosHabLen.append(motivoHabLen_2)
        lista_motivosHabLen.append(motivoHabLen_3)
        lista_motivosHabLen.append(motivoHabLen_4)
        lista_motivosHabLen.append(motivoHabLen_5)
        return random.choice(lista_motivosHabLen)
              
    def darMotivo(self, valor_riesgo, valor_optimismo, nombre_partipante, voto, tarea) -> string:
        motivoHabilidad = self.motivoHabilidad(nombre_partipante)
        motivoLenguaje = self.motivoLenguaje(nombre_partipante)
        votos_menores = lista_votos[0:7]
        motivoHabLen = self.motivoHabLen(motivoHabilidad, motivoLenguaje, voto, valor_riesgo, votos_menores)
        lista_motivos = []
        print("lista menores: " + str(votos_menores))
        if (voto in votos_menores): #0,0.5,1,2,3,5,8
            if (valor_riesgo == 4) or (valor_riesgo == 5):
                if (valor_optimismo == 4) or (valor_optimismo == 5):
                    motivo_1 = "Me considero una persona muy arriesgada y optimista, y " + motivoHabLen + ". Por eso decidi votar "  + str(voto) + " en la tarea "
                    motivo_2 = "Decidi votar " + str(voto) + ", ya que soy optimista, me gusta arriesgarme, y " + motivoHabLen
                    motivo_3 = "Al ser alguien optimista y que le gusta tomar riesgos, y teniendo en cuenta que " + motivoHabLen + ", he decidido votar "  + str(voto)
                    motivo_4 = "Mi estimación es " + str(voto) + " ya que " + motivoHabLen + ", además de estar dispuesto a arriesgarme y ser optimista con el tiempo que nos tomara llevar a cabo la tarea"
                    motivo_5 = motivoHabLen + ". Teniendo en cuenta esto y mi actitud arriesgada y optimista, vote " + str(voto)
                elif (valor_optimismo == 2) or (valor_optimismo == 3):
                    motivo_1 = "Al ser una persona muy arriesgada, " + motivoHabLen + ". Por eso, mi eleccion fue votar "  + str(voto) + " en la tarea"
                    motivo_2 = "Decidi votar " + str(voto) + " ya que soy arriesgado " + motivoHabLen
                    motivo_3 = tarea + ", quizá porque suelo arriesgarme al estimar, suena sencillo, y " + motivoHabLen + ". Por eso decidi votar "  + str(voto)
                    motivo_4 = "Siento que debo arriesgarme y votar " + str(voto) + "en esta tarea, ya que " + motivoHabLen
                    motivo_5 = "Puede que me esté arriesgando mucho, pero decidi estimar " + str(voto) + "en esta tarea debido a que " + motivoHabLen
                elif (valor_optimismo == 0) or (valor_optimismo == 1):
                    motivo_1 = "Aunque suela ser mas pesimista estimando, en este caso decidi arriesgarme y votar " + str(voto) + ", ya que " + motivoHabLen
                    motivo_2 = "Vote " + str(voto) + " ya que " + motivoHabLen + ". Esta vez, mi lado arriesgado ha influenciado mi estimacion"
                    motivo_3 = "Siendo alguien arriesgado, aunque pesimista, me parecio apropiado votar " + str(voto) + ". La razon de esto es que " + motivoHabLen
                    motivo_4 = "Lo primero que hice fue tener en cuenta que " + motivoHabLen + " En funcion a esto, quise mostrarme dispuesto a arriesgarme y votar " + str(voto)
                    motivo_5 = tarea + "suena al tipo de tarea donde puedo intentar arriesgarme. Eso me llevo a votar " + str(voto) + " porque " + motivoHabLen
            elif (valor_riesgo == 2) or (valor_riesgo == 3):
                if (valor_optimismo == 4) or (valor_optimismo == 5):
                    motivo_1 = "Me considero una persona muy optimista a la hora de resolver problemas, " + motivoHabLen + ". Por lo tanto, decidi votar "  + str(voto) + " en la tarea " + tarea
                    motivo_2 = "Decidi votar " + str(voto) + " ya que soy bastante optimista " + motivoHabLen + " en la tarea " + tarea
                    motivo_3 = motivoHabLen + " y siendo una persona optimista, creo que estimar " + str(voto) + " en la tarea es razonable"
                    motivo_4 = "Tengo fe en que nuestro equipo puede lidiar con esta tarea, por lo que decidí votar " + str(voto) + ". " + motivoHabLen
                    motivo_5 = "Considerando la tarea, nuestras capacidades, y también que " + motivoHabLen + ", mi estimacion en esta primera votacion es " + str(voto)
                elif (valor_optimismo == 2) or (valor_optimismo == 3):
                    motivo_1 = motivoHabLen + ", por lo que vote " + str(voto)
                    motivo_2 = "No estoy seguro de si fue adecuado, pero dado que " + motivoHabLen + ", decidi votar " + str(voto)
                    motivo_3 = "Como " + motivoHabLen + ", en la primera votacion vote " + str(voto)
                    motivo_4 = "No tengo ni tendencia ni aversión al riesgo, por lo que considerando que " + motivoHabLen + " vote " + str(voto)
                    motivo_5 = "Trato de no tener un sesgo ni muy optimista ni muy negativo a la hora de estimar. Teniendo en cuenta esto, y como " + motivoHabLen + ", vote " + str(voto)
                elif (valor_optimismo == 0) or (valor_optimismo == 1):
                    motivo_1 = "Pese a que usualmente soy mala onda estimando, esta vez decidi votar" + str(voto) + " debido a que " + motivoHabLen
                    motivo_2 = "No suelo estimar tan bajo, pero como " + motivoHabLen + "vote " + str(voto)
                    motivo_3 = "En esta primera votacion, y al contrario de otras de mis estimaciones, me parecio adecuado votar " + str(voto) + " ya que " + motivoHabLen
                    motivo_4 = "No suelo estar muy confiado en mi capacidad de resolver problemas. Sin embargo, debido a que " + motivoHabLen + ", he votado " + str(voto)
                    motivo_5 = "Creo que la tarea amerita una estimacion mas baja a las que suelo realizar, ya que " + motivoHabLen + ". Por lo tanto, he decidido que mi primer str(voto) para la tarea " + tarea + " es " + str(voto)
            elif (valor_riesgo == 0) or (valor_riesgo == 1):
                if (valor_optimismo == 4) or (valor_optimismo == 5):
                    motivo_1 = "Vote " + str(voto) + " porque " + motivoHabLen + ". Creo en que nuestro equipo puede lograr esta tarea en poco tiempo y sin arriesgarse"
                    motivo_2 = "A veces evito estimar bajo porque no me gusta arriesgarme; pero en este caso vote " + str(voto) + " ya que " + motivoHabLen + ". Creo que somos capaces de realizarla en poco tiempo"
                    motivo_3 = "Al ser una persona optimista y " + motivoHabLen + ", vote " + str(voto) + "a pesar de ser alguien que no le gusta arriesgarse"
                    motivo_4 = "Teniendo en cuenta que " + motivoHabLen + ", y a pesar que no me guste arriesgarme, vote" + str(voto) + ". Me parece que vamos a poder llevar a cabo la tarea en ese tiempo."
                    motivo_5 = "Creo que " + str(voto) + " es una estimación adecuada para la tarea, ya que " + motivoHabLen + ". No me gusta arriesgarme estimando bajo, pero en esta votacion intente ser optimista respecto al tiempo que nos llevaria."
                elif (valor_optimismo == 2) or (valor_optimismo == 3):
                    motivo_1 = "No me gusta arriesgarme, pero vote " + str(voto) + " porque "+  motivoHabLen
                    motivo_2 = motivoHabLen + ", por lo que vote " + str(voto) + " pese a mi aversion al riesgo"
                    motivo_3 = "Me parecio correcto estimar " + str(voto) + ". No senti que fuera un riesgo, ya que " + motivoHabLen
                    motivo_4 = "Como " + motivoHabLen + ", no me parecio arriesgado votar" + str(voto)
                    motivo_5 = "He votado " + str(voto) + " ya que " + motivoHabLen + ". Creo que podemos llevar a cabo esta tarea"
                elif (valor_optimismo == 0) or (valor_optimismo == 1):    
                    motivo_1 = "Evidentemente, si alguien mala onda como yo estima " + str(voto) + ", es porque la tarea debe ser realizable." + motivoHabLen
                    motivo_2 = "Suelo estimar muy alto, pero como " + motivoHabLen + " decidí votar " + str(voto)
                    motivo_3 = "En función de que " + motivoHabLen + ", creo que puedo votar un poco mas bajo de lo que estoy habituado, por lo que vote " + str(voto)
                    motivo_4 = "Soy alguien pesimista y con una aversion al riesgo. Al contrastar esto con " + motivoHabLen + ", decidí votar " + str(voto)
                    motivo_5 = "Pese a que usualmente soy muy mala onda estimando, esta vez decidí votar " + str(voto) + " debido a que " + motivoHabLen
        else:    #13,20,40,100,1000
            if (valor_riesgo == 4) or (valor_riesgo == 5):
                if (valor_optimismo == 4) or (valor_optimismo == 5):
                    motivo_1 = "Me considero una persona muy arriesgada y optimista, pero " + motivoHabLen + ". Por eso decidi votar "  + str(voto) + " en la tarea "
                    motivo_2 = "Decidi votar " + str(voto) + ". Incluso si soy optimista y me gusta arriesgarme, hay que tener en cuenta que " + motivoHabLen
                    motivo_3 = "Soy alguien optimista y que le gusta tomar riesgos, pero teniendo en cuenta que " + motivoHabLen + ", he decidido votar "  + str(voto)
                    motivo_4 = "Mi estimación es " + str(voto) + " ya que " + motivoHabLen + ", tome en consideracion mi disposicion a arriesgarme y mi optimismo respecto al tiempo que nos tomara llevar a cabo la tarea"
                    motivo_5 = motivoHabLen + ". Teniendo en cuenta esto, e incluso con mi actitud arriesgada y optimista, no quise votar mas bajo que " + str(voto)
                elif (valor_optimismo == 2) or (valor_optimismo == 3):
                    motivo_1 = "Incluso siendo una persona muy arriesgada, " + motivoHabLen + ". Por eso, mi eleccion fue votar "  + str(voto) + " en la tarea"
                    motivo_2 = "Decidi votar " + str(voto) + " ya que soy arriesgado pero " + motivoHabLen
                    motivo_3 = tarea + ", aunque suelo arriesgarme al estimar, no me parece trivial, y " + motivoHabLen + ". Por eso decidi votar "  + str(voto)
                    motivo_4 = "Aunque una parte de mi le gustaria arriesgarse mas y votar mas bajo que " + str(voto) + " en esta tarea, no puedo dejar pasar que " + motivoHabLen
                    motivo_5 = "Pese a mi tendencia a arriesgarme en mis estimaciones, me parecio que estimar " + str(voto) + " en esta tarea es adecuado debido a que " + motivoHabLen
                elif (valor_optimismo == 0) or (valor_optimismo == 1):
                    motivo_1 = "Aunque muchas veces me arriesgo mas estimando, en este caso no pude evitar ser pesimista y votar " + str(voto) + ", ya que " + motivoHabLen
                    motivo_2 = "Vote " + str(voto) + " ya que " + motivoHabLen + ". Esta vez, mi lado pesimista ha influenciado mi estimacion"
                    motivo_3 = "Siendo alguien pesimista, aunque arriesgado, me parecio apropiado votar " + str(voto) + ". La razon de esto es que " + motivoHabLen
                    motivo_4 = "Lo primero que hice fue tener en cuenta que " + motivoHabLen + "En funcion a esto, no considere trivial la tarea, por lo que vote " + str(voto)
                    motivo_5 = tarea + "suena al tipo de tarea que va a llevar muchisimo tiempo. Eso me llevo a no arriesgarme tanto como otras veces, votando " + str(voto) + " porque " + motivoHabLen
            elif (valor_riesgo == 2) or (valor_riesgo == 3):
                if (valor_optimismo == 4) or (valor_optimismo == 5):
                    motivo_1 = "Aunque me considero persona muy optimista a la hora de resolver problemas, " + motivoHabLen + ". Por lo tanto, decidi votar "  + str(voto) + " en la tarea " + tarea
                    motivo_2 = "Decidi votar " + str(voto) + " aunque yo sea bastante optimista ya que " + motivoHabLen
                    motivo_3 = motivoHabLen + " ; y, incluso siendo una persona optimista, creo que estimar" + str(voto) + " en la tarea es razonable"
                    motivo_4 = "Mas alla de que tengo fe en nuestro equipo, decidí votar " + str(voto) + " porque " + motivoHabLen
                    motivo_5 = "Considerando la tarea, nuestras capacidades, y también que " + motivoHabLen + ", tristemente no creo poder estimar mas bajo que " + str(voto)
                elif (valor_optimismo == 2) or (valor_optimismo == 3):
                    motivo_1 = motivoHabLen + ", por lo que vote " + str(voto)
                    motivo_2 = "No estoy seguro de si fue adecuado, pero dado que " + motivoHabLen + ", decidi votar " + str(voto)
                    motivo_3 = "Como " + motivoHabLen + ", en la primera votacion vote " + str(voto)
                    motivo_4 = "No tengo ni tendencia ni aversión al riesgo, por lo que considerando que " + motivoHabLen + " vote " + str(voto)
                    motivo_5 = "Trato de no tener un sesgo ni muy optimista ni muy negativo a la hora de estimar. Teniendo en cuenta esto, y como " + motivoHabLen + ", vote " + str(voto)
                elif (valor_optimismo == 0) or (valor_optimismo == 1):
                    motivo_1 = "Suelo ser mala onda estimando, y esta vez decidi votar " + str(voto) + " debido a que " + motivoHabLen
                    motivo_2 = "Como " + motivoHabLen + " y siendo alguien que de por si estima alto, vote " + str(voto)
                    motivo_3 = "En esta primera votacion, me parecio evidente que tenia que votar " + str(voto) + " ya que " + motivoHabLen
                    motivo_4 = "No suelo estar muy confiado en mi capacidad de resolver problemas. Si a eso sumamos que " + motivoHabLen + ", no me queda otra que votar " + str(voto)
                    motivo_5 = "Creo que la tarea amerita una estimacion mas baja a las que suelo realizar, ya que " + motivoHabLen + ". Por lo tanto, he decidido que mi primer str(voto) para la tarea " + tarea + " es " + str(voto)
            elif (valor_riesgo == 0) or (valor_riesgo == 1):
                if (valor_optimismo == 4) or (valor_optimismo == 5):
                    motivo_1 = "Vote " + str(voto) + " porque " + motivoHabLen + ". Quiza visto de otro modo podamos encararlo sin arriesgarse"
                    motivo_2 = "Quiero evito estimar bajo porque no me gusta arriesgarme; en este caso vote " + str(voto) + " ya que " + motivoHabLen + ". Creo que hay que pensar bien como podria llevarse a cabo"
                    motivo_3 = "Aunque sea una persona optimista, no me gusta arriesgarme y " + motivoHabLen + ", por lo que vote " + str(voto)
                    motivo_4 = "Teniendo en cuenta que " + motivoHabLen + " y que no me gusta arriesgarme, vote" + str(voto) + ". Espero que podamos hacer la tarea con un tiempo mejor que ese"
                    motivo_5 = "Tristemente, creo que " + str(voto) + " es una estimación adecuada para la tarea, ya que " + motivoHabLen + ". Aunque sea alguien optimista, no me gusta arriesgarme estimando bajo."
                elif (valor_optimismo == 2) or (valor_optimismo == 3):
                    motivo_1 = "No me gusta arriesgarme, por lo que vote " + str(voto) + " porque "+  motivoHabLen
                    motivo_2 = motivoHabLen + ", y siendo averso al riesgo vote " + str(voto)
                    motivo_3 = "Me parecio correcto estimar " + str(voto) + ". No queria arriesgarme, ya que " + motivoHabLen
                    motivo_4 = "Como " + motivoHabLen + ", me parecio muy arriesgado votar menos que " + str(voto)
                    motivo_5 = "He votado " + str(voto) + " ya que " + motivoHabLen + ". Quizas alguien mas arriesgado hubiera estimado algo mas bajo"
                elif (valor_optimismo == 0) or (valor_optimismo == 1):    
                    motivo_1 = "He estimado " + str(voto) + " porque " + motivoHabLen + ". Quizas mi mala onda influencio mi decision"
                    motivo_2 = "Suelo estimar muy alto, y como " + motivoHabLen + " decidí votar " + str(voto)
                    motivo_3 = "En función de que " + motivoHabLen + ", creo que esta justificado estimar alto como estoy habituado, por lo que vote " + str(voto)
                    motivo_4 = "Soy alguien pesimista y con una aversion al riesgo. Considerando junto a ello " + motivoHabLen + ", llegue a una estimacion inicial de " + str(voto)
                    motivo_5 = "Suelo ser muy mala onda estimando, y como " + motivoHabLen + ", esta vez no sera la excepcion. En consecuencia, vote " + str(voto)
        lista_motivos.append(motivo_1)
        lista_motivos.append(motivo_2)
        lista_motivos.append(motivo_3)
        lista_motivos.append(motivo_4)
        lista_motivos.append(motivo_5)
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
                    voto = diccionarioVotacion[nombre_participante]["Voto"][len(diccionarioVotacion[nombre_participante]["Voto"])-1]
                    #voto = voto[0] #Me quedo solo con el numero sin las comillas simples, corchetes y etc
                    print("Voto primera votacion: " + str(voto))
                if (diccionarioVotacion[nombre_participante]["Tarea"] != []):
                    tarea = diccionarioVotacion[nombre_participante]["Tarea"][len(diccionarioVotacion[nombre_participante]["Tarea"])-1]
                    #tarea = tarea[0]
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