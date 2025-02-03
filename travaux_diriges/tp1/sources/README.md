
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

``

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1                 |1930.77  |1898.3          |2334.6          |1807.47
2                 |1706     |1891.32         |2009.88         |1873.09
3                 |2050     |1905.38         |2353.66         |1863.88
4                 |2013.52  |1883.24         |2107.13         |1851.34
5                 |2113.36  |1883.71         |2517.09         |1865
6                 |2137.72  |1870.88         |2369.02         |1897.41
7                 |2087.08  |1929.36         |2260.58         |1879.46
8                 |1789.72  |1912.29         |2050.54         |1914.25
9                 |2061.69  |1709.68         |2140.84         |1875.29
*Tracer les courbes de speedup (pour chaque valeur de n), discuter les résultats.*
S(p)= MFlops avec p threads/ MFlops avec 1 thread
​
 

![Etude des courbes de speed up](courbes.png)

Les courbes de speedup ne font pas vraiment sens, on n'observe pas d'accélération ou d'augmentaion du Mflops avec le nombre de threads. --> Pourquoi ?
Afin d'optimiser la vitesse d'exécution, il faut que la mise en cache se fasse dans un cache privé propre à chaque cœur. Hors, selon comment est effectuée la parallélisation, cela peut entraîner plusieurs mises en cache des mêmes données, qui n'auraient pas forcément été nécessaires. En s'assurant que la parallélisation s'effectue de la meilleure des manières, on peut s'assurer d'une exécution plus rapide. D'où un passage par produit par blocs

### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    |
32                |2131     |1843.12         |2253.33         |1869.78
64                |1666.03  |1957.27         |2412.11
128               |2195.44  |1948.92         |2215.08
256               |2098.15  |1934.57         |2474.82
512               |2004.46  |1941.34         |1743.55
1024              |1795.12  |1830.95         |2382.13

Encore une fois les résultats ne semblent pas vraiment cohérents et on observe pas d'amélioration majeure avec ce produit par blocs.



### Bloc + OMP


  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|----------------|----------------|---------------|
1024           |  1      |2162.91  |1967.99         |1927.38         |1788.26        |
1024           |  8      |1760.56  |1923.07         |2089.73         |1894.89        |
512            |  1      |2151.44  |1905.59         |2173.18         |1730.18        |
512            |  8      |2116.16  |1745.24         |2365.56         |1868.2         |

Je vois pas du tout ce qu'on peut en tirer encore une fois, pas d'amélioration majeure, la parallélisation ou les produits n'apportent que des améliorations très légères et encore.


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
