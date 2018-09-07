#!/usr/bin/python
# -*- coding: utf-8 -*-
# ******************************************************************************
# PROGRAMME   : anasegment.py
# DESCRIPTION : Ce traitement identifie dans un fichier MARC passé en format 
#               texte les zones 600, 606 et 607 qui contiennent de l'indexation 
#               RAMEAU à la condition que la notice concernée soit orientée dans
#               un segment donné en paramètre. Il extrait les champs a, b, c, d 
#               et e pour la zone 600, et a, x, y et z pour les zones 606 et 607.
#               Puis il reconstruit les chaînes RAMEAU, les compte et les classe
#               par nombre d'occurrences décroissant.
# ENTREE      : trois paramètres : 
#               1. le segment à analyser 
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
        print "LOG : --> usage : python anasegment valeur-segment fichier-entree radical-fichier-sortie"
        print "LOG : --> Vérifiez votre commande !"
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
segment = ficEntree = radFicSortie = ""
segment, ficEntree, radFicSortie = validArgs (sys.argv)

# Déclenchement du traitement 
if os.path.isfile(ficEntree):

    print "Initialisation"

    wordcount600={}
    wordcount606={}
    wordcount607={}
    trouve689 = False
    tabIndexation=[]
    f = open(ficEntree,'r')  
    
    print "Lecture du fichier d'entrée :"

    for line in tqdm(f, total=get_line_number(ficEntree)):  
    # On lit ligne à ligne le fichier MARC au format texte :
    # - Si la ligne est une 600/606/607, on la stocke temporairement dans un 
    #   tableau
    # - Si la ligne est une 689 et que le segment qu'elle contient est celui  
    #   donné en paramètre alors on estime que toutes les 606 ont été trouvées  
    #   et on analyse les 606 stockées pour en extraire l'indexation qu'on 
    #   stocke en vue du résultat final.
    # - Si la ligne est autre, on ne fait rien sauf si c'est une ligne vide.
    #   Celle-ci signale le changement de notice. Auquel cas, on réinitialise
    #   les tableaux et variables utiles pour le traitement.
    # **************************************************************************

        
        if ( line.startswith("600") or line.startswith("606") or line.startswith("607") ):
            # C'est une ligne d'indexation : stockage temporaire 
            # en attendant l'implantation en 689 pour traiter
            # ******************************************************************
            tabIndexation.append(line)
            continue # on passe à la ligne suivante
            
        elif ( line.startswith("689" ) ):
            # Si le segment contenu dans cette 689$c est celui donné en paramètre, 
            # les 60x trouvées sont analysées. Sinon elles sont abandonnées.
            # ******************************************************************
            for cadre in line.split("$"):
                
                if (cadre.startswith("c")):

                    if (cadre[2:].strip() == segment):
                        trouve689 = True
                        break # La notice vérifie la condition sur le segment.
                    else:
                        trouve689 = False
                        
        elif ( line in ['\n', '\r\n'] ):
            # Fin de la notice : reconstruction des chaînes et réinitialisation
            # avant passage à la notice suivante
            # ******************************************************************

            # Reconstruction des chaînes d'indexation si la condition sur le segment 
            # a été vérifiée.
            # **********************************************************************
            if (trouve689):
            
                for indexation in tabIndexation:
            
                    chaineRameau = ""
                    
                    # Liste des champs nécessaires pour construire la chaîne Rameau
                    # **************************************************************
                    if ( indexation.startswith("600") ):
                        tabChamps = ["a", "b", "c", "d", "e"]
                    else:
                        tabChamps = ["a", "x", "y", "z"]
            
                    # Construction de la chaîne Rameau :
                    # **************************************************************
                    for word in indexation.split("$"): 
            
                        for champs in tabChamps:
                            # Une chaine Rameau est construite à partir des zones a,  
                            # x, y et z.
                            # ******************************************************
                            if (word.startswith(champs)):
                                if (champs == "a"):
                                    chaineRameau = word[2:].strip() 
                                else:
                                    chaineRameau += " -- " +  word[2:].strip()
                    ##for : Fin boucle analyse d'une ligne 606, 607 ou 600
            
                    # On stocke la chaine Rameau reconstruite.
                    # **************************************************************
                    if chaineRameau != "":
                        if (indexation.startswith("600")):
                            ecritRameau(chaineRameau, wordcount600)
                        elif (indexation.startswith("606")):
                            ecritRameau(chaineRameau, wordcount606)
                        elif (indexation.startswith("607")):
                            ecritRameau(chaineRameau, wordcount607)                    
                
                ##for : Fin de l'analyse de toutes les indexation pour la notice en cours


            trouve689 = False
            tabIndexation=[]
            i = 0
            continue # on passe à la ligne suivante 
        else:
            continue # on passe à la ligne suivante 
    
    ##for : Fin de la boucle de lecture du fichier marc
    
    f.close()
    
    print "Ecriture des résultats : "

    # Création des fichiers contenant les chaînes Rameau pour le segment et
    # le nombre d'occurrences de chacune.
    # **************************************************************************
    try:
        file600 = open(radFicSortie + "-anasegment-600-" + segment + ".txt",'w')    
        file606 = open(radFicSortie + "-anasegment-606-" + segment + ".txt",'w')
        file607 = open(radFicSortie + "-anasegment-607-" + segment + ".txt",'w')
        
        for navette, count in sorted(wordcount600.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file600.write("%s | %i\n" % (navette, count))
            
        for navette, count in sorted(wordcount606.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file606.write("%s | %i\n" % (navette, count))

        for navette, count in sorted(wordcount607.iteritems(), key=lambda (n,c): (c,n), reverse=True):
            file607.write("%s | %i\n" % (navette, count))
        
        file600.close()
        file606.close()
        file607.close()
        
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