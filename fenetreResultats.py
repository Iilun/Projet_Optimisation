# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import selectionFichierComparaison

#Crée la fenêtre de visualisation des résultats  
def createResultWindow(results):

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

    buttonList = ["-DEBITTURBINEBUTTON" + str(i) + "-" for i in range(1,6)] + ["-PUISSANCETURBINEBUTTON" + str(i) + "-" for i in range(1,6)] + ["-DEBITVANNEBUTTON-", "-PUISSANCETOTALEBUTTON-"]



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
    def extractResults(results, puissanceOrDebit, turbine):
        debits_simules = results[0]
        puissances_simules = results[1]
        puissances_totales_simules = results[2]
        numberOfLines = len(puissances_totales_simules)

        debits_simules = pd.DataFrame(debits_simules)
        puissances_simules = pd.DataFrame(puissances_simules)
        puissances_totales_simules = pd.DataFrame(puissances_totales_simules)

        simulation = pd.concat([puissances_totales_simules,debits_simules, puissances_simules], axis=1, ignore_index=True)

        yData = simulation.loc[:, 1 + turbine + (6 if puissanceOrDebit else 0)].values.tolist()
        xData = np.linspace(1, numberOfLines, num =numberOfLines,  dtype=int).tolist()
        return (xData, yData)

    #Fonction tracant  la première figure
    def drawChart():
        _VARS['pltFig'] = plt.figure()
        plt.title("Sélectionnez une turbine")
        plt.axis('off')
        _VARS['fig_agg'] = draw_figure(
            _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

    #Fonction permettant de changer le tracé sur le canvas en fonction de l'evenement demandé
    def updateChart(turbine, puissanceOrDebit):
        turbine = int(turbine)
        _VARS['window']['figCanvas'].set_tooltip(None)
        _VARS['fig_agg'].get_tk_widget().forget()
        #Récupération des résultats
        dataXY = extractResults(results, puissanceOrDebit, turbine)
        #Gestion du titre
        puissanceOrDebit = True if turbine == -1 else puissanceOrDebit
        title = ("Turbine " + str(turbine)) if turbine > 0 else ("Total" if turbine == -1 else "Vanné")
        title += " - " + ("Puissance (MW)" if puissanceOrDebit else "Débit (m3/s)")
        
        #Création de la figure
        plt.clf()
        plt.title(title)
        #Tracé des valeurs simulées
        plt.plot(dataXY[0], dataXY[1], 'b')
        _VARS['fig_agg'] = draw_figure(
            _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])
        return dataXY

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
        #Arondissement des valeurs pour un affichage plus clair
        data = [round(x,2) for x in dataXY[1]]
        #Mise a jour des valeurs du tableau
        table.Update(values=[data])
        #Calcul de la largeur des colonnes
        char_width = sg.Text.char_width_in_pixels(None)
        col_widths = [(max(len(str(columns)), min_colum_width)) *char_width for columns in data]
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

    #Layout différent si il y'a plusieurs valeurs (graphiques)
    if (numberOfRows != 1) :

        #Table extensible
        collapsableTable = [
                            [
                              sg.Table(values = [], headings= [str(x) for x in range(1, numberOfRows+1)],num_rows=1, justification="center",
                                        expand_x = True, max_col_width=50, vertical_scroll_only=False, hide_vertical_scroll=True,
                                        key ="-DETAILSTABLE-", auto_size_columns= False, def_col_width=15, select_mode = sg.TABLE_SELECT_MODE_NONE)
                            ]
                           ]

        #Layout principal de la fenêtre
        layout = [
                    [
                      sg.Push(), sg.Canvas(key='figCanvas', tooltip="Sélectionnez un élément", size =(432,288)), sg.Push()
                    ],
                    [
                        [
                            sg.Text("Débits : "), 
                            sg.Push()
                        ] + 
                        [
                            sg.Button('Turbine ' + str(i), key="-DEBITTURBINEBUTTON" + str(i) + "-") for i in range(1,6) 
                        ] +
                        [
                            sg.Button('Vanné', key="-DEBITVANNEBUTTON-")
                        ]
                    ],
                    [
                        [
                            sg.Text("Puissances : "), 
                            sg.Push()
                        ] + 
                        [
                            sg.Button('Turbine ' + str(i), key="-PUISSANCETURBINEBUTTON" + str(i) + "-") for i in range(1,6) 
                        ] +
                        [
                            sg.Button('Totale', key="-PUISSANCETOTALEBUTTON-")
                        ]
                    ],
                    [   
                        sg.T(SYMBOL_UP, enable_events=True, k='-OPEN TABLE-'),
                        sg.T('Détails', enable_events=True, k='-OPEN TABLE-TEXT')
                    ],
                    [   
                        collapse(collapsableTable, "-TABLEROW-", False)
                    ],
                    [
                        sg.Push(),
                        sg.Button('Comparer', key="-COMPARE-")
                    ],
                 ]
    #Sinon affichage des tableaux de valeurs seulement
    else :
        #Layout principal de la fenêtre
        layout = [
                    [
                      [
                          sg.Text("Débits : ")
                      ],
                    ],
                    [
                        sg.Table(values = [list(map(str,results[0]))], headings= ["Vanné"] +["Turbine " +str(x) for x in range(1, 6)], num_rows=1,
                                justification="center", expand_x = True, max_col_width=50, vertical_scroll_only=True, hide_vertical_scroll=True,
                                key ="-DEBITSTABLE-", auto_size_columns= False, def_col_width=8, select_mode = sg.TABLE_SELECT_MODE_NONE)
                    ],
                    [
                        [
                            sg.Text("Puissances : ")
                        ],
                    ],
                    [
                        sg.Table(values = [list(map(str, [round(x,2) for x in results[1][1::]])) + [str(round(results[2],2))]], 
                                headings= ["Turbine " +str(x) for x in range(1, 6)] + ["Totale"],num_rows=1, justification="center",
                                expand_x = True, max_col_width=50, vertical_scroll_only=True, hide_vertical_scroll=True,
                                key ="-PUISSANCESTABLE-", auto_size_columns= False, def_col_width=8, select_mode = sg.TABLE_SELECT_MODE_NONE)
                    ]
                 ]

    #Création de la fenêtre
    _VARS['window'] = sg.Window('Résultats',
                                layout,
                                finalize=True,
                                resizable=False,
                                location=(100, 100),
                                element_justification="left")


    ####################################################################################################################################
    ###WINDOW LIFE
    ####################################################################################################################################

    #Premier tracé si il y'a lieu
    if numberOfRows != 1 :
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
            if "TOTALE" in event :
                dataXY = updateChart(-1, False)
            elif "VANNE" in event:
                dataXY = updateChart(0, False)
            elif "-DEBIT" in event:
                dataXY = updateChart(event[-2:-1], False)
            elif "-PUISSANCE" in event:
                dataXY = updateChart(event[-2:-1], True)
            #Permettre d'ouvrir la table
            _VARS['hasSelected'] = True
            #Mise à jour du tableau des valeurs 
            updateTable(_VARS['window']["-DETAILSTABLE-"], dataXY)
        elif event == "-COMPARE-": 
            #Appui sur le bouton de comparaison
            selectionFichierComparaison.createComparisonFileSelect(results)
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
                sg.Popup("Sélectionnez une turbine", title = "Erreur",  keep_on_top=True, location = whereToPopMyPopup)

    _VARS['window'].close()