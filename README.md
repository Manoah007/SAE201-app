# DOCUMENTATION UTILISATEURS

## PRÉSENTATION DU PROJET
Ce projet consiste en la réalisation d'une application Web basé sur une architecture MVC, qui exploite une base de données contenant 9 tables de donées indépendantes et relié au API d'amélie pour les données dynamiques (valeurs numériques, effectifs, dates, etc). Cette application est 


## COMPOSITION D'ÉQUIPE
Notre équipe nommé A2 est composé de 4 membres :
* BOUSSAIDI Malik
* CHERIFI Ismaël
* DHALI Afnanmassud
* GILLES Manoah 


## FONCTION DES FICHIERS

### Fichier de configuration du projet
* .env : pour les informations de connexions
* .env.exemple : les champs d'informations sans les valeur
* .gitignore 
#### **FICHIER .env**
Les  se trouvent dans ce fichier sous la forme de clé (qui se situe à gauche) et les valeurs (à droite). C'est un fichier qui est personnel et qui ne doit pas être partagé.

#### **FICHIER .env.exemple**
Ce fichier un exemple du fichier précédent, cependant les clés de contiennnent pas de valeur

#### **FICHIER .gitignore**
Ce fichier possède tous les fichiers qui ne doivent pas être versionné. Le fichier .env se situe donc dans ce fichier.


## Arborescence
````text
SAE201-app/
├── app.py ← point d'entrée
├── config.py ← configuration
├── .env ← identifiants (NE PAS versionner)
├── .env.example ← modèle de .env
├── .gitignore
│
├── models/ ← classes ORM + moteur BDD
│ ├── __init__.py
│ ├── db.py
│ └── dimensions.py
│
├── services/ ← services métier (tuto #2)
│ └── __init__.py
│
├── controllers/ ← routes Flask
│ ├── __init__.py
│ └── accueil.py
│
├── templates/ ← fichiers HTML Jinja2
│ ├── base.html
│ └── accueil.html
│
└── static/ ← CSS, JS, images
 └── css/
 └── style.css
````
## PRÉREQUIS ET ÉTAPES D'INSTALLATION

