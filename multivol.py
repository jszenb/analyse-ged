#!/usr/bin/python
# -*- coding: utf-8 -*-
# ******************************************************************************
# PROGRAMME   : multivol.py
# DESCRIPTION : Ce programme dresse pour les titres en multivolumes les 
#               informations d'implantation associées. On se base sur les 461 et
#               les 517 pour détecter ces multivolumes.
# ENTREE      : deux paramètres : 
#                 1. le fichier contenant les données MARC au format texte  
#                 2. le radical pour former les trois fichiers de sortie
# SORTIE      : un fichier nommé avec le radical donné en paramètre suffixé par 
#               '-multivol.txt'.
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

# validArgs : validation des arguments d'entrée
# ******************************************************************************
def    validArgs(tabArgs):
    if (len(tabArgs) != 3):
        print "LOG : Erreur dans le passage des arguments : "
        print "LOG : --> usage : python multivol fichier-entree radical-fichier-sortie"
        print "LOG : --> Vérifiez votre commande !"
        print "LOG : Fin du traitement"
        sys.exit(1)
    
    return (tabArgs[1], tabArgs[2])

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
ficEntree = radFicSortie = ""
ficEntree, radFicSortie = validArgs (sys.argv)

monTitre200 = monVolume461 = monSousTitre461 = monSousTitre517 = champ = line = ""
tabExemplaireLA = []
monVolume200 = []
monSousTitre200 = []

# Déclenchement du traitement
if os.path.isfile(ficEntree):
    f = open(ficEntree,'r')  
    g = open(radFicSortie + "-multivol.txt", 'w')

    # Ecriture de la ligne d'entête dans le fichier de sortie
    # **************************************************************************
    g.write("Titre\t200$h-200$i\t461$t\t461$v\t517$a\t689$c\t689$2\t689$3\n");
    
    for line in tqdm(f, total=get_line_number(ficEntree)):  
        # Détection des informations intéressantes en 200, 461, 517 et 689
        # **********************************************************************
        
        if (line.startswith("200")):
            for champ in line.split("$"):
                if (champ.startswith("a")):
                    # Titre de la notice
                    monTitre200 = champ[2:].strip() 
                elif (champ.startswith("h")):
                    # Volume détecté en 200
                    monVolume200.append(champ[2:].strip())
                elif (champ.startswith("i")):
                    # Sous-titre détecté en 200
                    monSousTitre200.append(champ[2:].strip())
                else:
                    continue
                    
        elif (line.startswith("461")):
            for champ in line.split("$"):
                if (champ.startswith("v")):
                    # Volume détecté en 461
                    monVolume461 = champ[2:].strip() 
                elif (champ.startswith("t")):
                    # Sous-titre détecté en 461
                    monSousTitre461 = champ[2:].strip() 
                else:
                    continue
                    
        elif (line.startswith("517")):
            for champ in line.split("$"):
                if (champ.startswith("a")):
                    # Sous-titre détecté en 517
                    monSousTitre517 = champ[2:].strip()
                else:
                    continue
                    
        elif (line.startswith("689" )):
            # Implantation
            segment = bib = codeBarre = ""
            for champ in line.split("$"):
                
                if (champ.startswith("c")):
                    segment = champ[2:].strip()
                elif (champ.startswith("2")):
                    bib =  champ[2:].strip()
                elif (champ.startswith("3")):
                    codeBarre = champ[2:].strip()
                
            tabExemplaireLA.append([segment, bib,  codeBarre])
                        
        elif (line in ['\n', '\r\n']):
            # Fin de la notice. Début de l'écriture des résultats pour cette 
            # notice.
            # ******************************************************************
            first = True
            
            buffer = monTitre200 + "\t"
            
            # Ecriture des données stockées en 200
            # ******************************************************************
            nbIteration = max([len(monVolume200)-1 , len(monSousTitre200)-1])
            if (nbIteration < 0):
                nbIteration = 0 
                
            if (nbIteration > 0 or monVolume461 != "" or monSousTitre461 != "" or monSousTitre517!= ""):
                for i in range(nbIteration):
                    if (first):
                        first = False
                    else:
                        buffer += "|"
                    
                    try:
                        buffer += monVolume200[i] 
                    except:
                        buffer += "Pas de 200$h"
                    
                    buffer += " ~ "
                    
                    try:
                        buffer += monSousTitre200[i] 
                    except:
                        buffer += "Pas de 200$i"
                
                
                # Ecriture des données stockées en 461
                # **************************************************************
                buffer += "\t" + monVolume461 + "\t"
                buffer +=  monSousTitre461 + "\t"
                
                # Ecriture des données stockées en 517
                # **************************************************************
                buffer +=  monSousTitre517 + "\t"
                
                # Ecriture des infos dans le fichier de sortie
                # **************************************************************
                for triplet in tabExemplaireLA:
                    ligne = buffer + triplet[0] + "\t" + triplet[1] + "\t'" + str(triplet[2]) + "" 
                    try:
                        g.write("%s\n" % ligne)
                    except:
                        print('LOG : Erreur écriture sortie')
                        print ligne
                        sys.exit(1) # quit Python
                    
                
            monTitre200 = monVolume461 = monSousTitre461 = monSousTitre517 = champ = ""
            tabExemplaireLA = []
            monVolume200 = []
            monSousTitre200 = []
            buffer = ""
    
    ##for : Fin de la boucle de lecture du fichier marc
    
    f.close()
    g.close()

else:
    print("Pas de fichier trouvé à analyser !  Fin du traitement.")
    sys.exit(1)

print "Fin normale du traitement."    
sys.exit(0)
# **************************************************************************** #
#                                    Fin                                       #
# **************************************************************************** #