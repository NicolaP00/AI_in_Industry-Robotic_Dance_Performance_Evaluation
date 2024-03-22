# Robotic Performance Evaluation

This repo contains all the files related to the "Robotic Dance Performances Evaluation" project for the course "AI in Industry"

Folder "Theory" contains all the useful files used to study the argument of the project and the already existing algorithms.

This is the link for the official repository of  Robotic Dance Performances Evaluation Project, held by Unibo:
https://github.com/ProjectsAI/RoboticPerformanceArtisticEvaluation

Authors: Marvasi Riccardo
         Palli Nicola
         Saturno Edoardo

Tutors: Borghesi Andrea
        De Filippo Allegra
        Giuliani Luca


### Scripts

Run each Script as follows: python Script fileCSV targetN Model

fileCSV = datasetArtisticBackground.csv | datasetScientificBackground.csv

targetN = 0 | 1 | 2 | 3 | 4 | 5 | 6

Model = lr | dt | rf | gbr

Script:
- mainScript.py      (initial script with no explainability technique)
- main.py            (script with LIME, SHAP, DiCE and ANOVA explanations)
- DiCE.py            (script with DiCE explanation only)
- Explainable.py     (script with ANOVA explanation only)

Run DiCE.sh (for all the results) as follows: ./DiCE.sh

