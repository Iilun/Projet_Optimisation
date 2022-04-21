## Création d'un GUI pour l'optimisation d'une centrale hydroélectrique

Les dépendances requises sont présentes dans `requirements.txt` et peuvent être installées en utilisant la commande `pip install requirements.txt`.

Le programme se lance en éxécutant `GUI.py`.

## Utilisation du GUI

Le programme optimise la répartition des débits entre cinq turbines avec en entrée un débit total, et un niveau amont de l'eau. 
Cette optimisation a lieu à l'aide d'un algorithme de programmation dynamique défini dans `Projet2.py`.

### Utilisation en mode manuel

On peut choisir d'entrer un unique niveau amont et débit total. On obtient alors une fenêtre de résultats avec les différents débits calculés.

### Utilisation en mode fichier de données

En sélectionnant la checkbox `Utiliser un fichier de données`, on peut définir un fichier qui contient les informations de niveau amont et de débit.
Le fichier Data est fourni et contient des données réelles.
Une fois le calcul effectué, les résultats présentent une fenêtre graphique et un tableau de détail avec les différents débits calculés. 
Une comparaison avec un fichier de données réelles peut alors être effectué, on pourra réutiliser le fichier Data.

### Sauvegarde des résultats
En sélectionnant la checkbox `Sauvegarder les résultats`, les débits calculés seront enregistrés dans un fichier excel défini par l'utilisateur.
Celui ci présente les données brutes dans la première feuille, et des graphiques récapitulatifs dans la seconde.

### Sauvegarde des entrées
Les entrées sont sauvegardées à la fermeture du logiciel. 
