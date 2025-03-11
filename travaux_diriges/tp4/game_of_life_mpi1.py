import pygame as pg
import numpy as np
import time
import sys
from multiprocessing import Process, Pipe

class Grille:
    def __init__(self, dim, init_pattern=None, color_life=pg.Color("blue"), color_dead=pg.Color("white")):
        self.dimensions = dim
        self.cells = np.zeros(self.dimensions, dtype=np.uint8)
        
        if init_pattern is not None:
            indices_i = [v[0] for v in init_pattern]
            indices_j = [v[1] for v in init_pattern]
            self.cells[indices_i, indices_j] = 1
        else:
            self.cells = np.random.randint(2, size=dim, dtype=np.uint8)
        
        self.col_life = color_life
        self.col_dead = color_dead

    def compute_next_iteration(self):
        start_time = time.time()

        neighbours_count = sum(
            np.roll(np.roll(self.cells, i, 0), j, 1) 
            for i in (-1, 0, 1) for j in (-1, 0, 1) if (i != 0 or j != 0)
        )
        next_cells = (neighbours_count == 3) | (self.cells & (neighbours_count == 2))
        self.cells = next_cells

        return next_cells, time.time() - start_time  # Retourner la nouvelle grille et le temps de calcul

class App:
    def __init__(self, geometry, grid):
        self.grid = grid
        self.size_x = geometry[1] // grid.dimensions[1]
        self.size_y = geometry[0] // grid.dimensions[0]
        self.width = grid.dimensions[1] * self.size_x
        self.height = grid.dimensions[0] * self.size_y
        self.screen = pg.display.set_mode((self.width, self.height))
        self.colors = np.array([self.grid.col_dead[:-1], self.grid.col_life[:-1]])

    def draw(self, grid_cells):
        start_time = time.time()

        surface = pg.surfarray.make_surface(self.colors[grid_cells.T])
        surface = pg.transform.flip(surface, False, True)
        surface = pg.transform.scale(surface, (self.width, self.height))
        self.screen.blit(surface, (0, 0))
        pg.display.update()

        return time.time() - start_time  # Retourner le temps d'affichage

def process_calculation(grid, conn, iterations):
    """Processus dédié au calcul"""
    total_calc_time = 0

    for _ in range(iterations):
        new_cells, calc_time = grid.compute_next_iteration()
        total_calc_time += calc_time
        conn.send((new_cells, calc_time))  # Envoyer les nouvelles cellules et le temps au processus d'affichage

    conn.send(("END", total_calc_time))  # Envoyer un signal de fin
    conn.close()

def process_display(app, conn, iterations):
    """Processus dédié à l'affichage"""
    total_draw_time = 0

    for _ in range(iterations):
        new_cells, calc_time = conn.recv()  # Recevoir les nouvelles cellules et le temps de calcul
        draw_time = app.draw(new_cells)
        total_draw_time += draw_time

    _, total_calc_time = conn.recv()  # Recevoir le signal de fin avec le temps total de calcul

    # Calculs des moyennes
    avg_calc_time = total_calc_time / iterations
    avg_draw_time = total_draw_time / iterations

    print("\nSimulation terminée !")
    print(f"Moyenne temps de calcul: {avg_calc_time:.6f}s")
    print(f"Moyenne temps d'affichage: {avg_draw_time:.6f}s")
    print(f"Temps total simulé: {total_calc_time + total_draw_time:.6f}s")

if __name__ == '__main__':
    pg.init()

    # Définition du pattern
    pattern = 'flat'
    dico_patterns = { # Dimension et pattern dans un tuple
        'blinker' : ((5,5),[(2,1),(2,2),(2,3)]),
        'toad'    : ((6,6),[(2,2),(2,3),(2,4),(3,3),(3,4),(3,5)]),
        "acorn"   : ((100,100), [(51,52),(52,54),(53,51),(53,52),(53,55),(53,56),(53,57)]),
        "beacon"  : ((6,6), [(1,3),(1,4),(2,3),(2,4),(3,1),(3,2),(4,1),(4,2)]),
        "boat" : ((5,5),[(1,1),(1,2),(2,1),(2,3),(3,2)]),
        "glider": ((100,90),[(1,1),(2,2),(2,3),(3,1),(3,2)]),
        "glider_gun": ((200,100),[(51,76),(52,74),(52,76),(53,64),(53,65),(53,72),(53,73),(53,86),(53,87),(54,63),(54,67),(54,72),(54,73),(54,86),(54,87),(55,52),(55,53),(55,62),(55,68),(55,72),(55,73),(56,52),(56,53),(56,62),(56,66),(56,68),(56,69),(56,74),(56,76),(57,62),(57,68),(57,76),(58,63),(58,67),(59,64),(59,65)]),
        "space_ship": ((25,25),[(11,13),(11,14),(12,11),(12,12),(12,14),(12,15),(13,11),(13,12),(13,13),(13,14),(14,12),(14,13)]),
        "die_hard" : ((100,100), [(51,57),(52,51),(52,52),(53,52),(53,56),(53,57),(53,58)]),
        "pulsar": ((17,17),[(2,4),(2,5),(2,6),(7,4),(7,5),(7,6),(9,4),(9,5),(9,6),(14,4),(14,5),(14,6),(2,10),(2,11),(2,12),(7,10),(7,11),(7,12),(9,10),(9,11),(9,12),(14,10),(14,11),(14,12),(4,2),(5,2),(6,2),(4,7),(5,7),(6,7),(4,9),(5,9),(6,9),(4,14),(5,14),(6,14),(10,2),(11,2),(12,2),(10,7),(11,7),(12,7),(10,9),(11,9),(12,9),(10,14),(11,14),(12,14)]),
        "floraison" : ((40,40), [(19,18),(19,19),(19,20),(20,17),(20,19),(20,21),(21,18),(21,19),(21,20)]),
        "block_switch_engine" : ((400,400), [(201,202),(201,203),(202,202),(202,203),(211,203),(212,204),(212,202),(214,204),(214,201),(215,201),(215,202),(216,201)]),
        "u" : ((200,200), [(101,101),(102,102),(103,102),(103,101),(104,103),(105,103),(105,102),(105,101),(105,105),(103,105),(102,105),(101,105),(101,104)]),
        "flat" : ((200,400), [(80,200),(81,200),(82,200),(83,200),(84,200),(85,200),(86,200),(87,200), (89,200),(90,200),(91,200),(92,200),(93,200),(97,200),(98,200),(99,200),(106,200),(107,200),(108,200),(109,200),(110,200),(111,200),(112,200),(114,200),(115,200),(116,200),(117,200),(118,200)])
    }

    # Paramètres
    resx, resy = 800, 800
    iterations = 10000
    init_pattern = dico_patterns.get(pattern, ((100,100), []))

    # Création de la grille et de l'application
    grid = Grille(*init_pattern)
    app = App((resx, resy), grid)

    # Création du pipe pour communication entre processus
    parent_conn, child_conn = Pipe()

    # Création des processus
    process_calc = Process(target=process_calculation, args=(grid, child_conn, iterations))
    process_disp = Process(target=process_display, args=(app, parent_conn, iterations))

    # Démarrer les processus
    process_calc.start()
    process_disp.start()

    # Attendre la fin des processus
    process_calc.join()
    process_disp.join()

    pg.quit()
