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
	avg_rating: number;
	genres: string[];
	movieId: number;
	rating_distribution: Record<string, number>;
	title: string;
	top_reviews: Review[];
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
