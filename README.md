# Beyond the Threshold

# Investigating the Impact of Recruitment and Quorum Rules in the Robinson Model

## Overview

This project implements and extends the Robinson threshold model of ant nest-site selection. The original model shows how collective decisions can emerge from simple individual rules without direct comparison between options.

The aim of this project is to study how recruitment behaviour and quorum rules influence collective decision accuracy, decision time, and commitment when nest quality information is uncertain. The model is explored using systematic parameter sweeps and repeated simulations.

This work was developed as part of an MSc in Artificial Intelligence and Adaptive Systems.

## Background

In the Robinson model, individual ants assess nest quality using noisy information and accept a site if its perceived quality exceeds an internal threshold. Collective decisions emerge from the accumulation of individual accept or reject decisions, rather than from explicit comparisons.

Previous work has shown that this simple mechanism can produce accurate collective choices. In this project, the model is extended by adding recruitment dynamics and quorum thresholds, allowing an investigation of how these mechanisms affect robustness and speed of decision-making.


## Model Description

The simulated environment contains multiple nest options with fixed true quality values. Each agent:

- Samples nest quality with noise

- Applies an acceptance threshold

- May recruit other agents depending on the experimental condition

- Triggers a collective commitment once a quorum threshold is reached

The model allows recruitment and quorum mechanisms to be enabled or disabled independently, making it possible to compare different decision regimes.


## Experiments

The main experiments focus on:

- Varying nest-quality noise levels

- Varying quorum thresholds

- Comparing conditions with and without recruitment

- Measuring decision accuracy, decision time, and commitment stability

Each parameter setting is evaluated over multiple runs to account for stochasticity.

## Results and Analysis

Simulation results are analysed using summary statistics and visualisations. The analysis focuses on:

- How recruitment affects decision speed and robustness

- How quorum size trades off speed and accuracy

- How uncertainty interacts with collective decision rules

Plots and aggregated results are saved automatically for further inspection and reporting.


## Project Structure

```bash
.
├── main.py                 # Main simulation script
├── model/                  # Core model and agent logic
├── experiments/            # Parameter sweep and experiment setup
├── analysis/               # Result processing and plotting
├── data/                   # Saved simulation outputs
└── README.md

```

## How to Run

```bash
pip install numpy matplotlib pyyaml
python main.py
```

## Author

Efe Mirkan Guner  
MSc Artificial Intelligence & Adaptive Systems  
University of Sussex

