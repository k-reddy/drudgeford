import random 
import main
from game_loop import GameState

LOG_PATH = "ai_mode_condensed_log.txt"
wins = 0
exhausted = 0
losses = 0
other = 0
with open(LOG_PATH, 'w'):
    pass 
for i in range(20):
    num_players = random.choice([1,2,3])
    end_state = main.main(num_players)
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(f"End State: {end_state}, Num Players: {num_players} \n")
    if end_state == GameState.WIN:
        wins+=1
    elif end_state == GameState.EXHAUSTED:
        exhausted += 1
    elif end_state == GameState.GAME_OVER:
        losses += 1
    else:
        other+=1
with open(LOG_PATH, 'a') as log_file:
    log_file.write(f"END TALLYS \nWins: {wins}, Exhausted: {exhausted}, Losses: {losses}, Other: {other}")