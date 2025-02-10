#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <omp.h>

int main() {
    int n_points = 1000000000; // Nombre de points à générer
    int inside_circle = 0;
    double x, y;

    // Démarrer la mesure du temps
    double start_time = omp_get_wtime();

    srand(time(NULL)); // Initialisation du générateur de nombres aléatoires

    #pragma omp parallel private(x, y) shared(inside_circle)
    {
        int local_inside_circle = 0;
        #pragma omp for
        for (int i = 0; i < n_points; i++) {
            // Générer des coordonnées aléatoires dans le carré [-1, 1]x[-1, 1]
            x = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
            y = ((double)rand() / RAND_MAX) * 2.0 - 1.0;

            // Vérifier si le point est dans le cercle
            if (x * x + y * y <= 1.0) {
                local_inside_circle++;
            }
        }

        // Mise à jour atomique de la variable partagée inside_circle
        #pragma omp atomic
        inside_circle += local_inside_circle;
    }

    // Calcul de pi
    double pi = 4.0 * inside_circle / n_points;
    printf("Valeur estimée de pi : %f\n", pi);

    // Mesurer le temps d'exécution
    double end_time = omp_get_wtime();
    printf("Temps d'exécution: %f secondes\n", end_time - start_time);

    return 0;
}