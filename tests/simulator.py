import pandas as pd
import random
from .. import backend_main

# setup variables
LOG_PATH = "ai_mode_condensed_log.txt"
game_data = []
NUM_GAMES = 1000

# run simulation and gather data
for i in range(NUM_GAMES):
    if i % 10 == 0:
        print(f"Running game {i}/{NUM_GAMES}")
    num_players = random.choice([1, 2, 3])
    end_state = backend_main.main(num_players, all_ai_mode=True)
    game_data.append({"end_state": end_state, "num_players": num_players})

# convert data to a dataframe and create summary statistics
game_df = pd.DataFrame(game_data)
game_df["end_state"] = game_df["end_state"].astype(str)
summarized_df = (
    game_df.groupby(["num_players", "end_state"]).size().unstack(fill_value=0)
)
percentage_df = summarized_df.div(summarized_df.sum(axis=1), axis=0) * 100

# write summary statistics to a log file
with open(LOG_PATH, "w") as log_file:
    log_file.write("Summarized Game Data: \n" + summarized_df.to_string() + "\n")
    log_file.write("Percentage Game Data: \n" + percentage_df.to_string())
    log_file.write("\n\n Individual Game Data: \n" + game_df.to_string() + "\n")
