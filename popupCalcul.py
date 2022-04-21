# -*- coding: utf-8 -*-
import PySimpleGUI as sg


# Simple fenêtre empêchant les actions lors du calcul
def createPopupCalcul():

    _VARS = {'window': False,}
    sg.theme("SystemDefault1")

    ####################################################################################################################################
    ###LAYOUT
    ####################################################################################################################################

    #Layout de la fenêtre
    layout = [[sg.Text("Calcul en cours")]]

    #Création de la fenêtre, sans barre titre et bloquant les actions
    _VARS['window'] = sg.Window('Calcul',
                                layout,
                                finalize=True,
                                resizable=False,element_justification="center", 
                                no_titlebar=True, modal=True)

    #Renvoi de la fenêtre pour pouvoir la fermer dans le programme principal
    return  _VARS['window']