from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth) / self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Sinon on itère
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

# Initialisation MPI --> permet de connaitre le rang et la taille du processus pour donner des tâches spécifiques à chacun des
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Je suis le processus {rank} sur {size}")

# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024

scaleX = 3./width
scaleY = 2.25/height
# Calcul de l'ensemble de mandelbrot : chaque processus calcule une partie
y_min = rank * height // nbp
y_max = (rank + 1) * height // nbp
convergence_loc = np.empty((y_max - y_min, height), dtype=np.double)
convergence = np.empty((width, height), dtype=np.double)

# Répartition équitable des lignes entre les processus
lines_per_process = height // size
start_line = rank * lines_per_process
end_line = (rank + 1) * lines_per_process if rank != size - 1 else height

# Chaque processus calcule uniquement ses lignes
local_convergence = np.empty((width, end_line - start_line), dtype=np.double)

deb = time()
for y in range(y_min, y_max):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        convergence_loc[ y - y_min,x] = mandelbrot_set.convergence(c, smooth=True)
fin = time()
print(f"Temps du calcul du sous ensemble de Mandelbrot du processus {rank}: {fin-deb}")
globCom.Gatherv(convergence_loc, convergence, 0)

# Constitution de l'image résultante : seul le processus 0 le fait
if rank == 0:
    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
    image.save("mandelbrotmpi.png")
