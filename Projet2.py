import pandas as pd

####################################################################################################################################
###FONCTION DE SIMULATION
####################################################################################################################################

### Fonctions de simulation des turbines

def hauteur_aval(debit) :
    p1 = -1.453*10**-6
    p2 = 0.007022
    p3 = 99.98
    return p1*debit**2 + p2 * debit + p3

def hauteurChuteNette(amont, debit):
    return amont - hauteur_aval(debit) - (0.5*10**-5* debit* debit)

def p1(amont, debit) :
    p00 = 1.102
    p10 = -0.03187
    p01 = -0.04866
    p11 = 0.003308
    p02 = 0.002182
    p12 = 3.638 * 10**-5
    p03 = -1.277 * 10 **-5
    x = hauteurChuteNette(amont, debit)
    y = debit
    result = p00 + p10* x + p01 * y + p11 * x * y + p02 * y**2 + p12 * x*y**2 + p03 *y**3
    return result if result > 0 else 0

def p2(amont, debit) :
    p00 = -1.382
    p10 = 0.09969
    p01 = -1.945
    p11 = 0.09224
    p20 = -0.001724
    p02 = 0.007721
    p12 = -6.622 * 10 **-5
    p21 = -0.001096
    p03 = -1.933 * 10 **-5
    x = hauteurChuteNette(amont, debit)
    y = debit
    result = p00 + p10* x + p01 * y + p11 * x * y + p20 * x**2 + p02 * y**2 + p21* y * x**2 + p12 * x*y**2 + p03 *y**3
    return result if result > 0 else 0

def p3(amont, debit) :
    p00 = 0.7799
    p10 = -0.02261
    p01 = 0.1995
    p11 = -0.001695
    p02 = -3.519 * 10 **-5
    p12 = 7.235 * 10 **-5
    p03 = -9.338 * 10 **-6  
    x = hauteurChuteNette(amont, debit)
    y = debit
    result = p00 + p10* x + p01 * y + p11 * x * y + p02 * y**2 + p12 * x*y**2 + p03 *y**3
    return result if result > 0 else 0

def p4(amont, debit) :
    p00 = 20.22
    p10 = -0.5777
    p01 = -0.4586
    p11 = 0.01151
    p02 = 0.004886
    p12 = 1.379 * 10 **-5
    p03 = -1.882 * 10 **-5 
    x = hauteurChuteNette(amont, debit)
    y = debit
    result = p00 + p10* x + p01 * y + p11 * x * y + p02 * y**2 + p12 * x*y**2 + p03 *y**3
    return result if result > 0 else 0

def p5(amont, debit) :
    p00 = -212.1
    p10 = 12.17
    p01 = 0.004397
    p11 = -0.006808
    p20 = -0.1746
    p02 = 0.004529
    p12 = -4.211 * 10 **-5
    p21 = 0.0002936
    p03 = -1.176 * 10 **-5
    x = hauteurChuteNette(amont, debit)
    y = debit
    result = p00 + p10* x + p01 * y + p11 * x * y + p20 * x**2 + p02 * y**2 + p21* y * x**2 + p12 * x*y**2 + p03 *y**3
    return result if result > 0 else 0

def p_qvan(amont, debit):
    return 0

#Tableau regroupant ces fonctions pour un appel via indice
production_func = [p_qvan, p1, p2, p3 , p4 , p5]

####################################################################################################################################
###FONCTION UTILITAIRES
####################################################################################################################################

#Permet de réaliser la backward pass avec les indices et les débits max de chaque turbine
def reversedEnumerate(l):
    return reversed(list(enumerate(l)))

### Fonction récursive

#La fonction récursive de notre algorithme de programmation dynamique
def recursive_production(etape, etat, decision, amont, tableaux_etapes, pas_discretisation):
    #Ne pas faire les cas impossibles
    if etat < decision :
        return -1

    valeur_precedente =  tableaux_etapes[0][(etat-decision) //pas_discretisation]
    valeur_pour_cette_etape = production_func[etape](amont, decision) 
    return valeur_pour_cette_etape + valeur_precedente

### Fonction utilitaire

#Cette fonction prend en paramètre un état, et en déduit toutes les décision possibles, et sélectionne la meilleure pour cet état
def trouver_solution_optimale_pour_etat(etape, etat, amont, tableaux_etapes_valeurs, pas_discretisation, max_debit):
    valeur_max = 0
    decision_valeur_max = 0
    
    #Détermine la décision maximale possible, si l'état est le plus petit alors on ne peut affecter des décision que jusque lui, et s'il est trop grand on ne peut affecter que jusqu'au débit maximum 
    decision_maximum = min(int(max_debit), int(etat))
    #Decision forcément entre 0, et le max débit pour cette turbine
    for decision in range(0, decision_maximum+1, pas_discretisation) : 
        valeur_pour_decision = recursive_production(etape, etat , decision, amont, tableaux_etapes_valeurs, pas_discretisation)
        if valeur_pour_decision > valeur_max:
            valeur_max = valeur_pour_decision
            decision_valeur_max = decision//pas_discretisation
            
    return [decision_valeur_max, valeur_max]

####################################################################################################################################
###ALGORITHME DE PROGRAMMATION DYNAMIQUE
####################################################################################################################################

def optimisation(amont, Qtot, Qmax = [160, 160, 160, 160, 160], pas_discretisation = 5):
    Qmax = Qmax.copy()
    Qmax.insert(0, Qtot) # QVan max debit
    
    #Arrondissement de Qtot au plus proche multiple du pas d'echantillonage
    Qtot = int(Qtot//pas_discretisation*pas_discretisation)
    
    #Tableau regroupant les valeurs a toutes les etapes
    tableaux_etapes_valeurs = []
    
    #Tableau regroupant les decisions a toutes les etapes
    tableaux_etapes_decisions = []
    
    #Savoir si c'est la premiere etape
    premiere_etape = True
    
    #Backward pass 
    #Chaque etape = chaque turbine
    for etape, debit_max in reversedEnumerate(Qmax) :
        
        debit_max = int(debit_max//pas_discretisation*pas_discretisation)
        #creation du tableau
        tableau_etat_valeurs = []
        tableau_etat_decision = []
        
        #Debit max permis pour cette étape (somme des debits max des etapes precedentes)
        debit_max_permis = sum(Qmax[i] for i in range(len(Qmax)-1,etape-1,-1))
        
        #Si derniere étape : un seul état, le débit total dans la centrale 
        if etape != 0 :
            
            #Sinon : On génère les états pour chacun débits
            for etat  in (range(0, int(Qtot)+1, pas_discretisation)) : 
                #Le débit disponible est de 0, ou il est supérieur au débit max permis : pas de calcul
                if etat ==0 or etat > debit_max_permis:
                    #La decision est d'affecter 0 pour cette turbine
                    tableau_etat_decision.append(0)
                    #La valeur associée est de 0 si c'est la première étape, et celle de l'étape précedente sinon
                    if premiere_etape :
                        tableau_etat_valeurs.append(0)
                    else :
                        tableau_etat_valeurs.append(tableaux_etapes_valeurs[0][etat//pas_discretisation])
                #C'est la première étape : une seule décision possible pour chaque état: on choisit celui ci
                elif premiere_etape :
                    #Ici : probleme, on réaffecte pour chaque état, voir pour opti
                    tableau_etat_decision = list(range(0,int(debit_max)//pas_discretisation + 1))
                    tableau_etat_valeurs.append(production_func[etape](amont, etat))

                #Autres étapes : on choisit pour chaque état la meilleure décision
                else:
                    solution_optimale = trouver_solution_optimale_pour_etat(etape, etat, amont, tableaux_etapes_valeurs, pas_discretisation, debit_max)
                    tableau_etat_decision.append(solution_optimale[0])
                    tableau_etat_valeurs.append(solution_optimale[1])
        else:
            #Derniere étape, un seul état
            etat = Qtot
            solution_optimale = trouver_solution_optimale_pour_etat(etape, etat, amont, tableaux_etapes_valeurs, pas_discretisation, debit_max)
            tableau_etat_decision.append(solution_optimale[0])
            tableau_etat_valeurs.append(solution_optimale[1])
    
        premiere_etape = False
        #Insertion des tableaux de chaque étape dans le tableau mémoire
        tableaux_etapes_valeurs.insert(0,tableau_etat_valeurs)
        tableaux_etapes_decisions.insert(0, tableau_etat_decision)

        
    #Forward pass
    indice_decision = 0
    decisions_finales = []
    valeurs_finales = []
    valeur_totale = tableaux_etapes_valeurs[0][0]
    
    #Remise à jour de l'état
    etat = Qtot

    for i in range(0, len(Qmax)) :
        #la décision pour cette etape est récupérée dans le tableau des décisions
        decision_pour_cette_etape = tableaux_etapes_decisions[i][indice_decision]
        #Elle est sauvegardée
        decisions_finales.append(decision_pour_cette_etape*pas_discretisation)
        #Ainsi que sa valeur
        valeurs_finales.append(round(production_func[i](amont,decision_pour_cette_etape*pas_discretisation),2))
                               
        #Puis on met à jour l'indice et l'état pour l'étape suivante
        indice_decision = int(etat//pas_discretisation - decision_pour_cette_etape)
        etat -= decision_pour_cette_etape * pas_discretisation
    
    return [decisions_finales, valeurs_finales, valeur_totale]

####################################################################################################################################
###FONCTIONS D'EXPORTATION
#################################################################################################################################### 

#Cette fonction genère un fichier de résultat avec données et graphiques
def saveResultFile(results, path):
    
    debits_simules = results[0]
    puissances_simules = results[1]
    puissances_totales_simules = results[2]
    numberOfLines = len(puissances_totales_simules) if isinstance(puissances_totales_simules, list) else 1
    #Mise sous forme de dataframe pour exportation
    debits_simules = pd.DataFrame(debits_simules) if numberOfLines > 1 else pd.DataFrame([debits_simules])
    puissances_simules = pd.DataFrame(puissances_simules) if numberOfLines > 1 else pd.DataFrame([puissances_simules])
    puissances_totales_simules = pd.DataFrame(puissances_totales_simules) if numberOfLines > 1 else pd.DataFrame([puissances_totales_simules])

    #Concaténation des DF issus de la simulation
    simulation = pd.concat([puissances_totales_simules,debits_simules, puissances_simules], axis=1, ignore_index=True)

    finalFile =  pd.DataFrame()
    finalFile.insert(0, "Puissance Totale Simulée", simulation.loc[:,0])
    finalFile.insert(1, "QVan Simulé", simulation.loc[:,1])
    for i in range(5):
        j = i+1
        finalFile.insert(2 + 2*i, "Q" + str(j) +" Simulé", simulation.loc[:,j+1])
        finalFile.insert(3+ 2*i, "P" + str(j) +" Simulé", simulation.loc[:,j+7])
    

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    excel_file = path
    data_name = 'Data'
    chart_name = 'Charts'

    #Data
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    finalFile.to_excel(writer, sheet_name=data_name, index = False)


    # Access the XlsxWriter workbook and worksheet objects from the dataframe.
    workbook = writer.book

    #Charts
    if numberOfLines > 1 :
        worksheet = workbook.add_worksheet(chart_name)
    
        def generer_graphique_turbine(titre, proprietes_y, position, col1, numberOflines, x_scale=1.2, y_scale=1.6):
            # proprietes_y = (legende, min, max)
            chart = workbook.add_chart({'type': 'line'})
            chart.set_size({'x_scale': x_scale, 'y_scale': y_scale})
            chart.set_title({'name': titre})
            chart.add_series({
                'values':     [data_name, 1, col1, numberOflines, col1],
                'name': [data_name, 0, col1]
            })
    
            chart.set_x_axis({'name': 'Itérations', 'position_axis': 'on_tick'})
            chart.set_y_axis({'name': proprietes_y[0], 'major_gridlines': {'visible': False}, 'min': proprietes_y[1], 'max': proprietes_y[2]})
    
            worksheet.insert_chart(position, chart)
        max_puissance_totale = puissances_totales_simules.max()[0]
        generer_graphique_turbine("Puissance totale", ('Puissance totale (MW)', 0, max_puissance_totale + int(0.1*max_puissance_totale)), 'B2', 0, numberOfLines, x_scale=2)


        x_base_offset = 10
        y_start_offset = 27
        y_base_offset = 25

        for i in range(5):
            letter = chr(ord("B")+x_base_offset*(i%3))
            line = y_start_offset + y_base_offset*(i//3)
            position = letter + str(line)
            generer_graphique_turbine("Debits simulés pour la turbine "+str(i+1), ('Débit (m3/s)', 0, 170), position, 2 + 2*i, numberOfLines)
    
        generer_graphique_turbine("Debits vannés simulés", ('Débit (m3/s)', 0, 170), "V52", 1, numberOfLines)
    
        y_start_offset = 77
    
        for i in range(5):
            letter = chr(ord("B")+x_base_offset*(i%2)+2*x_base_offset*(i//4))
            line = y_start_offset + y_base_offset*(i//2) - (y_base_offset+y_base_offset//2)*(i//4)
            position = letter + str(line)
            generer_graphique_turbine("Puissances simulées pour la turbine "+str(i+1), ('Puissance (MW)', 0, 60), position, 3 + 2*i, numberOfLines)
    
    worksheet = writer.sheets[data_name]
    for idx, col in enumerate(finalFile):  # loop through all columns
        series = finalFile[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()

#Fonction permettant de lire un fichier excel de données
def readExcelValues(headerLines, dataLines, columnAmont, columnDebit, path):
    data = pd.read_excel(path, skiprows=headerLines, nrows= dataLines, usecols= columnAmont + "," + columnDebit)
    return data.values.tolist()
    