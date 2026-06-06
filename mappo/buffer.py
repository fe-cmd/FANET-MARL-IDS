class ReplayBuffer:

    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []

    def store(self, state, action, log_prob, reward):
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)

    def clear(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []