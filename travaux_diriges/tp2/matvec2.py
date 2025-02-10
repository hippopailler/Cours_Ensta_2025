# Produit matrice-vecteur v = A.u
import numpy as np

from time import time
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp, rank = globCom.size, globCom.rank

# Dimension du problème (peut être changé)
dim = 3600  # divisible par 2, 3 et 4

NLoc = dim // nbp
rowMin = rank * NLoc
rowMax = (rank + 1) * NLoc


# Initialisation de la matrice
A = np.array([[(i + j) % dim + 1.0 for i in range(dim)] for j in range(dim)])


# Initialisation du vecteur u
u = np.array([i + 1.0 for i in range(dim)])


# version locale de A
A_loc = np.array(
    [[(i + j) % dim + 1.0 for i in range(dim)] for j in range(rowMin, rowMax)]
)

# Produit matrice-vecteur
v_glob = np.zeros(dim, dtype=u.dtype)
deb = time()
v_loc = A_loc.dot(u)
globCom.Allgather(v_loc, v_glob)
fin = time()

# Vérification du résultat
v_expected = A.dot(u)
assert (v_glob == v_expected).all()

print(f"Temps du calcul du produit matrice-vecteur : {fin-deb}")