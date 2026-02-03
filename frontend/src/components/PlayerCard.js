function PlayerCard({ id, title, description, selected, onSelect }) {
  return (
    <div
      onClick={() => onSelect(id)}
      style={{
        border: selected ? "2px solid black" : "1px solid gray",
        padding: "10px",
        margin: "10px",
        cursor: "pointer"
      }}
    >
      <h3>Player {id}</h3>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}

export default PlayerCard;