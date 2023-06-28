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
from actions.Acciones.actionVotarPP import votarPrimeraVotacionPP
from actions.Acciones.actionArchivo import vectorParticipante, writeArchivo, diccionarioVotacion, direcVotacion
from actions.Acciones.actionReconocer import ActionReconocerTarea

class ActionEstimacion3Puntos(Action):
    def name(self) -> Text:
        return "action_estimacion_3_puntos"
    
    def aproximarVotoEstimacion3Puntos(self, valor, lista_votos):
        voto_aproximado = min(lista_votos, key=lambda v: abs(v - valor)) #La función lambda calcula la distancia absoluta entre cada voto v y valor, y min() encuentra el voto con la distancia mínima.
        return voto_aproximado
    
    def calcularVotosEstimacion3Puntos(self, voto, porc_opt, porc_rea, porc_pes):
        lista_votos = [0, 0.5, 1, 2, 3, 5, 8, 20, 40, 100, 1000] #No puedo usar la definida al principio porque es de strings.
        voto_optimista = self.aproximarVotoEstimacion3Puntos(voto * porc_opt, lista_votos)
        voto_realista = self.aproximarVotoEstimacion3Puntos(voto * porc_rea, lista_votos[lista_votos.index(voto_optimista)+1 : ]) #utilizo los elementos del voto optimista en adelante para que no se repitan
        voto_pesimista = self.aproximarVotoEstimacion3Puntos(voto * porc_pes, lista_votos[lista_votos.index(voto_realista)+1 : ]) #utilizo los elementos del voto optimista en adelante para que no se repitan
        return voto_optimista, voto_realista, voto_pesimista

    def votarEstimacion3Puntos(self, valor_optimismo, voto):
        voto_optimista = 0
        voto_realista = 0
        voto_pesimista = 0
        if (valor_optimismo == 0):
            voto_optimista, voto_realista, voto_pesimista = self.calcularVotosEstimacion3Puntos(voto, 0.2, 0.6, 1)
        elif (valor_optimismo == 1):
            voto_optimista, voto_realista, voto_pesimista = self.calcularVotosEstimacion3Puntos(voto, 0.2, 0.4, 0.8)
        elif (valor_optimismo == 2):
            voto_optimista, voto_realista, voto_pesimista = self.calcularVotosEstimacion3Puntos(voto, 0.4, 1.2, 1.6)
        elif (valor_optimismo == 3):
            voto_optimista, voto_realista, voto_pesimista = self.calcularVotosEstimacion3Puntos(voto, 0.6, 1, 1.4)
        elif (valor_optimismo == 4):
            voto_optimista, voto_realista, voto_pesimista = self.calcularVotosEstimacion3Puntos(voto, 0.8, 1.2, 1.4)
        elif (valor_optimismo == 5):
            voto_optimista, voto_realista, voto_pesimista = self.calcularVotosEstimacion3Puntos(voto, 1, 1.6, 2)
        return (voto_optimista, voto_realista, voto_pesimista)

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #nombre_participante = str(tracker.get_slot("participante"))
        nombre_participante = str(tracker.sender_id)
        #tarea = str(tracker.get_slot("tarea"))
        tarea = ActionReconocerTarea.tarea_actual
        voto = votarPrimeraVotacionPP(nombre_participante, tarea) #Utilizo la logica de la votacion del PP
        print("voto: " + str(voto))
        votos = (5,8,13) #Votos default. El primer voto es optimista, luego realistas y por ultimo pesimista
        message = str(votos)
        #Si vectorParticipante(nombre_participante) != None quiere decir que existe el participante
        if (nombre_participante != None and tarea != None):
            vector_participante = vectorParticipante(nombre_participante)
            if (vector_participante != None):
                valor_optimismo = vector_participante["optimismo"]
                #LOGICA 3 VOTOS
                votos = self.votarEstimacion3Puntos(valor_optimismo, int(voto))
                print("votos: " + str(votos))
                #FIN LOGICA 3 VOTOS
                message = str(votos)
                (diccionarioVotacion[nombre_participante]["Voto3puntos"]).append(votos) #Agrego a un json el voto
                (diccionarioVotacion[nombre_participante]["Tarea"]).append(tarea) #Agrego a un json la tarea
                writeArchivo(direcVotacion,diccionarioVotacion)
        dispatcher.utter_message(text=message)
        return []