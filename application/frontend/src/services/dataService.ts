import { Movie } from "../interfaces/Movie";
import moviesData from "../../fake-datas/movies.json";

export const getMovies = async (): Promise<Movie[]> => {
  return moviesData;
};
