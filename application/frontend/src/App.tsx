// import { useEffect, useState } from 'react';
// import { Movie } from "./interfaces/Movie";
// import { Link } from 'react-router-dom'
// import { getMovies } from './services/dataService';
import Home from './pages/Home';

function App() {
  // const [movies, setMovies] = useState<Movie[]>([]);

  // useEffect(() => {
  //   const fetchMovies = async () => {
  //     const data = await getMovies();
  //     setMovies(data);
  //   };
  //   fetchMovies();
  // }, []);

  // return (
  //   <div className="p-8">
  //     <h1 className="text-3xl font-bold mb-6">Liste des Films</h1>
  //     <div className="overflow-x-auto">
  //       <table className="min-w-full bg-white border border-gray-300">
  //         <thead>
  //           <tr>
  //             <th className="py-2 px-4 border-b">Movie ID</th>
  //             <th className="py-2 px-4 border-b">Title</th>
  //             <th className="py-2 px-4 border-b">Genre</th>
  //             <th className="py-2 px-4 border-b">Average Rating</th>
  //             <th className="py-2 px-4 border-b">Détail</th>
  //           </tr>
  //         </thead>
  //         <tbody>
  //           {movies.map((movie) => (
  //             <tr key={movie.movieId} className="hover:bg-gray-100">
  //               <td className="py-2 px-4 border-b text-center">{movie.movieId}</td>
  //               <td className="py-2 px-4 border-b">{movie.title}</td>
  //               <td className="py-2 px-4 border-b text-center">{movie.genres}</td>
  //               <td className="py-2 px-4 border-b text-center">{movie.averageRating}</td>
  //               <td className="py-2 px-4 border-b text-center">
  //                 <Link
  //                   to={`/movies/${movie.movieId}`}
  //                   className="text-blue-500 hover:underline"
  //                 >
  //                   Voir
  //                 </Link>
  //               </td>
  //             </tr>
  //           ))}
  //         </tbody>
  //       </table>
  //     </div>
  //   </div>
  // );
  return (
    <div style={{ backgroundColor: 'black' }}>
      <h1 style={{ color: 'white' }}>Recomovie </h1>
      <Home />
    </div>
  )
}

export default App;
