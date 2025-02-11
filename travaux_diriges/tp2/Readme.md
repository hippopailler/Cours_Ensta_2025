# TD n° 2 - 27 Janvier 2025

##  1. Parallélisation ensemble de Mandelbrot

L'ensensemble de Mandebrot est un ensemble fractal inventé par Benoit Mandelbrot permettant d'étudier la convergence ou la rapidité de divergence dans le plan complexe de la suite récursive suivante :
$$
\left\{
\begin{array}{l}
    c\,\,\textrm{valeurs\,\,complexe\,\,donnée}\\
    z_{0} = 0 \\
    z_{n+1} = z_{n}^{2} + c
\end{array}
\right.
$$
dépendant du paramètre $c$.

Il est facile de montrer que si il existe un $N$ tel que $\mid z_{N} \mid > 2$, alors la suite $z_{n}$ diverge. Cette propriété est très utile pour arrêter le calcul de la suite puisqu'on aura détecter que la suite a divergé. La rapidité de divergence est le plus petit $N$ trouvé pour la suite tel que $\mid z_{N} \mid > 2$.

On fixe un nombre d'itérations maximal $N_{\textrm{max}}$. Si jusqu'à cette itération, aucune valeur de $z_{N}$ ne dépasse en module 2, on considère que la suite converge.

L'ensemble de Mandelbrot sur le plan complexe est l'ensemble des valeurs de $c$ pour lesquels la suite converge.

Pour l'affichage de cette suite, on calcule une image de $W\times H$ pixels telle qu'à chaque pixel $(p_{i},p_{j})$, de l'espace image, on associe une valeur complexe  $c = x_{min} + p_{i}.\frac{x_{\textrm{max}}-x_{\textrm{min}}}{W} + i.\left(y_{\textrm{min}} + p_{j}.\frac{y_{\textrm{max}}-y_{\textrm{min}}}{H}\right)$. Pour chacune des valeurs $c$ associées à chaque pixel, on teste si la suite converge ou diverge.

- Si la suite converge, on affiche le pixel correspondant en noir
- Si la suite diverge, on affiche le pixel avec une couleur correspondant à la rapidité de divergence.

1. À partir du code séquentiel `mandelbrot.py`, faire une partition équitable par bloc suivant les lignes de l'image pour distribuer le calcul sur `nbp` processus  puis rassembler l'image sur le processus zéro pour la sauvegarder. Calculer le temps d'exécution pour différents nombre de tâches et calculer le speedup. Comment interpréter les résultats obtenus ?

--> cf mandelbrot-mpi.py

A. Pour un processus  :
Je suis le processus 0 sur 1
Temps du calcul du sous ensemble de Mandelbrot du processus 0: 2.970651865005493

B. Pour deux processus : 
Je suis le processus 0 sur 2
Je suis le processus 1 sur 2
Temps du calcul du sous ensemble de Mandelbrot du processus 1: 1.7628931999206543
Temps du calcul du sous ensemble de Mandelbrot du processus 0: 1.859450101852417

C. Pour trois processus  : 
Je suis le processus 2 sur 3
Je suis le processus 0 sur 3
Je suis le processus 1 sur 3
Temps du calcul du sous ensemble de Mandelbrot du processus 1: 0.986748456954956
Temps du calcul du sous ensemble de Mandelbrot du processus 0: 1.1308650970458984
Temps du calcul du sous ensemble de Mandelbrot du processus 2: 1.218024730682373


D. Pour 4 processus : 
Je suis le processus 2 sur 4
Je suis le processus 3 sur 4
Je suis le processus 1 sur 4
Je suis le processus 0 sur 4
Temps du calcul du sous ensemble de Mandelbrot du processus 2: 0.8368017673492432
Temps du calcul du sous ensemble de Mandelbrot du processus 1: 0.8986556529998779
Temps du calcul du sous ensemble de Mandelbrot du processus 3: 1.0038824081420898
Temps du calcul du sous ensemble de Mandelbrot du processus 0: 1.1191093921661377

La charge n'est pas uniformément répartie sur les différents processus car la séparation de l'ensemble s'est faite de manière continue sans prendre en compte les difficultés de cacul que certaines lignes pouvaient poser.
Une répartition plus fine et donc non continue serait judicieuse.

- Au lieu d’assigner **des blocs continus**, utiliser une **répartition en mode cyclic (ou dynamique)**, où chaque processus reçoit **des lignes alternées** (ex. lignes 0, 2, 4 pour P0 ; 1, 3, 5 pour P1, etc.).
- Utiliser **une approche en pool de tâches** pour équilibrer la charge.

Le **speedup** est défini comme :
\[
S(p) = \frac{T(1)}{T(p)}
\]
où :
- \( T(1) \) est le **temps d'exécution séquentiel**.
- \( T(p) \) est le **temps d'exécution avec \( p \) processus**.

| Nombre de processus \( p \) | Temps total max (s) | Speedup \( S(p) \) |
|----------------|----------------|----------------|
| 1             | 2.97           | 1.00          |
| 2             | 1.86           | 1.60          |
| 3             | 1.22           | 2.43          |
| 4             | 1.12           | 2.65          |

### **Observations :**
- Le speedup est croissant mais non linéaire.
- L'efficacité (\( E(p) = S(p) / p \)) diminue lorsque \( p \) augmente, ce qui montre que l’accélération n'est pas parfaite.

2. Réfléchissez à une meilleur répartition statique des lignes au vu de l'ensemble obtenu sur notre exemple et mettez la en œuvre. Calculer le temps d'exécution pour différents nombre de tâches et calculer le speedup et comparez avec l'ancienne répartition. Quel problème pourrait se poser avec une telle stratégie ?

--> cf mandelbrot-mpi-opt.py

Au lieu de donner un bloc continu de lignes à chaque processus, les lignes sont distribuées en alternance (ex: P0 fait les lignes 0, 4, 8... et P1 fait 1, 5, 9...).
Cela équilibre mieux la charge de calcul car certaines zones de l’image sont plus complexes à calculer que d'autres.

Pour un processus : 
Temps du calcul du sous-ensemble de Mandelbrot du processus 0: 3.7949 s

Pour deux processus :
Temps du calcul du sous-ensemble de Mandelbrot du processus 0: 1.9645 s
Temps du calcul du sous-ensemble de Mandelbrot du processus 1: 1.9662 s

Pour trois processus :
Temps du calcul du sous-ensemble de Mandelbrot du processus 0: 1.6062 s
Temps du calcul du sous-ensemble de Mandelbrot du processus 1: 1.6177 s
Temps du calcul du sous-ensemble de Mandelbrot du processus 2: 1.6115 s

Pour quatre processus :
Temps du calcul du sous-ensemble de Mandelbrot du processus 0: 1.4160 s
Temps du calcul du sous-ensemble de Mandelbrot du processus 2: 1.4829 s
Temps du calcul du sous-ensemble de Mandelbrot du processus 1: 1.4283 s
Temps du calcul du sous-ensemble de Mandelbrot du processus 3: 1.5022 s

### **Temps de calcul par processus**
| Nombre de processus | Temps processus 0 (s) | Temps processus 1 (s) | Temps processus 2 (s) | Temps processus 3 (s) |
|--------------------|------------------|------------------|------------------|------------------|
| 1                  | 3.7949           | -                | -                | -                |
| 2                  | 1.9645           | 1.9662           | -                | -                |
| 3                  | 1.6062           | 1.6177           | 1.6115           | -                |
| 4                  | 1.4160           | 1.4283           | 1.4829           | 1.5022           |

- Les temps sont **très proches entre les processus**, montrant une meilleure répartition de charge.



3. Mettre en œuvre une stratégie maître-esclave pour distribuer les différentes lignes de l'image à calculer. Calculer le speedup avec cette approche et comparez  avec les solutions différentes. Qu'en concluez-vous ?

## 2. Produit matrice-vecteur

On considère le produit d'une matrice carrée $A$ de dimension $N$ par un vecteur $u$ de même dimension dans $\mathbb{R}$. La matrice est constituée des cœfficients définis par $A_{ij} = (i+j) \mod N$. 

Par soucis de simplification, on supposera $N$ divisible par le nombre de tâches `nbp` exécutées.

### a - Produit parallèle matrice-vecteur par colonne

Afin de paralléliser le produit matrice–vecteur, on décide dans un premier temps de partitionner la matrice par un découpage par bloc de colonnes. Chaque tâche contiendra $N_{\textrm{loc}}$ colonnes de la matrice. 

- Calculer en fonction du nombre de tâches la valeur de Nloc
- Paralléliser le code séquentiel `matvec.py` en veillant à ce que chaque tâche n’assemble que la partie de la matrice utile à sa somme partielle du produit matrice-vecteur. On s’assurera que toutes les tâches à la fin du programme contiennent le vecteur résultat complet.
- Calculer le speed-up obtenu avec une telle approche


--> cf matvec1.py
Pour un processus :
- Temps du calcul du produit matrice-vecteur : 0.009612321853637695

Pour deux processus :
- Temps du calcul du produit matrice-vecteur : 0.00673985481262207
- Temps du calcul du produit matrice-vecteur : 0.04432868957519531

Pour trois processus :
- Temps du calcul du produit matrice-vecteur : 0.24751996994018555
- Temps du calcul du produit matrice-vecteur : 0.2139134407043457
- Temps du calcul du produit matrice-vecteur : 0.02121734619140625

Pour quatre processus :
- Temps du calcul du produit matrice-vecteur : 0.04156041145324707
- Temps du calcul du produit matrice-vecteur : 0.274141788482666
- Temps du calcul du produit matrice-vecteur : 0.38411641120910645
- Temps du calcul du produit matrice-vecteur : 0.0583951473236084


### b - Produit parallèle matrice-vecteur par ligne

Afin de paralléliser le produit matrice–vecteur, on décide dans un deuxième temps de partitionner la matrice par un découpage par bloc de lignes. Chaque tâche contiendra $N_{\textrm{loc}}$ lignes de la matrice.

- Calculer en fonction du nombre de tâches la valeur de Nloc
- paralléliser le code séquentiel `matvec.py` en veillant à ce que chaque tâche n’assemble que la partie de la matrice utile à son produit matrice-vecteur partiel. On s’assurera que toutes les tâches à la fin du programme contiennent le vecteur résultat complet.
- Calculer le speed-up obtenu avec une telle approche

--> cf matvec2.py

Pour un processus :
- Temps du calcul du produit matrice-vecteur : 0.005747079849243164

Pour deux processus :
- Temps du calcul du produit matrice-vecteur : 0.0030715465545654297
- Temps du calcul du produit matrice-vecteur : 0.07137298583984375

Pour trois processus :
- Temps du calcul du produit matrice-vecteur : 0.11696219444274902
- Temps du calcul du produit matrice-vecteur : 0.11955881118774414
- Temps du calcul du produit matrice-vecteur : 0.16460704803466797

Pour quatre processus : 
- Temps du calcul du produit matrice-vecteur : 0.24492692947387695
- Temps du calcul du produit matrice-vecteur : 0.09019970893859863
- Temps du calcul du produit matrice-vecteur : 0.09390997886657715
- Temps du calcul du produit matrice-vecteur : 0.2702956199645996

## 3. Entraînement pour l'examen écrit

Alice a parallélisé en partie un code sur machine à mémoire distribuée. Pour un jeu de données spécifiques, elle remarque que la partie qu’elle exécute en parallèle représente en temps de traitement 90% du temps d’exécution du programme en séquentiel.

En utilisant la loi d’Amdhal, pouvez-vous prédire l’accélération maximale que pourra obtenir Alice avec son code (en considérant n ≫ 1) ?

À votre avis, pour ce jeu de donné spécifique, quel nombre de nœuds de calcul semble-t-il raisonnable de prendre pour ne pas trop gaspiller de ressources CPU ?

En effectuant son cacul sur son calculateur, Alice s’aperçoit qu’elle obtient une accélération maximale de quatre en augmentant le nombre de nœuds de calcul pour son jeu spécifique de données.

En doublant la quantité de donnée à traiter, et en supposant la complexité de l’algorithme parallèle linéaire, quelle accélération maximale peut espérer Alice en utilisant la loi de Gustafson ?

