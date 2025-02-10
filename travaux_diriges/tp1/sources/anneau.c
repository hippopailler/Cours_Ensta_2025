#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    int rang, nbp, jeton;
    MPI_Init(&argc, &argv); //Initialise MPI
    MPI_Comm_rank(MPI_COMM_WORLD, &rang); // Récupère le rang du processus
    MPI_Comm_size(MPI_COMM_WORLD, &nbp); // Récupère le nombre total de processus

    if (rang == 0) {
        jeton = 1;  
        MPI_Send(&jeton, 1, MPI_INT, 1, 0, MPI_COMM_WORLD); // Envoie le jeton au processus suivant
    }

    for (int p = 1; p < nbp; p++) {
        if (rang == p) {
            MPI_Recv(&jeton, 1, MPI_INT, p - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE); //Reçoit le jeton du processus précédent
            jeton++;  
            int suivant = (p + 1) % nbp;
            MPI_Send(&jeton, 1, MPI_INT, suivant, 0, MPI_COMM_WORLD);
        }
    }

    if (rang == 0) {
        MPI_Recv(&jeton, 1, MPI_INT, nbp - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Jeton final reçu par le processus 0 : %d\n", jeton);
    }

    MPI_Finalize();
    return 0;
}