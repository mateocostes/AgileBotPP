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
from actions.Acciones.actionVotarPP import diccionarioVotacion, lista_votos, vectorParticipante

def motivoHabilidad(nombre_participante) -> string:
    habilidad = (diccionarioVotacion[nombre_participante]["Habilidad"])
    if (habilidad != []):
        habilidad = habilidad[len(diccionarioVotacion[nombre_participante]["Habilidad"])-1]
        print("habilidad: " + habilidad)
        return str(habilidad)
    return ""

def motivoLenguaje(nombre_participante) -> string:
    lenguaje = (diccionarioVotacion[nombre_participante]["Lenguaje"])
    if (lenguaje != []):
        lenguaje = lenguaje[len(diccionarioVotacion[nombre_participante]["Habilidad"])-1]
        print("lenguaje: " + lenguaje)
        return str(lenguaje)
    return ""

def motivoHabLen(motivoHabilidad, motivoLenguaje, voto, valor_riesgo, votos_menores) -> string:
    lista_motivosHabLen = []
    if (voto in votos_menores): #0,0.5,1,2,3,5,8
        if (motivoHabilidad != ""):
            if (motivoLenguaje != ""):
                motivoHabLen_1 = f"tengo habilidad trabajando en {motivoHabilidad} y conocimientos de {motivoLenguaje}"
                motivoHabLen_2 = f"trabaje en {motivoHabilidad} con {motivoLenguaje}"
                motivoHabLen_3 = f"tengo conocimientos sobre {motivoHabilidad} en el lenguaje {motivoLenguaje}"
                motivoHabLen_4 = f"ya he trabajado en {motivoHabilidad} con {motivoLenguaje}"
                motivoHabLen_5 = f"tengo experiencia en {motivoHabilidad} con {motivoLenguaje}"
            else:
                motivoHabLen_1 = f"tengo habilidad trabajando en {motivoHabilidad} sin conocer el lenguaje, pero se que puedo aprenderlo rapido"
                motivoHabLen_2 = f"trabaje en {motivoHabilidad} sin conocer el lenguaje, pero lo voy a aprender rapido"
                motivoHabLen_3 = f"conozco de {motivoHabilidad} aunque no sepa el lenguaje, no creo que tome mucho tiempo"
                motivoHabLen_4 = f"aunque no conozca el lenguaje, se bastante de {motivoHabilidad}"
                motivoHabLen_5 = f"habiendo trabajado en {motivoHabilidad} creo que podemos sobrellevar esta tarea"
        else:
            if (motivoLenguaje != ""):
                motivoHabLen_1 = f"he usado {motivoLenguaje} antes"
                motivoHabLen_2 = f"se programar en {motivoLenguaje}"
                motivoHabLen_3 = f"domino el lenguaje {motivoLenguaje}"
                motivoHabLen_4 = f"se me da bien el lenguaje {motivoLenguaje}"
                motivoHabLen_5 = f"{motivoLenguaje} es un lenguaje con el que estoy familiarizado"
            else:
                if (valor_riesgo == 4) or (valor_riesgo == 5):
                    motivoHabLen_1 = f"nunca trabaje con ese lenguaje, pero se que lo voy a lograr"
                    motivoHabLen_2 = f"no tengo conocimientos del tema pero voy a aprender rapido"
                    motivoHabLen_3 = f"me parece sencillo aunque no sepa mucho de eso"
                    motivoHabLen_4 = f"el no saber de esta area no me parece un inconveniente para la finalizacion de la tarea"
                    motivoHabLen_5 = f"creo que el tema no es algo que me tome mucho tiempo para aprender"
                else:
                    motivoHabLen_1 = f"nunca he trabajado en esa area"
                    motivoHabLen_2 = f"no tengo conocimientos del tema"
                    motivoHabLen_3 = f"no trabaje con ese lenguaje de programacion"
                    motivoHabLen_4 = f"no estoy familiarizado con esa area"
                    motivoHabLen_5 = f"voy a tener que capacitarme para poder realizarla"
    else:    #13,20,40,100,1000
        if (motivoHabilidad != ""):
            if (motivoLenguaje != ""):
                motivoHabLen_1 = f"tengo habilidad trabajando en {motivoHabilidad} y conocimientos de {motivoLenguaje}"
                motivoHabLen_2 = f"trabaje en {motivoHabilidad} con {motivoLenguaje}"
                motivoHabLen_3 = f"tengo conocimientos sobre {motivoHabilidad} en el lenguaje {motivoLenguaje}"
                motivoHabLen_4 = f"ya he trabajado en {motivoHabilidad} con {motivoLenguaje}"
                motivoHabLen_5 = f"tengo experiencia en {motivoHabilidad} con {motivoLenguaje}"
            else:
                motivoHabLen_1 = f"tengo habilidad trabajando en {motivoHabilidad} pero no conocer el lenguaje me juega en contra"
                motivoHabLen_2 = f"trabaje en {motivoHabilidad}, pero no saber el lenguaje dificulta las cosas"
                motivoHabLen_3 = f"conozco de {motivoHabilidad} pero tengo que aprender el lenguaje"
                motivoHabLen_4 = f"debo destacar que no conozco el lenguaje, aunque se bastante de {motivoHabilidad}, nos puede llevar mas de lo previsto"
                motivoHabLen_5 = f"aun habiendo trabajado en {motivoHabilidad} creo que la falta de conocimiento del lenguaje va a hacer dificil de completar esta tarea"
        else:
            if (motivoLenguaje != ""):
                motivoHabLen_1 = f"he usado {motivoLenguaje} antes pero al "
                motivoHabLen_2 = f"se programar en {motivoLenguaje} aunque quiza eso no sea suficiente"
                motivoHabLen_3 = f"domino el lenguaje {motivoLenguaje}, pero esto no trivializa la tarea planteada"
                motivoHabLen_4 = f"se me da bien el lenguaje {motivoLenguaje} pero la tarea es algo complicada"
                motivoHabLen_5 = f"{motivoLenguaje} es un lenguaje con el que estoy familiarizado, pero la tarea sigue pareciendo dificil"
            else:
                if (valor_riesgo == 4) or (valor_riesgo == 5):
                    motivoHabLen_1 = f"el no haber trabajado con lo pedido me hace dudar de que podamos hacerlo, aun si me gusta arriesgarme"
                    motivoHabLen_2 = f"no tengo conocimientos del tema aunque puedo intentar aprender de ser necesario"
                    motivoHabLen_3 = f"no es algo en lo que este familiarizado"
                    motivoHabLen_4 = f"el no saber de este lenguaje puede ser un inconveniente para la finalizacion de la tarea"
                    motivoHabLen_5 = f"creo que me va a llevar algo de tiempo para aprender"
                else:
                    motivoHabLen_1 = f"nunca he trabajado en esa area pero presiento que puede llevarnos mas de lo previsto"
                    motivoHabLen_2 = f"no tengo conocimientos del tema pero me parece un poco complejo"
                    motivoHabLen_3 = f"no trabaje con ese lenguaje de programacion y me podria llevar bastante tiempo aprenderlo"
                    motivoHabLen_4 = f"no estoy familiarizado con esa area y debo investigar sobre el tema"
                    motivoHabLen_5 = f"voy a tener que capacitarme para poder realizarla y eso me lleva tiempo"
    lista_motivosHabLen.append(motivoHabLen_1)
    lista_motivosHabLen.append(motivoHabLen_2)
    lista_motivosHabLen.append(motivoHabLen_3)
    lista_motivosHabLen.append(motivoHabLen_4)
    lista_motivosHabLen.append(motivoHabLen_5)
    return random.choice(lista_motivosHabLen)
            
def darMotivo(valor_riesgo, valor_optimismo, nombre_partipante, voto, tarea) -> string:
    motivoHabilidad = motivoHabilidad(nombre_partipante)
    motivoLenguaje = motivoLenguaje(nombre_partipante)
    votos_menores = lista_votos[0:7]
    motivoHabLen = motivoHabLen(motivoHabilidad, motivoLenguaje, voto, valor_riesgo, votos_menores)
    lista_motivos = []
    if (voto in votos_menores): #0,0.5,1,2,3,5,8
        if (valor_riesgo == 4) or (valor_riesgo == 5):
            if (valor_optimismo == 4) or (valor_optimismo == 5):
                motivo_1 = f"Me considero una persona muy arriesgada y optimista, y {motivoHabLen}. Por eso decidi votar {voto} en la tarea "
                motivo_2 = f"Decidi votar {voto}, ya que soy optimista, me gusta arriesgarme, y {motivoHabLen}"
                motivo_3 = f"Al ser alguien optimista y que le gusta tomar riesgos, y teniendo en cuenta que {motivoHabLen}, he decidido votar {voto}"
                motivo_4 = f"Mi estimación es {voto} ya que {motivoHabLen}, además de estar dispuesto a arriesgarme y ser optimista con el tiempo que nos tomara llevar a cabo la tarea"
                motivo_5 = f"{motivoHabLen}. Teniendo en cuenta esto y mi actitud arriesgada y optimista, vote {voto}"
            elif (valor_optimismo == 2) or (valor_optimismo == 3):
                motivo_1 = f"Al ser una persona muy arriesgada, {motivoHabLen}. Por eso, mi eleccion fue votar {voto} en la tarea"
                motivo_2 = f"Decidi votar {voto} ya que soy arriesgado {motivoHabLen}"
                motivo_3 = f"Quizá porque suelo arriesgarme al estimar, suena sencillo, y {motivoHabLen}. Por eso decidi votar {voto} en la tarea {tarea}"
                motivo_4 = f"Siento que debo arriesgarme y votar {voto} en esta tarea, ya que {motivoHabLen}"
                motivo_5 = f"Puede que me esté arriesgando mucho, pero decidi estimar {voto} en esta tarea debido a que {motivoHabLen}"
            elif (valor_optimismo == 0) or (valor_optimismo == 1):
                motivo_1 = f"Aunque suela ser mas pesimista estimando, en este caso decidi arriesgarme y votar {voto}, ya que {motivoHabLen}"
                motivo_2 = f"Vote {voto} ya que {motivoHabLen}. Esta vez, mi lado arriesgado ha influenciado mi estimacion"
                motivo_3 = f"Siendo alguien arriesgado, aunque pesimista, me parecio apropiado votar {voto}. La razon de esto es que {motivoHabLen}"
                motivo_4 = f"Lo primero que hice fue tener en cuenta que {motivoHabLen} En funcion a esto, quise mostrarme dispuesto a arriesgarme y votar {voto}"
                motivo_5 = f"{tarea} suena al tipo de tarea donde puedo intentar arriesgarme. Eso me llevo a votar {voto}porque {motivoHabLen}"
        elif (valor_riesgo == 2) or (valor_riesgo == 3):
            if (valor_optimismo == 4) or (valor_optimismo == 5):
                motivo_1 = f"Me considero una persona muy optimista a la hora de resolver problemas, {motivoHabLen}. Por lo tanto, decidi votar {voto} en la tarea {tarea}"
                motivo_2 = f"Decidi votar {voto} ya que soy bastante optimista {motivoHabLen} en la tarea {tarea}"
                motivo_3 = f"{motivoHabLen} y siendo una persona optimista, creo que estimar {voto} en la tarea es razonable"
                motivo_4 = f"Tengo fe en que nuestro equipo puede lidiar con esta tarea, por lo que decidí votar {voto}. {motivoHabLen}"
                motivo_5 = f"Considerando la tarea, nuestras capacidades, y también que {motivoHabLen}, mi estimacion en esta primera votacion es {voto}"
            elif (valor_optimismo == 2) or (valor_optimismo == 3):
                motivo_1 = f"{motivoHabLen}, por lo que vote {voto}"
                motivo_2 = f"No estoy seguro de si fue adecuado, pero dado que {motivoHabLen}, decidi votar {voto}"
                motivo_3 = f"Como {motivoHabLen}, en la primera votacion vote {voto}"
                motivo_4 = f"No tengo ni tendencia ni aversión al riesgo, por lo que considerando que {motivoHabLen} vote {voto}"
                motivo_5 = f"Trato de no tener un sesgo ni muy optimista ni muy negativo a la hora de estimar. Teniendo en cuenta esto, y como {motivoHabLen}, vote {voto}"
            elif (valor_optimismo == 0) or (valor_optimismo == 1):
                motivo_1 = f"Pese a que usualmente estimo bajo, esta vez decidi votar{voto} debido a que {motivoHabLen}"
                motivo_2 = f"No suelo estimar tan bajo, pero como {motivoHabLen} vote {voto}"
                motivo_3 = f"En esta primera votacion, y al contrario de otras de mis estimaciones, me parecio adecuado votar {voto} ya que {motivoHabLen}"
                motivo_4 = f"No suelo estar muy confiado en mi capacidad de resolver problemas. Sin embargo, debido a que {motivoHabLen}, he votado {voto}"
                motivo_5 = f"Creo que la tarea amerita una estimacion mas baja a las que suelo realizar, ya que {motivoHabLen}. Por lo tanto, he decidido que mi primer para la tarea sea de {voto}"
        elif (valor_riesgo == 0) or (valor_riesgo == 1):
            if (valor_optimismo == 4) or (valor_optimismo == 5):
                motivo_1 = f"Vote {voto} porque {motivoHabLen}. Creo en que nuestro equipo puede lograr esta tarea en poco tiempo y sin arriesgarse"
                motivo_2 = f"A veces evito estimar bajo porque no me gusta arriesgarme; pero en este caso vote {voto} ya que {motivoHabLen}. Creo que somos capaces de realizarla en poco tiempo"
                motivo_3 = f"Al ser una persona optimista y {motivoHabLen}, vote {voto} a pesar de ser alguien que no le gusta arriesgarse"
                motivo_4 = f"Teniendo en cuenta que {motivoHabLen}, y a pesar que no me guste arriesgarme, vote {voto}. Me parece que vamos a poder llevar a cabo la tarea en ese tiempo."
                motivo_5 = f"Creo que {voto} es una estimación adecuada para la tarea, ya que {motivoHabLen}. No me gusta arriesgarme estimando bajo, pero en esta votacion intente ser optimista respecto al tiempo que nos llevaria."
            elif (valor_optimismo == 2) or (valor_optimismo == 3):
                motivo_1 = f"No me gusta arriesgarme, pero vote {voto} porque {motivoHabLen}"
                motivo_2 = f"{motivoHabLen} por lo que vote {voto} pese a mi aversion al riesgo"
                motivo_3 = f"Me parecio correcto estimar {voto}. No senti que fuera un riesgo, ya que {motivoHabLen}"
                motivo_4 = f"Como {motivoHabLen}, no me parecio arriesgado votar {voto}"
                motivo_5 = f"He votado {voto} ya que {motivoHabLen}. Creo que podemos llevar a cabo esta tarea"
            elif (valor_optimismo == 0) or (valor_optimismo == 1):    
                motivo_1 = f"Evidentemente, es una tarea sencilla y estime {voto}, ya que {motivoHabLen}"
                motivo_2 = f"Suelo estimar muy alto, pero como {motivoHabLen} decidí votar {voto}"
                motivo_3 = f"En función de que {motivoHabLen}, creo que puedo votar un poco mas bajo de lo que estoy habituado, por lo que vote {voto}"
                motivo_4 = f"Soy alguien pesimista y con una aversion al riesgo. Al contrastar esto con {motivoHabLen}, decidí votar {voto}"
                motivo_5 = f"Pese a que usualmente estimo bajo, esta vez decidí votar {voto} debido a que {motivoHabLen}"
    else:    #13,20,40,100,1000
        if (valor_riesgo == 4) or (valor_riesgo == 5):
            if (valor_optimismo == 4) or (valor_optimismo == 5):
                motivo_1 = f"Me considero una persona muy arriesgada y optimista, pero {motivoHabLen}. Por eso decidi votar {voto} en la tarea"
                motivo_2 = f"Decidi votar {voto}. Incluso si soy optimista y me gusta arriesgarme, hay que tener en cuenta que {motivoHabLen}"
                motivo_3 = f"Soy alguien optimista y que le gusta tomar riesgos, pero teniendo en cuenta que {motivoHabLen}, he decidido votar {voto}"
                motivo_4 = f"Mi estimación es {voto} ya que {motivoHabLen}, tome en consideracion mi disposicion a arriesgarme y mi optimismo respecto al tiempo que nos tomara llevar a cabo la tarea"
                motivo_5 = f"{motivoHabLen} . Teniendo en cuenta esto, e incluso con mi actitud arriesgada y optimista, no quise votar mas bajo que {voto}"
            elif (valor_optimismo == 2) or (valor_optimismo == 3):
                motivo_1 = f"Incluso siendo una persona muy arriesgada, {motivoHabLen}. Por eso, mi eleccion fue votar {voto} en la tarea"
                motivo_2 = f"Decidi votar {voto} ya que soy arriesgado pero {motivoHabLen}"
                motivo_3 = f"Aunque suelo arriesgarme al estimar, no me parece una tarea trivial, y {motivoHabLen}. Por eso decidi votar {voto}"
                motivo_4 = f"Aunque una parte de mi le gustaria arriesgarse mas y votar mas bajo que {voto} en esta tarea, no puedo dejar pasar que {motivoHabLen}"
                motivo_5 = f"Pese a mi tendencia a arriesgarme en mis estimaciones, me parecio que estimar {voto} en esta tarea es adecuado debido a que {motivoHabLen}"
            elif (valor_optimismo == 0) or (valor_optimismo == 1):
                motivo_1 = f"Aunque muchas veces me arriesgo mas estimando, en este caso no pude evitar ser pesimista y votar {voto}, ya que {motivoHabLen}"
                motivo_2 = f"Vote {voto} ya que {motivoHabLen}. Esta vez, mi lado pesimista ha influenciado mi estimacion"
                motivo_3 = f"Siendo alguien pesimista, aunque arriesgado, me parecio apropiado votar {voto}. La razon de esto es que {motivoHabLen}"
                motivo_4 = f"Lo primero que hice fue tener en cuenta que {motivoHabLen}. En funcion a esto, no considere trivial la tarea, por lo que vote {voto}"
                motivo_5 = f"{tarea} suena al tipo de tarea que va a llevar muchisimo tiempo. Eso me llevo a no arriesgarme tanto como otras veces, votando {voto} porque {motivoHabLen}"
        elif (valor_riesgo == 2) or (valor_riesgo == 3):
            if (valor_optimismo == 4) or (valor_optimismo == 5):
                motivo_1 = f"Aunque me considero persona muy optimista a la hora de resolver problemas, {motivoHabLen}. Por lo tanto, decidi votar {voto} en la tarea {tarea}"
                motivo_2 = f"Decidi votar {voto} aunque yo sea bastante optimista ya que {motivoHabLen}"
                motivo_3 = f"{motivoHabLen}, e incluso siendo una persona optimista, creo que estimar {voto} en la tarea es razonable"
                motivo_4 = f"Mas alla de que tengo fe en nuestro equipo, decidí votar {voto} porque {motivoHabLen}"
                motivo_5 = f"Considerando la tarea, nuestras capacidades, y también que {motivoHabLen}, tristemente no creo poder estimar mas bajo que {voto}"
            elif (valor_optimismo == 2) or (valor_optimismo == 3):
                motivo_1 = f"{motivoHabLen}, por lo que vote {voto}"
                motivo_2 = f"No estoy seguro de si fue adecuado, pero dado que {motivoHabLen}, decidi votar {voto}"
                motivo_3 = f"Como {motivoHabLen}, en la primera votacion vote {voto}"
                motivo_4 = f"No tengo ni tendencia ni aversión al riesgo, por lo que considerando que {motivoHabLen} vote {voto}"
                motivo_5 = f"Trato de no tener un sesgo ni muy optimista ni muy negativo a la hora de estimar. Teniendo en cuenta esto, y como {motivoHabLen}, vote {voto}"
            elif (valor_optimismo == 0) or (valor_optimismo == 1):
                motivo_1 = f"Suelo estimar bajo, y esta vez decidi votar {voto} debido a que {motivoHabLen}"
                motivo_2 = f"Como {motivoHabLen} y siendo alguien que de por si estima alto, vote {voto}"
                motivo_3 = f"En esta primera votacion, me parecio evidente que tenia que votar {voto} ya que {motivoHabLen}"
                motivo_4 = f"No suelo estar muy confiado en mi capacidad de resolver problemas. Si a eso sumamos que {motivoHabLen}, no me queda otra que votar {voto}"
                motivo_5 = f"Creo que la tarea amerita una estimacion mas baja a las que suelo realizar, ya que {motivoHabLen}. Por lo tanto, he decidido que mi primer voto para la tarea sea de {voto}"
        elif (valor_riesgo == 0) or (valor_riesgo == 1):
            if (valor_optimismo == 4) or (valor_optimismo == 5):
                motivo_1 = f"Vote {voto} porque {motivoHabLen}. Quiza visto de otro modo podamos encararlo sin arriesgarse"
                motivo_2 = f"Quiero evito estimar bajo porque no me gusta arriesgarme; en este caso vote {voto} ya que {motivoHabLen}. Creo que hay que pensar bien como podria llevarse a cabo"
                motivo_3 = f"Aunque sea una persona optimista, no me gusta arriesgarme y {motivoHabLen}, por lo que vote {voto}"
                motivo_4 = f"Teniendo en cuenta que {motivoHabLen} y que no me gusta arriesgarme, vote{voto}. Espero que podamos hacer la tarea con un tiempo mejor que ese"
                motivo_5 = f"Tristemente, creo que {voto} es una estimación adecuada para la tarea, ya que {motivoHabLen}. Aunque sea alguien optimista, no me gusta arriesgarme estimando bajo."
            elif (valor_optimismo == 2) or (valor_optimismo == 3):
                motivo_1 = f"No me gusta arriesgarme, por lo que vote {voto} porque {motivoHabLen}"
                motivo_2 = f"{motivoHabLen} y siendo averso al riesgo vote {voto}"
                motivo_3 = f"Me parecio correcto estimar {voto}. No queria arriesgarme, ya que {motivoHabLen}"
                motivo_4 = f"Como {motivoHabLen}, me parecio muy arriesgado votar menos que {voto}"
                motivo_5 = f"He votado {voto} ya que {motivoHabLen}. Quizas alguien mas arriesgado hubiera estimado algo mas bajo"
            elif (valor_optimismo == 0) or (valor_optimismo == 1):    
                motivo_1 = f"He estimado {voto} porque {motivoHabLen}. Quizas mi pesimismo influencio mi decision"
                motivo_2 = f"Suelo estimar muy alto, y como {motivoHabLen} decidí votar {voto}"
                motivo_3 = f"En función de que {motivoHabLen}, creo que esta justificado estimar alto como estoy habituado, por lo que vote {voto}"
                motivo_4 = f"Soy alguien pesimista y con una aversion al riesgo. Considerando junto a ello {motivoHabLen}, llegue a una estimacion inicial de {voto}"
                motivo_5 = f"Suelo ser muy pesimista estimando, y como {motivoHabLen}, esta vez no sera la excepcion. En consecuencia, vote {voto}"
    lista_motivos.append(motivo_1)
    lista_motivos.append(motivo_2)
    lista_motivos.append(motivo_3)
    lista_motivos.append(motivo_4)
    lista_motivos.append(motivo_5)
    return random.choice(lista_motivos)

class ActionOpinionPrimeraVot(Action):
    def name(self) -> Text:
        return "action_motivo_primeravot"
        
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nombre_participante = str(tracker.get_slot("participante"))
        message = "Vote eso ya que no sabia que votar" #default
        voto = 8 #default
        tarea = ""
        if (nombre_participante != None):
            vector_participante = vectorParticipante(nombre_participante)
            if(vector_participante != None):
                if (diccionarioVotacion[nombre_participante]["Voto"] != []): #Consulto si tiene un valor en la primera votacion
                    voto = diccionarioVotacion[nombre_participante]["Voto"][len(diccionarioVotacion[nombre_participante]["Voto"])-1]
                    print("Voto primera votacion: " + str(voto))
                if (diccionarioVotacion[nombre_participante]["Tarea"] != []):
                    tarea = diccionarioVotacion[nombre_participante]["Tarea"][len(diccionarioVotacion[nombre_participante]["Tarea"])-1]
                    print("Tarea: " + str(tarea))
                valor_riesgo = vector_participante["riesgo"]
                valor_optimismo = vector_participante["optimismo"]
                if (valor_riesgo != "" and valor_optimismo != "" and voto != "" and tarea != ""):
                    message = darMotivo(valor_riesgo, valor_optimismo, nombre_participante, voto, tarea)
        dispatcher.utter_message(text=message)
        return[]