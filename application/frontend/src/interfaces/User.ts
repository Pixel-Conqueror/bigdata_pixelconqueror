export interface Rating {
  movieId: number;
  rating: number;
}

export interface User {
  userId: number;
  ratings: Rating[];
}
