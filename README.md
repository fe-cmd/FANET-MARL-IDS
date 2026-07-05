# FANET-MARL-IDS

## Multi-Agent Deep Reinforcement Learning Intrusion Detection System for Flying Ad Hoc Networks (FANETs)

---

## Project Overview

FANET-MARL-IDS is a decentralized Intrusion Detection System (IDS) developed for Flying Ad Hoc Networks (FANETs) using Multi-Agent Deep Reinforcement Learning (MARL). The project applies the Multi-Agent Proximal Policy Optimization (MAPPO) algorithm to enable each unmanned aerial vehicle (UAV) to independently observe neighbouring drones, identify malicious behaviour, and make intelligent security decisions without relying on a centralized controller.

The current implementation simulates a FANET environment consisting of multiple UAVs, where one or more drones may behave maliciously through GPS spoofing attacks. Each UAV continuously monitors its surroundings, estimates trust levels, detects anomalies, and learns an optimal response policy through reinforcement learning.

The project has been implemented in Python using PyTorch and follows a modular architecture, making it easier to extend with additional attacks, datasets, communication protocols, and reinforcement learning algorithms.

---

# Project Structure

```text
FANET-MARL-IDS/
│
├── config/
├── env/
├── mappo/
├── tests/
├── train/
├── utils/
│
├── main.py
├── requirements.txt
└── README.md
```

Each folder has a specific responsibility within the overall system. The following sections describe the purpose of every module.

---

# Configuration Module (`config/`)

The **config** folder stores the system-wide configuration parameters that control how the FANET simulation operates. Keeping these settings separate from the implementation allows experiments to be repeated easily by modifying only the configuration values.

## action_space.py

This file defines the discrete action space available to every reinforcement learning agent.

```python
0 → TRUST
1 → SUSPECT
2 → ISOLATE
```

These actions represent the security decisions that an observing drone can make regarding another drone within the network.

- **TRUST** indicates that the neighbour is considered legitimate.
- **SUSPECT** represents uncertainty and assigns a moderate suspicion level.
- **ISOLATE** classifies the neighbour as malicious and recommends removing it from network participation.

The MAPPO actor network predicts one of these actions during every interaction with the environment.

---

## config.py

This file contains the global simulation parameters used throughout the project.

Some of the important parameters include:

- Number of drones participating in the FANET.
- Number of legitimate drones.
- Three-dimensional simulation space size.
- Simulation time step.
- Maximum UAV velocity.
- Attack probability.
- Detection threshold.

Because these values are centralized inside one configuration file, changing the simulation size or difficulty requires modifying only this file rather than several source files.

---

# Environment Module (`env/`)

The **env** folder implements the FANET simulation itself. It models drone behaviour, network interactions, cyber-attacks, observations, trust computation, anomaly detection, and reward generation for reinforcement learning.

This module acts as the environment in which the MAPPO agents are trained.

---

## attacks.py

This module contains the cyber-attacks implemented within the simulation.

Currently, the project implements **GPS Spoofing**.

Rather than changing the drone's true position, the attack modifies only the position that the attacker broadcasts to neighbouring drones. As a result, honest drones receive false location information, creating inconsistencies that can later be detected through anomaly analysis.

The attack intensity can be adjusted to simulate different spoofing strengths.

---

## drone.py

This file defines the Drone class, which represents every UAV participating in the FANET.

Each drone maintains both physical and cyber-related properties including:

- Drone identifier
- Position
- Velocity
- Remaining energy
- Claimed GPS position
- Trust score
- Anomaly score
- Attacker status

The Drone class also provides helper functions for updating movement, computing flight speed, calculating GPS error, and displaying drone information during debugging.

Every drone created during simulation is an instance of this class.

---

## dynamics.py

This module provides the basic physics used to update UAV movement.

Its primary responsibility is updating each drone's position according to its velocity and the simulation time step.

Separating motion dynamics into an independent file makes it easier to introduce more realistic flight models in future work without modifying other components.

---

## fanet_env.py

This is the core environment of the entire project.

It coordinates every stage of the simulation and serves as the interaction point between the reinforcement learning agents and the FANET.

During each simulation step, the environment performs the following operations:

1. Updates drone movement.
2. Allows legitimate drones to broadcast their true positions.
3. Applies GPS spoofing to attacker drones.
4. Computes GPS errors and anomaly scores.
5. Updates trust values.
6. Calculates reinforcement learning rewards.
7. Generates the next observation state.
8. Determines whether the episode has ended.

This module is responsible for maintaining the complete simulation lifecycle.

---

## observation.py

The observation module constructs the information available to every reinforcement learning agent.

For each UAV, it collects both physical and security-related features including:

- Current position
- Velocity
- Speed
- Claimed GPS position
- GPS error
- Trust score
- Anomaly score
- Distances to neighbouring drones

These observations are then converted into numerical feature vectors that can be processed directly by the MAPPO neural networks.

This observation vector serves as the input to the actor and critic networks during training.

---

## reward.py

This module implements the reinforcement learning reward function.

Rewards are assigned according to whether the agent correctly identifies legitimate or malicious drones.

For malicious drones:

- Trusting an attacker receives a strong negative reward.
- Suspecting an attacker receives a moderate positive reward.
- Correctly isolating an attacker receives the highest positive reward.

For legitimate drones:

- Correctly trusting a legitimate neighbour receives a positive reward.
- Incorrectly suspecting a legitimate drone results in a penalty.
- Incorrectly isolating a legitimate drone receives the largest penalty.

This reward design encourages the learning agent to maximise attack detection while minimising false alarms, thereby improving the overall reliability of the intrusion detection system.

---

## fusion.py

This module is currently reserved for future work.

It is intended to support information fusion techniques in which observations or trust values collected by multiple UAVs can be combined before making intrusion detection decisions.

Although the file is presently empty, it has been included in anticipation of future extensions involving cooperative multi-agent trust fusion and distributed decision-making.

# Multi-Agent Reinforcement Learning Module (`mappo/`)

The **mappo** folder contains the complete implementation of the Multi-Agent Proximal Policy Optimization (MAPPO) algorithm used to train the intrusion detection agents.

Unlike conventional machine learning approaches where a centralized model makes all decisions, the MAPPO framework allows each drone to act as an independent learning agent. Every UAV observes its local environment, selects an action, receives a reward, and gradually improves its decision-making policy through reinforcement learning.

The module consists of four major components:

- Actor Network
- Critic Network
- Replay Buffer
- MAPPO Learning Algorithm

These components work together during every training episode to enable decentralized learning within the FANET.

---

## actor.py

The **Actor** network is responsible for making decisions.

Its primary function is to receive the observation vector generated for each drone and determine which action should be taken.

The observation vector contains physical, cyber-security and network-related information such as:

- Drone position
- Velocity
- Speed
- Claimed GPS position
- GPS error
- Trust score
- Anomaly score

After processing these features through a neural network, the actor outputs a probability distribution over the available actions.

The available actions are:

```text
0 → TRUST
1 → SUSPECT
2 → ISOLATE
```

Rather than always selecting the highest probability action, the policy samples from the probability distribution. This allows the agent to explore different behaviours during training and gradually discover an optimal intrusion detection strategy.

The actor network therefore represents the decision-making component of the reinforcement learning agent.

---

## critic.py

The **Critic** network evaluates how good the current situation is for the learning agent.

Instead of selecting actions, the critic estimates the expected future return of the current observation.

Its output is called the **state value**, which measures how beneficial the current state is likely to be in terms of future rewards.

The value estimated by the critic is used during training to calculate the **advantage function**, allowing the actor to determine whether its chosen action performed better or worse than expected.

Separating the actor from the critic significantly improves learning stability and is one of the defining characteristics of the PPO and MAPPO algorithms.

---

## buffer.py

The Replay Buffer temporarily stores experiences collected during one episode of interaction with the FANET environment.

For every drone action, the following information is stored:

- Observation state
- Selected action
- Action log probability
- Reward received

Unlike experience replay used in Deep Q-Networks (DQN), PPO-based algorithms use the collected experiences only for the current policy update.

Once the policy has been updated, the buffer is cleared and begins collecting new experiences for the next episode.

This process ensures that policy updates are always performed using data generated by the current policy.

---

## mappo.py

This file contains the complete implementation of the Multi-Agent Proximal Policy Optimization (MAPPO) learning algorithm.

It coordinates the interaction between the Actor network, Critic network and Replay Buffer throughout the training process.

The implementation includes several mechanisms that improve training stability, including:

- Reward clipping
- State normalization
- Return normalization
- Advantage normalization
- PPO clipped objective
- Mini-batch gradient updates
- Gradient clipping
- Learning rate scheduling

These techniques help prevent unstable learning and reduce the likelihood of excessively large parameter updates during optimisation.

The MAPPO training cycle follows the standard PPO framework.

### Step 1 – Collect Experiences

Each drone observes its environment and constructs its observation vector.

The Actor network receives this observation and predicts an action.

The selected action is then executed within the FANET environment.

---

### Step 2 – Receive Rewards

After every drone performs its selected action, the environment evaluates whether the decision was correct.

Rewards are assigned according to the reward function defined in **reward.py**.

Correct identification of malicious drones increases the cumulative reward, while incorrect decisions result in penalties.

---

### Step 3 – Store Experiences

The observation, selected action, action probability and received reward are stored inside the Replay Buffer.

These experiences represent one trajectory collected by the current policy.

---

### Step 4 – Compute Returns

Once an episode has finished, the algorithm computes the discounted return for every stored experience.

Discounted returns allow the learning agent to consider both immediate and future rewards when updating its policy.

---

### Step 5 – Estimate State Values

The Critic network evaluates every stored observation and estimates its expected long-term value.

These state value estimates are later compared with the actual discounted returns.

---

### Step 6 – Compute Advantages

The difference between the discounted return and the critic's value estimate produces the **advantage**.

The advantage indicates whether a chosen action performed better or worse than expected.

Positive advantages encourage similar actions in the future, while negative advantages reduce their probability.

---

### Step 7 – Update the Actor

The Actor network is updated using the PPO clipped objective function.

Rather than allowing excessively large policy updates, PPO limits how much the policy can change during each optimisation step.

This clipping mechanism significantly improves learning stability and prevents sudden performance degradation.

---

### Step 8 – Update the Critic

The Critic network is trained by minimizing the difference between its predicted state values and the actual discounted returns.

As training progresses, the critic becomes increasingly accurate at evaluating future rewards, providing better guidance for the actor.

---

### Step 9 – Repeat the Process

Once both neural networks have been updated, the Replay Buffer is cleared and the next training episode begins.

Through repeated interaction with the FANET environment, the policy gradually improves its ability to distinguish between legitimate and malicious drones.

---

# MAPPO Training Workflow

The overall reinforcement learning process implemented in this project can be summarised as follows:

```text
Environment Reset
        │
        ▼
Generate Drone Observations
        │
        ▼
Actor Network Selects Actions
        │
        ▼
Execute Actions in FANET
        │
        ▼
Compute Rewards
        │
        ▼
Store Experiences in Replay Buffer
        │
        ▼
Episode Ends
        │
        ▼
Compute Returns
        │
        ▼
Estimate State Values (Critic)
        │
        ▼
Calculate Advantages
        │
        ▼
Update Actor Network
        │
        ▼
Update Critic Network
        │
        ▼
Clear Replay Buffer
        │
        ▼
Start Next Episode
```

This learning cycle continues for multiple episodes until the reinforcement learning policy converges towards an effective intrusion detection strategy.

# Training Module (`train/`)

The **train** folder is responsible for managing the reinforcement learning training process.

Although the current implementation performs training directly from `main.py`, this folder has been included to improve project organisation and future scalability.

As the project evolves, this directory can be expanded to include separate training scripts for different reinforcement learning algorithms, hyperparameter tuning experiments, checkpoint management, and model evaluation.

Keeping training logic separate from the main application makes the project easier to maintain and extend.

---

# Testing Module (`tests/`)

The **tests** folder contains scripts used to verify that different components of the project behave correctly.

Testing helps identify implementation errors before they affect the overall reinforcement learning process.

Although there is none code in it 

As additional features are introduced, this folder can be expanded with more comprehensive unit and integration tests.

---

# Utility Module (`utils/`)

The **utils** folder contains helper functions that support the rest of the project.

These functions are generally reusable and are kept separate from the core implementation to improve readability and reduce code duplication.

Depending on future development, this folder may include:

- Logging utilities.
- Model checkpoint saving.
- Performance evaluation functions.
- Graph generation.
- Dataset loading.
- Configuration helpers.

Separating utility functions from the learning algorithm keeps the project modular and easier to maintain.

---

# Main Training Script (`main.py`)

The `main.py` file serves as the entry point of the entire project.

It coordinates communication between the FANET simulation environment and the MAPPO learning algorithm.

Every training episode follows the same sequence of operations.

---

## Step 1 — Initialise the Environment

The simulation environment is created together with the MAPPO agent and replay buffer.

At this stage, the neural networks are initialised and all training variables are prepared before learning begins.

---

## Step 2 — Reset the FANET Environment

At the beginning of every episode, the environment is reset.

This creates a fresh network containing both legitimate drones and attacker drones positioned randomly within the simulated three-dimensional space.

Each drone begins with its own initial trust score, anomaly score and physical state.

---

## Step 3 — Generate Observations

Every drone observes its surrounding environment.

The observation vector generated for each drone contains information about its own physical state together with security-related features used for intrusion detection.

These observations become the inputs to the Actor neural network.

---

## Step 4 — Select Actions

Using the Actor network, each drone independently selects one of the available security actions:

- Trust
- Suspect
- Isolate

The selected actions represent the drone's local intrusion detection decisions.

---

## Step 5 — Execute Environment Step

The chosen actions are passed to the FANET environment.

The environment then performs several operations:

- Updates drone movement.
- Applies GPS spoofing attacks.
- Calculates anomaly scores.
- Updates trust values.
- Computes rewards.
- Generates the next state.

---

## Step 6 — Store Experiences

For every drone interaction, the following information is stored inside the Replay Buffer:

- Observation
- Selected action
- Action probability
- Reward

These experiences are collected throughout the episode before being used to update the learning policy.

---

## Step 7 — Update the MAPPO Policy

Once the episode has finished, all collected experiences are used to train both the Actor and Critic neural networks.

During this stage the algorithm:

- Computes discounted returns.
- Estimates state values.
- Calculates advantages.
- Updates the Actor.
- Updates the Critic.
- Clears the Replay Buffer.

This completes one reinforcement learning episode.

---

## Step 8 — Record Performance

Throughout training, several performance metrics are recorded.

These include:

- Episode reward.
- Smoothed reward.
- Critic loss.

These metrics provide insight into how well the learning process is progressing over time.

---

# Training Performance

The current implementation records two primary performance metrics throughout training.

---

## Episode Reward

Episode reward represents the cumulative reward received by all drone agents during one training episode.

An increasing reward generally indicates that the learning agents are making better intrusion detection decisions.

To reduce fluctuations caused by reinforcement learning exploration, a moving average reward is also calculated.

The moving average provides a clearer picture of the overall learning trend and makes convergence easier to observe.

---

## Critic Loss

The Critic Loss measures how accurately the Critic network predicts the expected future reward of each observed state.

Lower values generally indicate that the Critic has learned to estimate state values more accurately.

Temporary spikes in critic loss are common during reinforcement learning because the policy continuously changes as learning progresses.

---

# Understanding the Training Graphs

Two graphs are generated automatically after training.

---

## Reward Curve

The reward curve illustrates how the learning performance changes over multiple episodes.

The graph contains two curves.

The first curve represents the raw episode rewards, while the second curve represents the moving average reward.

The moving average smooths short-term fluctuations and makes long-term learning behaviour easier to interpret.

A stable reward curve generally indicates that the learning policy has converged towards a consistent decision-making strategy.

---

## Critic Loss Curve

The critic loss graph illustrates how the value estimation error changes during training.

Although occasional fluctuations are expected, the overall trend should remain reasonably stable.

Large temporary spikes do not necessarily indicate failure, as reinforcement learning naturally experiences periods of exploration and policy adjustment.

The critic loss should therefore be interpreted together with the reward curve rather than in isolation.

---

# Current Project Status

At the current stage of development, the project has successfully achieved the following milestones:

- A complete FANET simulation environment has been developed.
- GPS spoofing attacks have been successfully modelled.
- Decentralised MAPPO learning has been implemented.
- The Actor and Critic neural networks have been integrated.
- Reinforcement learning training has been successfully completed.
- Training performance can be visualised using reward and critic loss graphs.
- The project has been tested successfully on Windows before migration to Linux.

These milestones provide a stable foundation for future experimentation and large-scale evaluation.

---

# Future Work

Although the current implementation focuses on GPS spoofing attacks, several important extensions are planned.

Future improvements include:

- Integration of publicly available FANET intrusion detection datasets.
- Implementation of additional attacks such as DoS, Blackhole and Jamming.
- Cooperative trust fusion between neighbouring UAVs.
- Communication using realistic wireless network models.
- Evaluation under larger FANET topologies.
- Hyperparameter optimisation.
- Distributed multi-agent training on Linux.
- Performance comparison with existing intrusion detection approaches.

These improvements will enable a more comprehensive evaluation of the proposed intrusion detection framework.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/fe-cmd/FANET-MARL-IDS.git
```

Navigate into the project directory:

```bash
cd FANET-MARL-IDS
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

# Running the Project

To begin training, execute:

```bash
python main.py
```

The program will automatically:

- Initialise the FANET environment.
- Train the MAPPO agents.
- Display training progress.
- Generate reward and critic loss graphs after training completes.

---

# Future Dataset Integration

The current implementation trains agents using a simulated FANET environment developed specifically for this project.

In the next phase of development, publicly available FANET intrusion detection datasets will be incorporated to evaluate the trained model under more realistic network conditions.

Dataset integration will enable benchmarking against existing intrusion detection techniques and provide a more comprehensive assessment of the proposed MAPPO-based IDS.

---

# Author

This project was developed as part of ongoing research into the application of Multi-Agent Deep Reinforcement Learning for intrusion detection in Flying Ad Hoc Networks (FANETs).

The implementation is intended for academic research and future extension towards real-world UAV network security applications.