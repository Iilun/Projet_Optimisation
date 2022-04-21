# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

#Crée la fenêtre de comparaison des résultats   
def createComparisonWindow(results,comparison_results_puissances, comparison_results_debits, previous_window):
    #Fermeture de la fenêtre précédente
    previous_window.close()
    
    #Variables globales
    _VARS = {'window': False,
             'fig_agg': False,
             'pltFig': False,
             'hasSelected': False}

    
    SYMBOL_UP =    '▲'
    SYMBOL_DOWN =  '▼'
    tableOpened = False
    min_colum_width = 4
    numberOfRows = len(results[2]) if  isinstance(results[2] , list) else 1
    
    sg.theme("SystemDefault1")
    
    buttonList = [ "-PUISSANCETOTALEBUTTON-", "-NBTURBINESBUTTON-"]
    
    ####################################################################################################################################
    ###TRAITEMENT DES DONNEES
    ####################################################################################################################################
    debits_simules = results[0]
    puissances_totales_simules = results[2]
    
    debit_reels = pd.DataFrame(comparison_results_debits)
    puissances_totales_reels = pd.DataFrame(comparison_results_puissances).sum(axis=1).values.tolist()
    
    puissances = [puissances_totales_simules, puissances_totales_reels]
    
    
    debits_simules = pd.DataFrame(debits_simules)
    
    #Calcul du nombre de turbines
    nb_turbines_simules = (debits_simules.iloc[:,1:]!=0).sum(axis=1).values.tolist()
    nb_turbines_reels = (debit_reels.iloc[:,:]!=0).sum(axis=1).values.tolist()
    
    nb_turbines = [nb_turbines_simules, nb_turbines_reels]
    ####################################################################################################################################
    ###FIGURE FUNCTIONS
    ####################################################################################################################################
    
    #Fonction tracant la figure sur le canvas
    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg
    
    #Fonction récupérant les données à tracer
    def extractResults(results, event):
        
        numberOfLines = len(puissances_totales_simules)
        if (event == "-PUISSANCETOTALEBUTTON-") :
            yData = puissances
        elif (event == "-NBTURBINESBUTTON-") :
            yData = nb_turbines
        xData = np.linspace(1, numberOfLines, num =numberOfLines,  dtype=int).tolist()
        return [yData, xData]
    
    #Fonction tracant  la première figure
    def drawChart():
        _VARS['pltFig'] = plt.figure()
        plt.title("Sélectionnez une comparaison")
        plt.axis('off')
        _VARS['fig_agg'] = draw_figure(
            _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])
    
    #Fonction permettant de changer le tracé sur le canvas en fonction de l'evenement demandé
    def updateChart(event):
        _VARS['window']['figCanvas'].set_tooltip(None)
        _VARS['fig_agg'].get_tk_widget().forget()
        #Récupération des résultats
        [[dataY_simul, dataY_reel], dataX] = extractResults(results, event)
        plt.clf()
        #Gestion du titre
        if (event == "-PUISSANCETOTALEBUTTON-") :
            title = "Comparaison de la puissance totale (MW)"
            typeofDash = ""
        elif (event == "-NBTURBINESBUTTON-") :
            title = "Comparaison du nombre de turbines"
            typeofDash = "."
        
        plt.title(title)
        #Tracé des valeurs simulées
        plt.plot(dataX, dataY_simul, 'b', label="Simulé")
        #Tracé des valeurs réelles
        plt.plot(dataX, dataY_reel, 'g'+typeofDash, label="Réel")
        plt.legend()
        _VARS['fig_agg'] = draw_figure(
            _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])
        #Renvoi des données pour affichage dans tableau
        return [[dataY_simul, dataY_reel], dataX]
    
    ####################################################################################################################################
    ###EVENT FUNCTIONS
    ####################################################################################################################################
    
    #Fonction permettant de maintenir un et un seul bouton enfoncé
    def pressSelectedButton(event):
        for key in buttonList:
            _VARS['window'][key].Widget.config(relief="raised")
        _VARS['window'][event].Widget.config(relief="sunken")
    
    #Fonction permettant de mettre à jour la table des résultats
    def updateTable(table, dataXY):
        [[dataY_simul, dataY_reel], dataX] = dataXY
        #Arondissement des valeurs pour un affichage plus clair
        dataY_reel = [round(x,2) for x in dataY_reel]
        dataY_simul= [round(x,2) for x in dataY_simul]
        #Mise a jour des valeurs du tableau
        table.Update(values=[ ["Simulé"] + dataY_simul, ["Réel"] + dataY_reel])
        #Calcul de la largeur des colonnes
        char_width = sg.Text.char_width_in_pixels(None)
        col_widths = [(max(len(str(columns)), min_colum_width)) *char_width for columns in dataY_reel]
        table_widget = table.Widget
        table_widget.pack_forget()
        for cid, width in enumerate(col_widths):
            table_widget.column(cid+1, width=width)
        table_widget.pack(side='left', fill='both', expand=True)
        return 0
    
    ####################################################################################################################################
    ###LAYOUT FUNCTIONS
    ####################################################################################################################################
    
    #Fonction permettant de rendre un élement extensible
    def collapse(layout, key, defaultState = True):
        return sg.pin(sg.Column(layout, key=key, visible=defaultState))
    
    ####################################################################################################################################
    ###LAYOUT
    ####################################################################################################################################
    
    
    #Table extensible
    collapsableTable = [
                        [
                            sg.Table(values = [], headings=[""] + [str(x) for x in range(1, numberOfRows+1)],num_rows=2, justification="center",
                                    expand_x = True, max_col_width=50, vertical_scroll_only=False, hide_vertical_scroll=True,
                                    key ="-DETAILSTABLE-", auto_size_columns= False, def_col_width=15, select_mode = sg.TABLE_SELECT_MODE_NONE)
                        ]
                       ]
    
    #Layout principal de la fenêtre
    layout = [  
              [     
                  sg.Push(), 
                  sg.Canvas(key='figCanvas', tooltip="Sélectionnez un élément", size =(432,288)), 
                  sg.Push()
              ],
              [
                  sg.Push(),
                  sg.Button('Puissance Totale', key="-PUISSANCETOTALEBUTTON-"),
                  sg.Push(),
                  sg.Button('Nombre de turbines', key="-NBTURBINESBUTTON-"),
                  sg.Push()
              ],
              [   
                  sg.T(SYMBOL_UP, enable_events=True, k='-OPEN TABLE-'),
                  sg.T('Détails', enable_events=True, k='-OPEN TABLE-TEXT')
              ],
              [   
                  collapse(collapsableTable, "-TABLEROW-", False)
              ]
             ]
    
    
    #Création de la fenêtre
    _VARS['window'] = sg.Window('Comparaison des résultats',
                                layout,
                                finalize=True,
                                resizable=False,
                                location=(1000, 100),
                                element_justification="left")
    
    
    ####################################################################################################################################
    ###WINDOW LIFE
    ####################################################################################################################################
    
    #Tracé par défaut
    drawChart()
    
    #Boucle d'évènements
    while True:
        #Adaptation de la taille de la fenêtre
        if numberOfRows != 1 :
            _VARS['window'].size = (max(_VARS['window']['figCanvas'].TKCanvas.winfo_width(),550), max(_VARS['window']['figCanvas'].TKCanvas.winfo_height() + 180,500))
        #Lecture des évènements
        event, values = _VARS['window'].read(timeout=200)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if "BUTTON" in event :
            #Appui sur un bouton
            #Affichage de cet appui
            pressSelectedButton(event, _VARS['window'])
            #Changement de la courbe
            dataXY = updateChart(event)
            #Permettre d'ouvrir la table
            _VARS['hasSelected'] = True
            #Mise à jour du tableau des valeurs    
            updateTable(_VARS['window']["-DETAILSTABLE-"], dataXY)
        elif event.startswith('-OPEN TABLE-'):
            #Ouverture de la table
            #Si une valeur a été seléctionnée
            if _VARS['hasSelected'] :
                #Changement d'état
                tableOpened = not tableOpened
                #Changement de l'affichage
                _VARS['window']['-OPEN TABLE-'].update(SYMBOL_DOWN if tableOpened else SYMBOL_UP)
                _VARS['window']['-TABLEROW-'].update(visible=tableOpened)
            else :
                #Fenetre d'erreur
                #Calcul de la position pour qu'elle apparaisse au centre
                whereToPopMyPopup = tuple(np.add(_VARS['window'].CurrentLocation(), np.subtract(np.divide(_VARS['window'].size, (2,2)), np.divide((187,104), (2,2)))))
                sg.Popup("Sélectionnez un élément", title = "Erreur",  keep_on_top=True, location = whereToPopMyPopup)
    
    _VARS['window'].close()