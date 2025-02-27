def normalize_state(state):
    # Normalize the state to a range of [0, 1]
    return state / 255.0

def define_action_space():
    # Define the action space for the game
    return {
        0: "NO_OP",
        1: "MOVE_LEFT",
        2: "MOVE_RIGHT",
        3: "MOVE_UP",
        4: "MOVE_DOWN"
    }