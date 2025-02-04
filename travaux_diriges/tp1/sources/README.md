
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`

## lscpu

*lscpu donne des infos utiles sur le processeur : nb core, taille de cache :*

 Model name:             Intel(R) Core(TM) i7-10510U CPU @ 1.80GHz
    CPU family:           6
    Model:                142
    Thread(s) per core:   2
    Core(s) per socket:   4
    Socket(s):            1
    Stepping:             12

Thread(s) per core : 2
Chaque cœur du processeur peut exécuter deux threads simultanément grâce à l'Hyper-Threading, ce qui améliore les performances dans les tâches parallèles.
Core(s) per socket : 4
Le processeur possède 4 cœurs physiques, chacun capable de traiter des instructions indépendantes.
Socket(s) : 1
Cela signifie que votre ordinateur dispose d'un seul processeur (socket).


## Produit matrice-matrice

### Effet de la taille de la matrice

  n            | MFlops
---------------|--------
1023           |113.915  (18.79)
1024           |72.8781  (29.46)
1025           |110.738  (19.44)
1026           |120.775  (17.86)
               |

Les matrices sont stockées en mémoire en ligne (row-major order), mais si l’algorithme accède aux colonnes plutôt qu’aux lignes, cela entraîne de nombreux cache misses, ralentissant les calculs.
Si l'algorithme n'exploite pas toutes les ressources de l'ordinateur (comme les cœurs multiples d'un processeur), le calcul est séquentiel et donc lent.
Solution : - Réorganiser les calculs pour maximiser la localité des données
1024 est censé être vraiment plus long que les deux autres (pas compréhensible sur mon ordi)

### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048)
------------------|---------|---------|----------------
i,j,k (origine)   | 24.98   | 85.94   |
j,i,k             | 7.58055 | 283.289 |
i,k,j             | 26.28   | 81.68   |
k,i,j             | 25.6775 | 83.6328 |
j,k,i             | 1.01937 | 2106.68 |1896.42(9s)
k,j,i             | 1.09636 | 1958.74 |1759.6 (9.76349)


On se place dans le pire cas, où à chaque changement de ligne le cache de la ligne précédente est supprimé, et soit une matrice carrée de taille n. Avec l'ordre (j,k,i), j est modifié n fois, k n² fois et i n³ fois. Or, quand i change il suffit de lire dans le cache la valeur, quand k change il faire une mise en cache, et quand k change il faut faire deux mises en cache (sans compter d'éventuelles mises en cache si n est plus grand que le cache, car il y en aura autant pour les trois variables). Cet ordre permet donc de minimiser le nombre de mises en cache.
--> cela permet d'exploiter des blocs mémoires continus et donc d'améliorer la vitesse de calcul


### OMP sur la meilleure boucle
Il fallait mettre :#pragma omp parallel for (pour permettre la parallélisation !)

``

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1                 |1930.77  |1898.3          |2334.6          |1807.47
2                 |2221.94  |3181.38         |2412.47         |2412.47
3                 |5212.52  |4115.6          |2797.5          |3626.97
4                 |4932.16  |5355.76         |3495.36         |4932.05
5                 |5724.39  |5991.23         |3947.04         |5521.13
6                 |5469.47  |6682.94         |5089.48         |6026.62
7                 |7725.19  |7910.59         |5316.65         |6303.8
8                 |6864.1   |8743.94         |4006.54         |8120.24
*Tracer les courbes de speedup (pour chaque valeur de n), discuter les résultats.*
S(p)= MFlops avec p threads/ MFlops avec 1 thread
​
 

![Etude des courbes de speed up (avant ajout pragma)](courbes.png)

![Etude des courbes de speed up (après ajout pragma)](courbes2.png)
Les courbes de speedup ne font pas vraiment sens, on n'observe pas d'accélération ou d'augmentaion du Mflops avec le nombre de threads. --> Pourquoi ?

Après ajout du pragma on observe bien une amélioration des performances avec le nombre de coeurs, la parallélisation permet bien d'augmenter les performances de calcul.

Afin d'optimiser la vitesse d'exécution, il faut que la mise en cache se fasse dans un cache privé propre à chaque cœur. Hors, selon comment est effectuée la parallélisation, cela peut entraîner plusieurs mises en cache des mêmes données, qui n'auraient pas forcément été nécessaires. En s'assurant que la parallélisation s'effectue de la meilleure des manières, on peut s'assurer d'une exécution plus rapide. D'où un passage par produit par blocs

### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    |
32                |6334.3   |7705.02         |4053.4          |5291.79
64                |8076.63  |6702.48         |3944.7          |5866.97
128               |7916.44  |5014.13         |3372.76         |5227.55
256               |6464.35  |4943.77         |4989.6          |4942.93
512               |6973.75  |5835.07         |3047.86         |5461.39
1024              |7278.37  |5793.3          |3938.59         |5307.25

Encore une fois les résultats ne semblent pas vraiment cohérents et on observe pas d'amélioration majeure avec ce produit par blocs.

ATTENTION : il fallait ajouter #pragma omp parallel for pour permettre de faire de la parallélisation dans le code ! Tous les résultats avant sont donc à retravailler



### Bloc + OMP


  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|----------------|----------------|---------------|
1024           |  1      |2162.91  |1967.99         |1927.38         |1788.26        |
1024           |  8      |1760.56  |1923.07         |2089.73         |1894.89        |
512            |  1      |2151.44  |1905.59         |2173.18         |1730.18        |
512            |  8      |2116.16  |1745.24         |2365.56         |1868.2         |

Je vois pas du tout ce qu'on peut en tirer encore une fois, pas d'amélioration majeure, la parallélisation ou les produits n'apportent que des améliorations très légères et encore.

(Il faudrait refaire la simulation maitenant qu'on a ajouté le pragma)


### Comparaison avec BLAS, Eigen et numpy

*Comparer les performances avec un calcul similaire utilisant les bibliothèques d'algèbre linéaire BLAS, Eigen et/ou numpy.*


# Tips

```
	env
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
