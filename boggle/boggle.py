# import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
import PySimpleGUIWx as sg
# import PySimpleGUIQt as sg
import enchant


def setup_board():
  # fill board with letters
  # ensure there's enough vowels
  # and common letters
  board = [['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']]
  return board



def evaluate_guess():
  # is guess on board?
  # is guess a word?
  return


def check_if_valid(current_position, last_position):
  if last_position[0] is None:
    return True
  max_dist = max(abs(a - b) for a, b in zip(current_position, last_position))
  return max_dist <= 1


def check_if_in_dictionary(word):
  d = enchant.Dict("en_US")
  return d.check(word)


def event_loop(window, board):
  word = ""
  words = []
  old_row, old_col = None, None
  while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
      break
    if event == "End_word":
      print(word)
      if not check_if_in_dictionary(word):
        print("Not a valid word!")
      else:
        print(f"nice find: {word}")
        words.append(word)
      word = ""
      old_row, old_col = None, None

    else:
      row, col = event
      is_valid_move = check_if_valid((row,col), (old_row, old_col))
      if is_valid_move:
        letter = board[row][col]
        old_row, old_col = row, col
        word += letter
        print(f"You clicked: {event}{letter}")
      else:
        print("That's an invalid move. Try again!")
  window.close()
  return words


def main():
  print("yup")
  board = setup_board()
  buttons = [[
      sg.Button(letter, key=(row_num, column_num))
      for column_num, letter in enumerate(row)
  ] for row_num, row in enumerate(board)]
  layout = buttons.append([sg.Button("Finish Word", key="End_word")])
  window = sg.Window("Try", buttons)

  event_loop(window, board)


main()
# check_if_valid((5, 5), (5, 1))
