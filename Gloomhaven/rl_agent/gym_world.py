from typing import Optional
import numpy as np
import gymnasium as gym

class GymWorld(gym.Env):
    # !!! need to add healths
    def __init__(self, agent_location, teammate_locations, opponent_locations, agent_action_cards):
        
        
