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

    int N = 5000000; 
    vector<float> global_data;
    vector<float> local_data;

    if (rank == 0) {
        global_data.resize(N);
        generate_random_numbers(global_data, N);
    }
    double start_parallel = MPI_Wtime();

    // Répartition des données avec MPI_Scatter
    int local_size = N / nbp;
    local_data.resize(local_size);
    MPI_Scatter(global_data.data(), local_size, MPI_FLOAT, local_data.data(), local_size, MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Tri local de chaque bloc
    sort(local_data.begin(), local_data.end());

    // Sélection d'échantillons pour déterminer les pivots
    int num_samples = nbp - 1;
    vector<float> local_samples(num_samples);
    for (int i = 0; i < num_samples; i++) {
        local_samples[i] = local_data[(i + 1) * local_size / (nbp + 1)];
    }

    // Réduction des échantillons dans le processus 0
    vector<float> gathered_samples(nbp * num_samples);
    MPI_Gather(local_samples.data(), num_samples, MPI_FLOAT, gathered_samples.data(), num_samples, MPI_FLOAT, 0, MPI_COMM_WORLD);

    vector<float> pivots(num_samples);
    if (rank == 0) {
        sort(gathered_samples.begin(), gathered_samples.end());
        for (int i = 0; i < num_samples; i++) {
            pivots[i] = gathered_samples[(i + 1) * nbp / (nbp + 1)];
        }
    }

    // Diffusion des pivots à tous les processus
    MPI_Bcast(pivots.data(), num_samples, MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Répartition des données en fonction des pivots
    vector<vector<float>> buckets(nbp);
    for (float num : local_data) {
        int dest = 0;
        while (dest < num_samples && num > pivots[dest]) {
            dest++;
        }
        buckets[dest].push_back(num);
    }

    // Calcul des tailles des buckets pour chaque processus
    vector<int> send_counts(nbp);
    for (int i = 0; i < nbp; i++) {
        send_counts[i] = buckets[i].size();
    }

    vector<int> recv_counts(nbp);
    MPI_Alltoall(send_counts.data(), 1, MPI_INT, recv_counts.data(), 1, MPI_INT, MPI_COMM_WORLD);

    // Création des buffers pour réception
    vector<float> recv_data;
    int total_recv = 0;
    vector<int> recv_displs(nbp, 0), send_displs(nbp, 0);

    for (int i = 0; i < nbp; i++) {
        total_recv += recv_counts[i];
        if (i > 0) {
            send_displs[i] = send_displs[i - 1] + send_counts[i - 1];
            recv_displs[i] = recv_displs[i - 1] + recv_counts[i - 1];
        }
    }
    recv_data.resize(total_recv);

    // Envoi des données triées aux bons processus
    MPI_Alltoallv(buckets[0].data(), send_counts.data(), send_displs.data(), MPI_FLOAT,
                  recv_data.data(), recv_counts.data(), recv_displs.data(), MPI_FLOAT,
                  MPI_COMM_WORLD);

    // Tri local des données reçues
    sort(recv_data.begin(), recv_data.end());

    // Rassemblement des données finales
    vector<int> final_displs(nbp, 0);
    vector<int> final_sizes(nbp);
    MPI_Gather(&total_recv, 1, MPI_INT, final_sizes.data(), 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        for (int i = 1; i < nbp; i++) {
            final_displs[i] = final_displs[i - 1] + final_sizes[i - 1];
        }
        global_data.resize(N);
    }

    MPI_Gatherv(recv_data.data(), total_recv, MPI_FLOAT,
                global_data.data(), final_sizes.data(), final_displs.data(), MPI_FLOAT,
                0, MPI_COMM_WORLD);

    if (rank == 0) {
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
