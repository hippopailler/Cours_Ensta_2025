Hippolyte PAILLER

# TD4 : Optimisation du jeu de la vie

## Partie 1 : répérer les étapes critiques du programme

Pour identifier les étapes les plus consommatrices en ressources, j'ai ajouté des indicateurs de temps pour mesurer :

- Le temps de calcul de la génération suivante (compute_next_iteration).
- Le temps de rendu graphique (draw).
- L'occupation mémoire en utilisant sys.getsizeof() pour mesurer la taille des structures principales.


Pour gagner en lisibilité et avoir une analyse plus fine, on faire un nombre restreint d'itérations et calculer le temps moyen de rendu graphique et de calcul en fonction des différents patterns de départ.

### Analyse des résultats en fonction des différents patterns
Pour 500 itérations on obtient 

--> introduire le tableau de comparaison des temps en fonction du pattern initial
    --> cf game_of_life_temps.py


--> Globalement, le temps d'affichage est plpus long que le temps de calcul



- Première étape : paralléliser en séparant calcul et affichage, une fois que le calcul est fini on l'envoi à l'affichage. Mais dèséquilibre de charges, le calcul va toujours attendre l'affichage 
    - cf game_of_life_mpi1

- Deuxième étape : l'affichage est là pour faire beau, on peut afficher une itération sur dix par exemple. Ou mieux, on calcule en continu et que affichage est disponible il affiche (proche de maitre esclave). On cherche à faire de l'asychronisme. Il faut que calcul envoi les données au bon moment. Comment faire ? Il faut que affichage envoi un message à calcul pour lui dire qu'il est disponible afin de recevoir les prochaines données à afficher. 
    - cf game_of_life_mpi2

- Troisième étape : paralléliser le calcul, on peut partionner le maillage, pour les zones au milieu qui peuvent poser problèmes car il faut communiquer, on doit avoir recours aux cellules fantômes






Pour le projet :
- binome 
- partager le code sur un dépot avec un rapport
- plus un petit oral individuel de 10 minutes environ, sur le projet, pour tester notre compréhension de l'ensemble 