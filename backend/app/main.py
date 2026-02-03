from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.game.engine import GameEngine

app = FastAPI(title="Last Model Standing")

# -------------------------------------------------
# CORS CONFIG (Frontend ↔ Backend)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Game Engine (single in-memory instance)
# -------------------------------------------------
game_engine = GameEngine()

# -------------------------------------------------
# GAME LIFECYCLE ENDPOINTS
# -------------------------------------------------

@app.post("/game/start")
def start_game(predicted_winner: str):
    """
    Initialize a new game.
    """
    game_engine.start_new_game(predicted_winner)
    return {"message": "Game started"}


@app.post("/game/reset")
def reset_game():
    """
    Reset the current game.
    """
    game_engine.reset()
    return {"message": "Game reset"}


@app.get("/game/state")
def get_state():
    """
    Get the full current game state.
    """
    return game_engine.get_state()

# -------------------------------------------------
# ROUND CONTROL (STEP-BY-STEP MODE)
# -------------------------------------------------

@app.post("/game/round/{round_number}/start")
def start_round(round_number: int):
    """
    Start a new round and calculate turn order.
    """
    return game_engine.start_round(round_number)


@app.post("/game/round/next-move")
def next_move():
    """
    Execute exactly ONE player move.
    Called repeatedly by the frontend until round_complete = True.
    """
    return game_engine.play_next_move()
