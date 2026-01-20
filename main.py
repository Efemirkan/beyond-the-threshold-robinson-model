import numpy as np
import PlotSummaryDataRobinson as psdr
import RobinsonCode as rc
import os
import yaml


def main():

    # Plot folder
    plot_folder = "plots"
    os.makedirs(plot_folder, exist_ok=True)

    # Read Parameters
    with open("params.yaml", "r", encoding="utf-8") as f:
        params = yaml.safe_load(f)

    qual_stddev_list = params["qual_stddev"] # quality noise
    threshold_stddev = params["threshold_stddev"] # threshold noise
    n = params["n"] # number of ants
    threshold_mean = params["threshold_mean"] # mean threshold

    colony_reps = params["colony_reps"] # colony repeats
    base_seed = params.get("base_seed", 42) # for reproducibility

    recruit_strength = params["recruit_strength"] # strength of recruitment
    quorum_k = params["quorum_k"] # quorum size

    quorum_sweep = params["quorum_sweep"] # quorum size to test in sweep plots
    qual_noise_fixed = params["qual_noise_fixed"] # fixed noise level for quorum sweep

    # Lists to store the average results for plotting
    acc_baseline = []
    acc_recruit = []
    acc_both = []
    time_baseline = []
    time_recruit = []
    time_both = []

    example_accepts = None
    example_accept_time = None

    # Loop through every noise level in list
    for qual_noise in qual_stddev_list:

        # No recruitment and no quorum
        temp_acc = []
        temp_time = []
        for rep in range(colony_reps):
            np.random.seed(base_seed + rep) # Change seed slightly each rep
            res = run_robinson(qual_noise, n, threshold_mean, threshold_stddev, 0, 0.0)
            temp_acc.append(res[0]) # accuracy
            temp_time.append(res[1]) # time
        acc_baseline.append(np.mean(temp_acc))
        time_baseline.append(np.mean(temp_time))

        # Recruitment Only
        temp_acc = []
        temp_time = []
        for rep in range(colony_reps):
            np.random.seed(base_seed + 100 + rep) # Use a different seed range
            res = run_robinson(qual_noise, n, threshold_mean, threshold_stddev, 0, recruit_strength)
            temp_acc.append(res[0])
            temp_time.append(res[1])
        acc_recruit.append(np.mean(temp_acc))
        time_recruit.append(np.mean(temp_time))

        # Recruit + Quorum
        temp_acc = []
        temp_time = []
        for rep in range(colony_reps):
            np.random.seed(base_seed + 200 + rep)
            res = run_robinson(qual_noise, n, threshold_mean, threshold_stddev, quorum_k, recruit_strength)

            # If the colony chose the good nest
            temp_acc.append(1.0 if res[4] == 2 else 0.0)

            # Colony decision time
            temp_time.append(res[5] if res[5] is not None else np.nan)

            # Save one representative run for plot 5
            if qual_noise == qual_noise_fixed and rep == 0:
                example_accepts = res[2]
                example_accept_time = res[3]

        # Nanmean in case some colonies never reached quorum
        acc_both.append(np.nanmean(temp_acc))
        time_both.append(np.nanmean(temp_time))

    # Package lists into dictionaries
    accuracy_results = {"baseline": acc_baseline, "recruitment only": acc_recruit, "recruit+quorum": acc_both}
    time_results = {"baseline": time_baseline, "recruitment only": time_recruit, "recruit+quorum": time_both}

    # Accuracy vs Noise Plot
    psdr.PlotAccuracyConditions(qual_stddev_list, accuracy_results,
                                os.path.join(plot_folder, "accuracy_vs_noise_conditions.png"), "Accuracy vs Noise")

    # Decision time vs Noise Plot
    psdr.PlotTimeConditions(qual_stddev_list, time_results,
                            os.path.join(plot_folder, "decision_time_vs_noise_conditions.png"),
                            "Decision time vs Noise")

    # Quorum Sweep
    q_acc = []
    q_time = []

    for qk in quorum_sweep:
        colony_accs = []
        colony_times = []

        for rep in range(colony_reps):
            seed = base_seed + rep * 100 + qk
            np.random.seed(seed)
            # Run simulation with the current quorum size
            res_q = run_robinson(qual_noise_fixed, n, threshold_mean, threshold_stddev, qk, recruit_strength)
            colony_accs.append(1.0 if res_q[4] == 2 else 0.0)
            colony_times.append(float(res_q[5]) if res_q[5] is not None else np.nan)

        # Take if good nest pick and how long it took
        q_acc.append(float(np.nanmean(colony_accs)))
        q_time.append(float(np.nanmean(colony_times)))

    # Accuracy vs Quorum Plot
    psdr.PlotAccuracyVsQuorum(quorum_sweep, q_acc, os.path.join(plot_folder, "accuracy_vs_quorum.png"),
                              "Accuracy vs Quorum")

    # Decision Time vs Quorum Plot
    psdr.PlotTimeVsQuorum(quorum_sweep, q_time, os.path.join(plot_folder, "time_vs_quorum.png"), "Time vs Quorum")

    # If example data not None, plot the dynamics in Plot 5
    if example_accepts is not None:
        nest_labels = {1: "Poor nest", 2: "Good nest"}

        psdr.PlotCommitmentDynamics(example_accepts, example_accept_time, nest_labels,
                                    os.path.join(plot_folder, "commitment_dynamics_example.png"), "Commitment Dynamics")


def run_robinson(qual_val, n, threshold_mean, threshold_stddev, quorum_k=0, recruit_strength=0.0):

    probs = np.array([[0.91, 0.15, 0.03],
                      [0.06, 0.80, 0.06],
                      [0.03, 0.05, 0.91]])

    time_means = np.array([[1, 36, 143],
                           [36, 1, 116],
                           [143, 116, 1]])

    time_stddevs = time_means / 5

    quals = np.array([-np.inf, 4, 6])

    qual_stddev = np.array([0.0, qual_val, qual_val])

    accuracy, mean_decision_time, accepts, accept_time, colony_choice, colony_time, quorum_times = rc.RobinsonCode(
        n, quals, probs, threshold_mean, threshold_stddev,
        qual_stddev, time_means, time_stddevs,
        quorum_k=quorum_k,
        recruit_strength=recruit_strength
    )

    return accuracy, mean_decision_time, accepts, accept_time, colony_choice, colony_time, quorum_times


if __name__ == "__main__":
    main()
