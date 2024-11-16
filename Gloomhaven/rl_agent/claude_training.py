import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque, namedtuple
import random
from backend.models.action_model import ActionCard

Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )

    def forward(self, x):
        return self.network(x)

class RLAgent(Agent):
    def __init__(self, state_size, action_size, device='cpu'):
        self.state_size = state_size
        self.action_size = action_size
        self.device = device
        
        # DQN hyperparameters
        self.gamma = 0.99
        self.learning_rate = 1e-3
        self.batch_size = 64
        self.memory_size = 10000
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # Initialize networks and optimizer
        self.policy_net = DQN(state_size, action_size).to(device)
        self.target_net = DQN(state_size, action_size).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        
        # Replay memory
        self.memory = deque(maxlen=self.memory_size)

    def get_state(self, board, char):
        # Extract state information
        agent_loc = board.find_location_of_target(char)
        
        # Get teammate and opponent locations
        teammates = []
        opponents = []
        for character in board.characters:
            if character.team == char.team and character != char:
                teammates.append(board.find_location_of_target(character))
            else:
                opponents.append(board.find_location_of_target(character))
        
        # Flatten locations and add health information
        state = [
            agent_loc[0], agent_loc[1],
            char.health
        ]
        
        # Add teammate information
        for loc in teammates:
            state.extend([loc[0], loc[1]])
        
        # Add opponent information
        for loc in opponents:
            state.extend([loc[0], loc[1]])
            
        return torch.FloatTensor(state).to(self.device)

    def select_action(self, state, available_actions):
        if random.random() < self.epsilon:
            return random.choice(available_actions)
        
        with torch.no_grad():
            state = state.unsqueeze(0)
            action_values = self.policy_net(state)
            return available_actions[torch.argmax(action_values).item()]

    def store_experience(self, state, action, reward, next_state, done):
        self.memory.append(Experience(state, action, reward, next_state, done))

    def learn(self):
        if len(self.memory) < self.batch_size:
            return

        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        # Convert to tensors
        states = torch.stack(states)
        next_states = torch.stack(next_states)
        rewards = torch.FloatTensor(rewards).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Compute Q values
        current_q_values = self.policy_net(states)
        next_q_values = self.target_net(next_states).detach()

        # Compute target Q values
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values.max(1)[0]

        # Compute loss
        loss = nn.MSELoss()(current_q_values, target_q_values.unsqueeze(1))

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

    @staticmethod
    def select_action_card(disp, available_action_cards):
        # Implementation using the trained policy
        state = self.get_state(disp.board, disp.current_character)
        return self.select_action(state, available_action_cards)

    @staticmethod
    def decide_if_move_first(disp):
        # Could be trained as a separate policy or use simple heuristic
        return True

    @staticmethod
    def select_attack_target(disp, in_range_opponents, board, char):
        # Similar to Ai class implementation for now
        shortest_dist = 1000
        nearest_opponent = None
        attacker_location = board.find_location_of_target(char)
        
        for opponent in in_range_opponents:
            opponent_location = board.find_location_of_target(opponent)
            opponent_dist = len(board.get_shortest_valid_path(attacker_location, opponent_location))
            if opponent_dist < shortest_dist:
                nearest_opponent = opponent
                shortest_dist = opponent_dist
        return nearest_opponent

    @staticmethod
    def perform_movement(char, movement, is_jump, board):
        # Similar to Ai class implementation for now
        targets = board.find_opponents(char)
        target = RLAgent.select_attack_target(None, targets, board, char)
        target_loc = board.find_location_of_target(target)
        board.move_character_toward_location(char, target_loc, movement, is_jump)