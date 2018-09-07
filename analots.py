#!/usr/bin/python
# -*- coding: utf-8 -*-
# ******************************************************************************
# PROGRAMME   : analots.py
# DESCRIPTION : Ce traitement identifie dans un fichier MARC passé en format 
#               texte les zones 600, 606, 607 et 610 qui contiennent de 
#               l'indexation Rameau ou libre à la condition que la notice 
#               concernée soit orientée dans un lot donné en paramètre. 
#               Il extrait les champs a, b, c, d et e pour la zone 600,
#               a, x, y et z pour les zones 606 et 607 et enfin la a pour la 610.
#               Puis il reconstruit les chaînes d'indexation, les compte et les 
#               classe par nombre d'occurrences décroissant.
# ENTREE      : trois paramètres : 
#               1. le lot à analyser 
#               2. le fichier contenant les données MARC au format texte  
#               3. le radical pour former les noms des trois fichiers de sortie
# SORTIE      : Trois fichiers (un par zone), suffixé par '-anasegment-'.
# J. CHIAVASSA-SZENBERG, CAMPUS CONDORCET, 2017
# ******************************************************************************
import itertools
import fileinput
import os.path
import sys
import time
from tqdm import tqdm 
import mmap
from collections import Counter

# **************************************************************************** #
#                                 Fonctions                                    #
# **************************************************************************** #

# ecritRameau : écriture du dictionnaire stockant les chaînes Rameau
# ******************************************************************************
def ecritRameau( rameau, tabRameau ):
    if rameau not in tabRameau:
        tabRameau[rameau] = 1
    else:
        tabRameau[rameau] += 1    
    return;

# validArgs : validation des arguments d'entrée
# ******************************************************************************
def    validArgs(tabArgs):
    # On vérifie les arguments. Message d'information s'il manque un
    # paramètre et arrêt du traitement.
    if (len(tabArgs) != 4):
        print "LOG : Erreur dans le passage des arguments : "
        print "LOG : --> usage : python anasegment valeur-lot fichier-entree radical-fichier-sortie"
        print "LOG : --> Vérifiez votre commande !"
        print "LOG : --> ATTENTION : saisissez le lot avec son segment. Ex. : B32 615 et non 615 seulement."
        print "LOG : Fin du traitement"
        sys.exit(1)
    
    return (tabArgs[1], tabArgs[2], tabArgs[3])

# get_line_number : comptage du nombre de lignes à traiter
# ******************************************************************************
def get_line_number(file_path):  
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines
    

# **************************************************************************** #
#                                   Main                                       #
# **************************************************************************** #

# Récupération des paramètres
lot = ficEntree = radFicSortie = ""
lot, ficEntree, radFicSortie = validArgs (sys.argv)

# Déclenchement du traitement 
if os.path.isfile(ficEntree):

    print "Initialisation"

    wordcount600={}
    wordcount606={}
    wordcount607={}
    wordcount610={}
    trouve689 = False
    tabIndexation=[]
    f = open(ficEntree,'r')  
    
    print "Lecture du fichier d'entrée :"

    for line in tqdm(f, total=get_line_number(ficEntree)):  
    # On lit ligne à ligne le fichier MARC au format texte :
    # - Si la ligne est une 600/606/607/610, on la stocke temporairement dans un 
    #   tableau
    # - Si la ligne est une 689 et que le segment qu'elle contient est celui  
    #   donné en paramètre alors on estime que toutes les 606 ont été trouvées  
    #   et on analyse les 6xx stockées pour en extraire l'indexation qu'on 
    #   stocke en vue du résultat final.
    # - Si la ligne est autre, on ne fait rien sauf si c'est une ligne vide.
    #   Celle-ci signale le changement de notice. Auquel cas, on réinitialise
    #   les tableaux et variables utiles pour le traitement.
    # **************************************************************************

        
        if ( line.startswith("600") or line.startswith("606") or\
             line.startswith("607") or line.startswith("610") ):
            # C'est une ligne d'indexation : stockage temporaire 
            # en attendant l'implantation en 689 pour traiter
            # ******************************************************************
            tabIndexation.append(line)
            continue # on passe à la ligne suivante
            
        elif ( line.startswith("689" ) ):
            # Si le lot contenu dans cette 689$f est celui donné en paramètre, 
            # les 6xx trouvées sont analysées. Sinon elles sont abandonnées.
            # ******************************************************************
            for cadre in line.split("$"):
                
                if (cadre.startswith("f")):

                    if (cadre[2:].strip() == lot):
                        trouve689 = True
                        break # La notice vérifie la condition sur le lot.
                    else:
                        trouve689 = False
                        
        elif ( line in ['\n', '\r\n'] ):
            # Fin de la notice : on réinitialise tout en prévision de la prochaine
            #print "LOG : Fin de la notice en cours atteinte"
            # ******************************************************************
            trouve689 = False
            tabIndexation=[]
            i = 0
            continue # on passe à la ligne suivante 
        else:
            continue # on passe à la ligne suivante 

        # Reconstruction des chaînes d'indexation si la condition sur le segment 
        # a été vérifiée.
        # **********************************************************************
        if (trouve689):

            for indexation in tabIndexation:

                chaineRameau = ""
                
                # Liste des champs nécessaires pour construire la chaîne 
                # d'indexation.
                # **************************************************************
                if ( indexation.startswith("600") ):
                    tabChamps = ["a", "b", "c", "d", "e"]
                elif ( indexation.startswith("606") or\
                       indexation.startswith("607") ):
                    tabChamps = ["a", "x", "y", "z"]
                else: # C'est une 610
                    tabChamps = ["a"]

                # Construction de la chaîne d'indexation :
                # **************************************************************
                for word in indexation.split("$"): 

                    for champs in tabChamps:
                        # Une chaine d'indexation est construite à partir de 
                        # la zone a suivie des autres dans l'ordre de tabChamps
                        # ******************************************************
                        if (word.startswith(champs)):
                            if (champs == "a"):
                                chaineRameau = word[2:].strip() 
                            else:
                                chaineRameau += " -- " +  word[2:].strip()
                ##for : Fin boucle analyse d'une ligne 606, 607, 600 ou 610

                # On stocke la chaine d'indexation reconstruite.
                # **************************************************************
                if chaineRameau != "":
                    if (indexation.startswith("600")):
                        ecritRameau(chaineRameau, wordcount600)
                    elif (indexation.startswith("606")):
                        ecritRameau(chaineRameau, wordcount606)
                    elif (indexation.startswith("607")):
                        ecritRameau(chaineRameau, wordcount607)        
                    elif (indexation.startswith("610")):
                        ecritRameau(chaineRameau, wordcount610)             
            
            ##for : Fin de l'analyse de toutes les indexation pour la notice en cours
    
    ##for : Fin de la boucle de lecture du fichier marc
    
    f.close()
    
    print "Ecriture des résultats : "

    # Création des fichiers contenant les chaînes  pour le lot et
    # le nombre d'occurrences de chacune.
    # **************************************************************************
    try:
        file600 = open(radFicSortie + "-analots-600-" + lot + ".txt",'w')    
        file606 = open(radFicSortie + "-analots-606-" + lot + ".txt",'w')
        file607 = open(radFicSortie + "-analots-607-" + lot + ".txt",'w')
        file610 = open(radFicSortie + "-analots-610-" + lot + ".txt",'w')
        
        for navette, count in sorted(wordcount600.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file600.write("%s | %i\n" % (navette, count))
            
        for navette, count in sorted(wordcount606.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file606.write("%s | %i\n" % (navette, count))

        for navette, count in sorted(wordcount607.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file607.write("%s | %i\n" % (navette, count))

        for navette, count in sorted(wordcount610.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file610.write("%s | %i\n" % (navette, count))
        
        file600.close()
        file606.close()
        file607.close()
        file610.close()
        
        print "Résultats disponibles dans les fichiers de sortie."
        
    except:
        print('LOG : Erreur à la création des fichiers')
        sys.exit(1) # quit Python

else:
    print("Pas de fichier trouvé à analyser !  Fin du traitement.")
    sys.exit(1)

print "Fin normale du traitement."    
sys.exit(0)
# **************************************************************************** #
#                                    Fin                                       #
# **************************************************************************** #