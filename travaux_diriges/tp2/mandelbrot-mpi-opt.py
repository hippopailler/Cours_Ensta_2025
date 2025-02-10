from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth) / self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex, smooth=False) -> int | float:
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                return iter + 1 - log(log(abs(z))) / log(2) if smooth else iter
        return self.max_iterations

# Paramètres
width, height = 1024, 1024
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)

scaleX = 3./width
scaleY = 2.25/height

# Répartition en Round-Robin
local_lines = [y for y in range(height) if y % size == rank]
num_local_lines = len(local_lines)

# Allocation des tableaux locaux
local_convergence = np.empty((num_local_lines, width), dtype=np.double)

# Calcul des valeurs locales
deb = time()
for i, y in enumerate(local_lines):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        local_convergence[i, x] = mandelbrot_set.convergence(c, smooth=True)
fin = time()
print(f"Temps du calcul du sous-ensemble de Mandelbrot du processus {rank}: {fin-deb:.4f} s")

# Réglage des paramètres pour MPI_Gatherv
local_sizes = np.array(comm.gather(num_local_lines, root=0))
recvcounts = local_sizes * width if rank == 0 else None
displs = np.insert(np.cumsum(recvcounts[:-1]), 0, 0) if rank == 0 else None

# Allocation du tableau global uniquement sur le root
convergence = np.empty((height, width), dtype=np.double) if rank == 0 else None

# Rassemblement des données
comm.Gatherv(local_convergence.flatten(), [convergence, recvcounts, displs, MPI.DOUBLE], root=0)

# Reconstruction et affichage de l'image
if rank == 0:
    # On trie les lignes selon leur numéro initial (important en round-robin)
    sorted_indices = np.argsort(local_lines)
    convergence = np.vstack([convergence[i, :] for i in sorted_indices])

    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T) * 255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb:.4f} s")
    image.show()
    image.save("mandelbrotmpiopt.png")


