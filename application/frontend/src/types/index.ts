export type HealthStatus = {
	db_status: {
		ok: boolean;
	};
	status: string;
};

export type ShapesData = {
	genres: string[];
	total_movies: number;
	total_users: number;
	total_ratings: number;
};

export type Review = {
	rating: number;
	userId: number;
	username: string;
};

export type Movie = {
	movieId: number;
	title: string;
	genres: string[];
	avg_rating: number | null;
	total_ratings: number;
	rating_distribution: Record<string, number> | null;
	top_reviews: Review[];
	worst_reviews: Review[];
};

export type MovieLight = {
	genres: string[];
	movieId: number;
	title: string;
};

export type MoviesResponse = {
	has_next: boolean;
	has_prev: boolean;
	movies: Movie[];
	page: number;
	page_size: number;
	total_movies: number;
	total_pages: number;
};

export type UserRating = {
	movieId: number;
	title: string;
	genres: string[];
	rating: number;
	timestamp: string;
};

export type UserRecommendation = {
	movieId: number;
	title: string;
	genres: string[];
};

export type UserDetails = {
	userId: number;
	username: string;
	total_ratings: number;
	ratings_page: number;
	ratings_total_pages: number;
	has_next: boolean;
	has_prev: boolean;
	ratings: UserRating[];
	recommendations: UserRecommendation[];
};
