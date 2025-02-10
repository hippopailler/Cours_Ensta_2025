#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

int main() {
    int n_points = 1000000000; // Nombre de points à générer
    int inside_circle = 0;
    double x, y;

    clock_t start_time, end_time;
    double elapsed_time;

    start_time = clock(); // Démarrer le chronomètre

    srand(time(NULL)); // Initialisation du générateur de nombres aléatoires

    for (int i = 0; i < n_points; i++) {
        // Générer des coordonnées aléatoires dans le carré [-1, 1]x[-1, 1]
        x = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
        y = ((double)rand() / RAND_MAX) * 2.0 - 1.0;

        // Vérifier si le point est dans le cercle
        if (x * x + y * y <= 1.0) {
            inside_circle++;
        }
    }

    double pi = 4.0 * inside_circle / n_points;
    printf("Valeur estimée de pi : %f\n", pi);

    end_time = clock(); // Arrêter le chronomètre
    elapsed_time = ((double)(end_time - start_time)) / CLOCKS_PER_SEC; // Calculer le temps écoulé

    printf("Temps d'exécution: %f secondes\n", elapsed_time);

    return 0;
}