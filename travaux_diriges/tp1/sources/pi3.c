#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

int main(int argc, char *argv[]) {
    int n_points = 1000000000;
    int rank, size, local_inside_circle = 0, total_inside_circle = 0;
    double x, y;
    double start_time, end_time; // Variables pour mesurer le temps

    // Initialiser MPI
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Capturer le temps de début uniquement sur le processus maître
    if (rank == 0) {
        start_time = MPI_Wtime();
    }

    srand(rank + 1); // Utiliser une graine différente pour chaque processus

    // Répartition du travail entre les processus
    int points_per_process = n_points / size;

    for (int i = 0; i < points_per_process; i++) {
        x = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
        y = ((double)rand() / RAND_MAX) * 2.0 - 1.0;

        if (x * x + y * y <= 1.0) {
            local_inside_circle++;
        }
    }

    // Rassembler les résultats de tous les processus
    MPI_Reduce(&local_inside_circle, &total_inside_circle, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    // Calcul du temps d'exécution
    if (rank == 0) {
        end_time = MPI_Wtime(); // Capturer le temps de fin
        double elapsed_time = end_time - start_time; // Calcul du temps total

        double pi = 4.0 * total_inside_circle / n_points;
        printf("Valeur estimée de pi : %f\n", pi);
        printf("Temps d'exécution: %f secondes\n", elapsed_time);
    }

    // Finaliser MPI
    MPI_Finalize();
    return 0;
}
