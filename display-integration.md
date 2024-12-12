## Integrating Pyxel Front End with Gloomhaven

### Initializing

Pyxel waits for initial map, terrain, and character positions until it initializes the canvas. Bonus if we can have a "Waiting for game to start" or whatever message while it waits.

### Where Gloomhaven updates display.

We run `display.reload_display()` on any change to `terrain`, `location`, and `characters`, but this shouldn't be necessary to pass to pyxel.

Initially we'll have to send initial map to pyxel before it can create canvas and initialize map.

We'll need a way to have the `CharacterType` result in a string that's callable from the sprite list. Default to something.

Looks like we'll just have to adapt `Board.update_character_location`, as long as this will be one move at a time, which it seems like it is from `Board.move_character_toward_location`.

### How do we communicate non-board moves to Pyxel?

We can either expand the current message queue to accept different types of tasks, not just board actions, or create a separate queue just for system concerns.

As long as we don't need concurrent actions or system actions, I think we should expand the current queue to be more flexible.

We currently have one task type that's added to the message queue:

```python
ActionTask: {
    character: str,
    animation_type: str,
    direction: Direction,
    from_grid_pos: tuple,
    to_grid_pos: tuple,
    duration_ms: int = 1000,
    action_steps: probably going to deprecate,
}
```

I feel we could create a `LogTask` and a `BoardInitTask` dataclass and have the queue be able to handle all 3.

We'll need an `is_board_initialized` flag to raise if there are any tasks received before board init.

Should rename `PyxelActionQueue` to `PyxelTaskQueue`
