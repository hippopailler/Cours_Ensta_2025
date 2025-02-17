#include <mpi.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <cfloat>

using namespace std;

void generate_random_numbers(vector<float>& data, int size) {
    srand(time(nullptr));
    for (int i = 0; i < size; i++) {
        data[i] = static_cast<float>(rand()) / RAND_MAX;
    }
}

void print_vector(const vector<float>& vec, const string& label) {
    cout << label << ": ";
    for (float v : vec) {
        cout << v << " ";
    }
    cout << endl;
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, nbp;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nbp);

    int N = 1000000;  // Taille du tableau (modifiable pour voir les performances)
    vector<float> global_data;
    vector<float> local_data;

    if (rank == 0) {
        // Générer les nombres aléatoires dans le processus 0
        global_data.resize(N);
        generate_random_numbers(global_data, N);
    }

    // Mesure du temps pour le tri parallèle
    double start_parallel = MPI_Wtime();

    // Chaque processus reçoit une partie du tableau
    int local_size = N / nbp;
    local_data.resize(local_size);
    MPI_Scatter(global_data.data(), local_size, MPI_FLOAT, local_data.data(), local_size, MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Chaque processus trie sa partie localement
    sort(local_data.begin(), local_data.end());

    // Rassemble les résultats triés dans le processus 0
    MPI_Gather(local_data.data(), local_size, MPI_FLOAT, global_data.data(), local_size, MPI_FLOAT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        // Fusionner les buckets triés (Merge)
        vector<float> final_sorted;
        final_sorted.reserve(N);
        
        vector<int> indices(nbp, 0);
        for (int i = 0; i < N; ++i) {
            float min_val = FLT_MAX;
            int min_index = -1;
            for (int j = 0; j < nbp; ++j) {
                if (indices[j] < local_size && global_data[j * local_size + indices[j]] < min_val) {
                    min_val = global_data[j * local_size + indices[j]];
                    min_index = j;
                }
            }
            if (min_index != -1) {
                final_sorted.push_back(min_val);
                indices[min_index]++;
            }
        }
        
        // Fin du tri parallèle
        double end_parallel = MPI_Wtime();
        cout << "Parallel sorting time: " << (end_parallel - start_parallel) << " seconds." << endl;

        // Comparaison avec le tri séquentiel
        vector<float> sequential_data = global_data; // Copie des données non triées
        double start_sequential = MPI_Wtime();
        sort(sequential_data.begin(), sequential_data.end());
        double end_sequential = MPI_Wtime();
        
        cout << "Sequential sorting time: " << (end_sequential - start_sequential) << " seconds." << endl;
    }

    MPI_Finalize();
    return 0;
}
