import { TextInput } from "@mantine/core";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export function InputMovieRedirect() {
	const [movieId, setMovieId] = useState<string>("");
	const navigate = useNavigate();

	const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === "Enter" && movieId && !isNaN(Number(movieId))) {
			navigate(`/movies/${movieId}`);
		}
		setMovieId("");
	};

	return (
		<TextInput
			placeholder="ID du film"
			value={movieId}
			onChange={(e) => setMovieId(e.target.value)}
			onKeyDown={handleKeyDown}
		/>
	);
}
