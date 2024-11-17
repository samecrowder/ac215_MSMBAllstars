interface PlayerCardProps {
  id: string;
  name: string;
  age: number;
  country: string;
  height: string;
  weight: string;
  imageUrl: string;
  gradientFrom?: string;
  gradientTo?: string;
}

export function PlayerCard({
  name,
  age,
  country,
  height,
  weight,
  imageUrl,
  gradientFrom = "#ffffff",
  gradientTo = "#f3f4f6",
}: PlayerCardProps) {
  return (
    <div className="border p-4 rounded-lg w-80">
      <img
        src={imageUrl}
        alt={`${name}`}
        className="w-full h-48 object-contain rounded-lg mb-4"
        style={{
          background: `linear-gradient(to bottom, ${gradientFrom}, ${gradientTo})`,
        }}
      />
      <h1 className="font-bold">{name}</h1>
      <p>Age: {age}</p>
      <p>Country: {country}</p>
      <p>Height: {height}</p>
      <p>Weight: {weight}</p>
    </div>
  );
}
