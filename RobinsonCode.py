import numpy as np


def RobinsonCode(n, quals, probs, threshold_mean,
                 threshold_stddev, qual_stddev, time_means, time_stddevs,
                 quorum_k=0, recruit_strength=0.0):

    #   n = number of replicates (>=1)
    #   quals = row vector of m site qualities
    #		(quals(1) = home site
    #     	quality: -Inf for no effect of home site quality on searching)
    #   discovery_probabilities = m * m matrix of discovery probabilities from
    #     column site to row site (N.B. columns should sum to 1)

    #   threshold_mean: mean population threshold for site acceptability
    #   threshold_stddev: standard deviation in population thresholds

    #   qual_stddev: standard deviation in quality assessments:
    #   time_means: m * m matrix of mean travel times from column site to row
    #     site (N.B. should probably be symmetric)
    #   time_stddevs: m * m matrix of travel time standard deviations, from
    #     column site to row site (N.B. should probably be symmetric)

    # quorum_k = quorum size (0 means no quorum)
    # recruit_strength = strength of recruitment bias (0 means no recruitment)

    nestNum = probs.shape[0]  # number of sites

    # Final nest chosen by each ant
    accepts = np.zeros([n], dtype=int)

    # Time taken by each ant
    current_time = np.zeros([n])

    # discovery times and visit counts
    discovers = np.zeros([nestNum, n])
    visits = np.zeros([nestNum, n])


    Ants = []
    for i in range(n):
        ant = {'path': [],
               't': [],
               'thresh': 0,
               'selected': 0}
        Ants.append(ant)

    # Time each ant accepts a nest
    accept_time = np.full(n, np.nan)

    # Number of ants accepted each nest
    recruiters = np.zeros(nestNum, dtype=int)

    # Set the maximum number of steps for each ant
    Max_num_steps = 1000

    for i in range(n):

        # Monte Carlo simulation of one ant
        # this sets up the output variables

        # This holds the time it has taken before an ant has made the first
        # recruitment
        current_time[i] = 0

        # this is a variable which holds where ant i currently is
        accepts[i] = 0  # ant starts in home site

        # this is a matrix which holds the time at which the ant discovers
        # sites 1 to N where N= number of sites;
        # As ant is currently in the home site it never 'discovers' it
        # so set this (arbitrarily) to -1
        discovers[0,i] = -1 # ant is already in home site

        # this is a matrix which holds the number of times an ant visits
        # sites 1 to number of sites. As it is already in the home site the
        # 1st element is set to 1
        visits[0,i] = 1 # ant is already in home site

        # initialise the variables for the other home sites. it hasn't been to
        # any of the others so the time to 1st discovery is 0 and the number
        # of visits = 0
        for j in range(1, nestNum):

            discovers[j, i] = 0 # ant has not discovered or visited other sites
            visits[j, i] = 0

        # sample and set the ant's acceptance threshold
        thresh = threshold_stddev * np.random.randn() + threshold_mean

        # set up some output variables *** AOP
        num_step = 0
        Ants[i]['path'].append(accepts[i])
        Ants[i]['t'].append(current_time[i])
        Ants[i]['thresh'] = thresh
        Ants[i]['selected'] = 0

        # this is now the main loop of the program. Essentially it says:
        # 1. for the current site, check to see if the ant accepts it based on
        #    it's threshold and a randomly selected quality based on the quality
        #    of the site
        # 2. Do this until a site is accepted
        while Ants[i]['selected'] == 0:

            # check the quality of the current nest
            perceivedQuality = qual_stddev[accepts[i]] * np.random.randn() + quals[accepts[i]]

            # if the perceived nest quality is above the threshold, select it
            if perceivedQuality >= Ants[i]['thresh']:
                Ants[i]['selected'] = 1

                # Record acceptance time for quorum calculations
                accept_time[i] = current_time[i]

                # Update recruitment count for the chosen nest
                recruiters[accepts[i]] += 1
                break

            # if you have exceeded the max number of steps without stopping
            # break out of the algorithm
            if num_step > Max_num_steps:
                Ants[i]['selected'] = 0
                accept_time[i] = np.nan
                break

            # movement probabilities from current site
            p = probs[:, accepts[i]].astype(float).copy()

            # Recruitment bias toward nests with more accepted ants
            # Positive feedback mechanism
            if recruit_strength > 0.0:

                bias = recruit_strength * recruiters.astype(float)
                bias[0] = 0.0  # no recruitment to home
                p = p + bias

                # Normalise
                p = np.clip(p, 0.0, None)
                s = p.sum()
                if s > 0:
                    p = p / s
                else:
                    # Fall back to the original transition probs
                    p = probs[:, accepts[i]].astype(float).copy()

            # probablistically pick one of the new sites to go to
            # unifrnd(0,1) generates a uniformly distributed number
            # between 0 and 1
            ran = np.random.uniform()
            newsite = 0
            while ran > p[newsite]:
                ran = ran - p[newsite]
                newsite = newsite + 1

            # update the time taken with normally-distributed time-step size
            # (>=1)
            delta = max(1, time_stddevs[newsite, accepts[i]] * np.random.randn() + time_means[newsite, accepts[i]])
            current_time[i] = current_time[i] + delta

            # update ant's current site, accepts,
            # discovers, and the number of times it has been visited, visits
            accepts[i] = newsite

            # if it hasn't discovered this site before, update the time that it
            # 1st discovered it, in discovers
            if discovers[newsite, i] == 0:
                discovers[newsite, i] = current_time[i]

            # update the number of times it has visited this site
            visits[newsite, i] = visits[newsite, i] + 1

            # Update the output variables
            num_step = num_step + 1
            Ants[i]['path'].append(accepts[i])
            Ants[i]['t'].append(current_time[i])

        # record number of steps taken
        Ants[i]['numSteps'] = num_step

    # Calculate mean decision time
    mean_decision_time = float(np.mean(current_time))

    # Calculate accuracy by ants chose the good nest
    accuracy = np.sum(accepts == 2) / len(accepts)

    # Which nest reaches quorum first, None if no quorum reached
    colony_choice = None

    # Time at which the winner nest hits quorum
    # None if no quorum reached
    colony_decision_time = None

    # Time when nest j reaches quorum
    quorum_times = np.full([nestNum], np.inf)

    # Quorum
    if quorum_k > 0:
        best_time = 999999999

        for nest_idx in range(1, nestNum): # Start from 1 to skip home

            # Manually find which ants chose this nest
            nest_times = []
            for i in range(n):
                if accepts[i] == nest_idx:
                    # Check if they actually accepted
                    if not np.isnan(accept_time[i]):
                        nest_times.append(accept_time[i])

            # Check if this nest even reached the quorum size
            if len(nest_times) >= quorum_k:
                # Sort them to find when the ant arrive
                nest_times.sort()
                this_quorum_time = nest_times[quorum_k - 1]

                # Update the wiinner
                if this_quorum_time < best_time:
                    best_time = this_quorum_time
                    colony_choice = nest_idx
                    colony_decision_time = float(best_time)

        # Fill quorum_times for the return variable if needed
        for nest_idx in range(1, nestNum):
            nest_times = [accept_time[i] for i in range(n) if accepts[i] == nest_idx and not np.isnan(accept_time[i])]
            nest_times.sort()
            if len(nest_times) >= quorum_k:
                quorum_times[nest_idx] = nest_times[quorum_k - 1]

    # Take returns of accuracy, mean_decision_time, accepts,
    # accept_time, colony_choice, colony_decision_time, quorum_times
    return accuracy, mean_decision_time, accepts, accept_time, colony_choice, colony_decision_time, quorum_times
