# analyse-ged
Scripts python permettant d'extraire diverses informations des données du SID Chantier

# ******************************************************************************
PROGRAMME   : anasegment.py<br>
DESCRIPTION : Ce traitement identifie dans un fichier MARC passé en format 
              texte les zones 600, 606 et 607 qui contiennent de l'indexation 
              RAMEAU à la condition que la notice concernée soit orientée dans
              un segment donné en paramètre. Il extrait les champs a, b, c, d 
              et e pour la zone 600, et a, x, y et z pour les zones 606 et 607.
              Puis il reconstruit les chaînes RAMEAU, les compte et les classe
              par nombre d'occurrences décroissant.
ENTREE      : trois paramètres : 
              1. le segment à analyser 
              2. le fichier contenant les données MARC au format texte  
              3. le radical pour former les noms des trois fichiers de sortie
SORTIE      : Trois fichiers (un par zone), suffixé par '-anasegment-'.
# ******************************************************************************
# ******************************************************************************
PROGRAMME   : anacadre.py
DESCRIPTION : Dans un fichier MARC passé en format texte, ce traitement 
              identifie les zones 689 et les analyse pour donner en sortie
              la ventilation dans le cadre de classement en général.
ENTREE      : deux paramètres : 
              1. le fichier contenant les données MARC au format texte  
              2. le radical pour former le fichier de sortie
SORTIE      : Fichier de sortie nommé avec le radical donné en paramètre 
              suffixé par "-anacadre.txt"
# ******************************************************************************
# ******************************************************************************
PROGRAMME   : anadoublons.py
DESCRIPTION : à partir d'un fichier marc au format texte passé en entrée, ce 
              traitement identifie les doublons et produit des statistiques
              par titres.
ENTREES     : 1. le fichier contenant les données MARC au format texte  
              2. le radical pour former le fichier de sortie
SORTIE      : Fichier de sortie nommé avec le radical donné en paramètre suffixé 
              par "-anadoublons.txt"
# ******************************************************************************
# ******************************************************************************
PROGRAMME   : multivol.py
DESCRIPTION : Ce programme dresse pour les titres en multivolumes les 
              informations d'implantation associées. On se base sur les 461 et
              les 517 pour détecter ces multivolumes.
ENTREE      : deux paramètres : 
                1. le fichier contenant les données MARC au format texte  
                2. le radical pour former les trois fichiers de sortie
SORTIE      : un fichier nommé avec le radical donné en paramètre suffixé par 
              '-multivol.txt'.
# ******************************************************************************
