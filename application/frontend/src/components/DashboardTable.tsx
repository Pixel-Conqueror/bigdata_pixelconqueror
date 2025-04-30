import { useState, useEffect } from "react";
import { Movie } from "../../fake-datas/movies.json";
import { getMovies } from "../services/dataService";
import "../styles/MoviesTable.css";

function MoviesTable() {
    const [movies, setMovies] = useState<Movie[]>([]);
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
    const [limit, setLimit] = useState<number>(10);
    const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
    const [minRating, setMinRating] = useState<number>(0);
    const [searchTerm, setSearchTerm] = useState<string>("");

    useEffect(() => {
        getMovies().then(setMovies);
    }, []);

    const allGenres = Array.from(new Set(movies.map((m) => m.genres)));

    const sortedMovies = [...movies]
        .sort((a, b) =>
            sortOrder === "asc"
                ? a.averageRating - b.averageRating
                : b.averageRating - a.averageRating
        )
        .slice(0, limit);

    const filteredMovies = sortedMovies.filter(
        (movie) =>
            (selectedGenres.length === 0 || selectedGenres.includes(movie.genres)) &&
            movie.averageRating >= minRating &&
            movie.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="table-container">
            <h1>Liste des films</h1>
            <div className="control-panel">
                <label htmlFor="sort">Tri :</label>
                <select
                    id="sort"
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value as "asc" | "desc")}
                >
                    <option value="desc">Note décroissante</option>
                    <option value="asc">Note croissante</option>
                </select>

                <label htmlFor="limit">Nombre affiché :</label>
                <select
                    id="limit"
                    value={limit}
                    onChange={(e) => setLimit(Number(e.target.value))}
                >
                    <option value={5}>5 films</option>
                    <option value={10}>10 films</option>
                    <option value={20}>20 films</option>
                    <option value={movies.length}>Tous</option>
                </select>

                <label htmlFor="minRating">Note min. :</label>
                <input
                    id="minRating"
                    type="number"
                    min={0}
                    max={5}
                    step={0.1}
                    value={minRating}
                    onChange={(e) => setMinRating(Number(e.target.value))}
                />

                <label htmlFor="search">Recherche :</label>
                <input
                    id="search"
                    type="text"
                    placeholder="Rechercher un titre"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            <div className="genre-filter">
                <label>Genres :</label>
                {allGenres.map((genre) => (
                    <label key={genre} style={{ marginRight: "1rem" }}>
                        <input
                            type="checkbox"
                            value={genre}
                            checked={selectedGenres.includes(genre)}
                            onChange={(e) => {
                                const value = e.target.value;
                                setSelectedGenres((prev) =>
                                    prev.includes(value)
                                        ? prev.filter((g) => g !== value)
                                        : [...prev, value]
                                );
                            }}
                        />
                        {genre}
                    </label>
                ))}
            </div>

            <table className="table">
                <thead>
                    <tr>
                        <th>Movie ID</th>
                        <th>Titre</th>
                        <th>Genre</th>
                        <th>Note moyenne</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredMovies.map((movie) => (
                        <tr key={movie.movieId}>
                            <td>{movie.movieId}</td>
                            <td>{movie.title}</td>
                            <td>{movie.genres}</td>
                            <td>{movie.averageRating}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default MoviesTable;

