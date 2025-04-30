import React, { useEffect, useState } from 'react';
import MovieRow from '../components/MovieRow';
import '../index.css'
import '../styles/Home.css'
import { fetchTrendingMovies, fetchMoviesByGenre } from '../services/tmdb';
import MoviesTable from '../components/DashboardTable';


const Home: React.FC = () => {
    const [trending, setTrending] = useState([]);
    const [actionMovies, setActionMovies] = useState([]);
    const [comedyMovies, setComedyMovies] = useState([]);

    useEffect(() => {
        (async () => {
            setTrending(await fetchTrendingMovies());
            setActionMovies(await fetchMoviesByGenre(28));
            setComedyMovies(await fetchMoviesByGenre(35));
        })();
    }, []);

    return (
        <div className='movie-category'>
            <MovieRow title="Notre sélection" movies={trending} />
            <MovieRow title="Films d'action" movies={actionMovies} />
            <MovieRow title="Comédies" movies={comedyMovies} />

            <MoviesTable></MoviesTable>
        </div>

    );
};

export default Home;
