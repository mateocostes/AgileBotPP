# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
    
#Importo las acciones de los demas archivos .py
from actions.Acciones.actionReconocer import ActionReconocerParticipante, ActionReconocerTarea  
from actions.Acciones.actionVotarPP import ActionVotarPrimeraVot, ActionVotarSegundaVot
from actions.Acciones.actionMotivoPP import ActionOpinionPrimeraVot
from actions.Acciones.actionVotar3P import ActionEstimacion3Puntos
from actions.Acciones.actionMovito3P import ActionMotivoEstimacion3Puntos
from actions.Acciones.actionArchivo import ActionFinalizarCeremonia   
from rasa_sdk import Action

def main():
    ActionReconocerTarea()
    ActionReconocerParticipante()
    ActionVotarPrimeraVot()
    ActionOpinionPrimeraVot()
    ActionVotarSegundaVot()
    ActionEstimacion3Puntos()
    ActionMotivoEstimacion3Puntos()
    ActionFinalizarCeremonia()
    