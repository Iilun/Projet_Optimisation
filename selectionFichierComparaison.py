# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import Projet2
import fenetreComparaison
import re

#Création d'une fenêtre de choix d'un fichier de comparaison
def createComparisonFileSelect(results) :
    #Variables globales
    _VARS = {'window': False}

    numberOfRows = len(results[2]) if  isinstance(results[2] , list) else 1
    
    dataFilePath = ""
    entete = 2
    lignesDonnees = 20
    colonneDebit = "G,I,K,M,O"
    colonneAmont ="H,J,L,N,P"
    
    #Fonction permetttant seulement l'entrée d'un entier dans un champ texte
    def UpdateInputInt(event, values, forceZero = False):
        global entete
        global lignesDonnees
        
        inputValue = _VARS['window'][event]
        previousValue = inputValue.metadata
        
        #Si le champ est désactivé la saisie est ignorée
        if inputValue.Widget["state"] == "readonly":
            return
        
        if values[event] != "" :
            try :
                #Vérifier si la conversion est possible
                newValue = str(int(values[event]))
                
                #Éviter de devoir supprimer le 0, suppression auto
                if previousValue == "0" and  newValue != "0":
                    newValue = newValue.replace("0","")
                    
                #Mise à jour des valeurs du champs et des variables associées
                inputValue.metadata = newValue
                inputValue.Update(newValue)
                if event == "-ENTETE-" :
                    entete = int(newValue)
                elif event == "-LIGNESDONNEES-" :
                    lignesDonnees = int(newValue)
                    
            except :
                #Si ce n'est pas un entier, on ignore la saisie en recopiant la dernière valeur enregistrée
                values[event] = previousValue
                inputValue.Update(values[event])
        else :
            #Ne pas autoriser la valeur ""
            if forceZero :
                inputValue.metadata = "0"
                if event == "-ENTETE-" :
                    entete = 0
                elif event == "-LIGNESDONNEES-" :
                    lignesDonnees = 0
                inputValue.Update(0)
            else : 
                inputValue.metadata = "" 
    
    #Fonction permetttant seulement l'entrée de colonnes (Lettres, "," et " ")
    def UpdateInputColumn(event, values):
        global colonneDebit
        global colonneAmont
        
        inputValue = _VARS['window'][event]
        previousValue = inputValue.metadata
        
        #Si le champ est désactivé la saisie est ignorée
        if inputValue.Widget["state"] == "readonly":
            return
        
        if values[event] != "" :
            
                #Vérifier que la valeur est une lettre
                if not re.search('[^a-zA-Z, ]', values[event]) :
                    #Mise en forme en majuscule
                    newValue = values[event].upper().replace(" ","")
                    
                    #Mise à jour des valeurs du champs et des variables associées
                    inputValue.metadata = newValue
                    inputValue.Update(newValue)
                    if event == "-COLONNEDEBIT-" :
                        colonneDebit = newValue
                    elif event == "-COLONNEAMONT-" :
                        colonneAmont = newValue
                        
                else :
                    #Si ce n'est pas une lettre, on ignore la saisie en recopiant la dernière valeur enregistrée
                    values[event] = previousValue
                    inputValue.Update(values[event])
        else :
            inputValue.metadata = ""   
    
    
    ####################################################################################################################################
    ###LAYOUT
    ####################################################################################################################################
    
    #Layout générale de la fenêtre
    layout =  [
        [sg.Text("Fichier de données : "),
         sg.In(dataFilePath, size=(25, 1), enable_events=True, key="-DATAFILE-", disabled = True, readonly= True),
         sg.FileBrowse('Parcourir')],
        
        [sg.Text("Nombre de lignes d'en-tête"), sg.Push(),
         sg.InputText(str(entete), size =(4,1), key ='-ENTETE-', enable_events=True, metadata = str(entete))],
        
         [sg.Text("Colonnes des débits"), sg.Push(),
         sg.InputText(colonneDebit, size =(10,1), key ='-COLONNEDEBIT-', enable_events=True, metadata = colonneDebit)],
         
         [sg.Text("Colonnes des puissances"), sg.Push(),
         sg.InputText(colonneAmont, size =(10,1), key ='-COLONNEAMONT-', enable_events=True, metadata = colonneAmont),
         ],
         [sg.Push(),
          sg.Button(button_text="Comparer", size=(25, 3), key="-COMPAREBUTTON-", disabled= True, tooltip = "Saisir un fichier de comparaison"),
          sg.Push()
         ],
    ]
    
    
    #Création de la fenêtre
    _VARS['window'] = sg.Window('Fichier de comparaison',
                                layout,
                                finalize=True,
                                resizable=False,
    
                                element_justification="left")
    
    
    ####################################################################################################################################
    ###WINDOW LIFE
    ####################################################################################################################################
    
    
    
    
    while True:
        event, values = _VARS['window'].read(timeout=200)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif "COLONNE" in event :
            #Une modification de la valeur dans les champs de colonnes
            UpdateInputColumn(event, values)
        elif event == "-ENTETE-" :
            #Une modification de la valeur dans le champs du nombre de lignes d'entete
            UpdateInputInt(event, values, True)
        elif event == "-LIGNESDONNEES-" :
            #Une modification de la valeur dans le champs du nombre de lignes de données dans le fichier
            UpdateInputInt(event, values, True)
        elif event == "-DATAFILE-":
            #Une modification de la valeur dans la selection d'un fichier de données
            if not values["-DATAFILE-"] =="" :
                _VARS['window']["-COMPAREBUTTON-"].update(disabled=False)
                _VARS['window']["-COMPAREBUTTON-"].SetTooltip(None)
                dataFilePath = values["-DATAFILE-"]
        elif event == "-COMPAREBUTTON-":
            #Un appui sur le bouton de comparaison
            try :
                #Lecture des valeurs
                original_data_debits = Projet2.readExcelValues(entete, numberOfRows, colonneDebit, "", dataFilePath)
                original_data_puissances = Projet2.readExcelValues(entete, numberOfRows, colonneAmont, "", dataFilePath)
                #Céation de la fenetre d'affichage des résultats
                fenetreComparaison.createComparisonWindow(results, original_data_puissances, original_data_debits, _VARS['window'])
            except :
                #Si échec de la sauvegarde c'est que le fichier est ouvert, on l'afffiche à l'utilisateur
                sg.Popup("Erreur de lecture du fichier, veuillez vous assurer que les informations sont correctes", title="Erreur à la lecture", button_color= "red")
    
    _VARS['window'].close()
    