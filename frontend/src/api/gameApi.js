const BASE_URL = "http://127.0.0.1:8000";

export async function startGame(predictedWinner) {
  const res = await fetch(`${BASE_URL}/game/start?predicted_winner=${predictedWinner}`, {
    method: "POST"
  });
  return res.json();
}

export async function playRound(round) {
  const res = await fetch(`${BASE_URL}/game/round/${round}`, {
    method: "POST"
  });
  return res.json();
}

export async function getGameState() {
  const res = await fetch(`${BASE_URL}/game/state`);
  return res.json();
}

export async function resetGame() {
  const res = await fetch(`${BASE_URL}/game/reset`, {
    method: "POST"
  });
  return res.json();
}