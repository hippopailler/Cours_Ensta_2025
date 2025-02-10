# Produit matrice-vecteur v = A.u
import numpy as np

from time import time
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp, rank = globCom.size, globCom.rank

# Dimension du problème (peut être changé)
dim = 3600  # divisible par 2, 3 et 4

NLoc = dim // nbp
colMin = rank * NLoc
colMax = (rank + 1) * NLoc


# Initialisation de la matrice
A = np.array([[(i + j) % dim + 1.0 for i in range(dim)] for j in range(dim)])


# Initialisation du vecteur u
u = np.array([i + 1.0 for i in range(dim)])

# versions locales de A et u
A_loc = np.array(
    [[(i + j) % dim + 1.0 for i in range(colMin, colMax)] for j in range(dim)]
)

u_loc = np.array([i + 1.0 for i in range(colMin, colMax)])

# Produit matrice-vecteur local
v_glob = np.zeros(dim, dtype=u.dtype)
deb = time()
v_loc = A_loc.dot(u_loc)
globCom.Allreduce(v_loc, v_glob, MPI.SUM)
fin = time()

# Vérification du résultat
v_expected = A.dot(u)
assert (v_glob == v_expected).all()

print(f"Temps du calcul du produit matrice-vecteur : {fin-deb}")