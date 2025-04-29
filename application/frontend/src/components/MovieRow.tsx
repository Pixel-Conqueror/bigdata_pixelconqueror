import React from 'react';
import { getImageUrl } from '../services/tmdb';
import '../index.css'
import '..//styles/MovieRow.css'

type Movie = {
    id: number;
    title: string;
    poster_path: string;
};

interface Props {
    title: string;
    movies: Movie[];
}

const MovieRow: React.FC<Props> = ({ title, movies }) => {
    return (
        <div>
            <h2 className='h2-title'>{title}</h2>
            <div className="row-wrapper">

                <div className='row'>
                    {movies.map((movie) => (
                        <img
                            key={movie.id}
                            src={getImageUrl(movie.poster_path)}
                            alt={movie.title}
                            style={{ width: '150px', marginRight: '10px' }}
                            className='movie-poster'
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default MovieRow;
