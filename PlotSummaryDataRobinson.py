import matplotlib.pyplot as plt
import numpy as np

# Function to plot how accurate the ants and colony are as noise increases
def PlotAccuracyConditions(x_vals, series_dict, out_path, title):

    # Create figure
    plt.figure(figsize=(8, 5))

    # Loop through each condition
    for label, y_vals in series_dict.items():
        plt.plot(x_vals, y_vals, marker='o', label=label)

    plt.xlabel("Nest Quality Noise (σ)") # label x-axis
    plt.ylabel("Accuracy")  # label y-axis
    plt.title(title) # set title
    plt.grid(True)  # add grid
    plt.legend() # add legend
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

# Function to plot how long it takes to make a decision as noise increases
def PlotTimeConditions(x_vals, series_dict, out_path, title):

    # Create figure
    plt.figure(figsize=(8, 5))

    # Loop through each condition
    for label, y_vals in series_dict.items():
        plt.plot(x_vals, y_vals, marker='o', label=label)

    plt.xlabel("Nest Quality Noise (σ)") # label x-axis
    plt.ylabel("Decision Time") # label y-axis
    plt.title(title) # set title
    plt.grid(True) # add grid
    plt.legend() # add legend
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

# Function to plot to observe if accuracy changes as increasing the quorum size
def PlotAccuracyVsQuorum(q_vals, acc_vals, out_path, title):

    # Create figure
    plt.figure(figsize=(8, 5))

    # Plot accuracy as a function of quorum size
    plt.plot(q_vals, acc_vals, marker='o')

    plt.xlabel("Quorum size (Q)") # label x-axis
    plt.ylabel("Accuracy") # label y-axis
    plt.title(title) # set title
    plt.grid(True) # add grid
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

# Function to plot to see if takes longer to reach a decision with a higher quorum
def PlotTimeVsQuorum(q_vals, time_vals, out_path, title):

    # Create figure
    plt.figure(figsize=(8, 5))

    # Plot commitment time as a function of quorum size
    plt.plot(q_vals, time_vals, marker='o')

    plt.xlabel("Quorum size (Q)") # label x-axis
    plt.ylabel("Time to quorum") # label y-axis
    plt.title(title) # set title
    plt.grid(True) # add grid
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

# Function to plot to see how fast the colony builds up at each nest until they hit the quorum threshold
def PlotCommitmentDynamics(accepts, accept_time, nest_labels, out_path, title):
    plt.figure(figsize=(8, 5))

    # Filter any ants that did not choose a nest
    ok_times = accept_time[~np.isnan(accept_time)]
    if len(ok_times) == 0:
        plt.close()
        return

    # Create the x-axis for the plot
    max_t = np.max(ok_times)
    t_steps = np.linspace(0, max_t, 200)

    # Loop through each nest and count arrivals
    for nest_id in sorted(set(accepts)):
        if nest_id == 0:
            continue  # skip home site

        # Get times for just this nest
        this_nest_times = accept_time[accepts == nest_id]
        this_nest_times = this_nest_times[~np.isnan(this_nest_times)]
        this_nest_times.sort()  # sort them

        # Calculate how many ants are there at each time step
        ant_counts = np.searchsorted(this_nest_times, t_steps, side='right')
        plt.plot(t_steps, ant_counts, label=nest_labels.get(nest_id, f"Nest {nest_id}"))

    plt.xlabel("Time") # label x-axis
    plt.ylabel("Number of ants committed") # label y-axis
    plt.title(title) # set title
    plt.grid(True) # add grid
    plt.legend()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()