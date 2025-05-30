import {
	HealthStatus,
	Movie,
	MoviesResponse,
	ShapesData,
	UserDetails,
} from "../types/index";

const API_URL = "http://localhost:5001";
const LIMIT = 50;

interface GetMoviesParams {
	page: number;
	title?: string;
	genre?: string;
}

export interface UserRating {
	movieId: number;
	title: string;
	genres: string[];
	rating: number;
	timestamp: string;
}

export interface UserRecommendation {
	movieId: number;
	title: string;
	genres: string[];
}

export const querykeys = {
	health: ["health"],
	shapes: ["shapes"],
	movies: (
		page: number,
		limit: number,
		searchQuery?: string,
		selectedGender?: string | null
	) => ["movies", page, limit, searchQuery, selectedGender],
	movieDetails: (movieId: number) => ["movie", movieId],
	userDetails: (userId: number, page: number) => ["user", userId, page],
};

export const apiService = {
	async getHealth(): Promise<HealthStatus> {
		const response = await fetch(`${API_URL}/api/health`);
		return response.json();
	},

	async getShape(): Promise<ShapesData> {
		const response = await fetch(`${API_URL}/api/shape`);
		return response.json();
	},

	async getMovies({
		page,
		title,
		genre,
	}: GetMoviesParams): Promise<MoviesResponse> {
		const url = this.urlBuilder({
			page,
			title,
			genre,
		});
		const response = await fetch(url);
		return response.json();
	},

	async getMovieDetails(movieId: number): Promise<Movie> {
		const response = await fetch(`${API_URL}/api/movies/${movieId}`);
		return response.json();
	},

	async getUserDetails({
		userId,
		page,
	}: {
		userId: number;
		page: number;
	}): Promise<UserDetails> {
		const response = await fetch(
			`${API_URL}/api/users/${userId}?page=${page}&limit=${LIMIT}`
		);
		return response.json();
	},

	urlBuilder({ page, title, genre }: GetMoviesParams): string {
		const params = new URLSearchParams();
		params.set("page", page.toString());
		params.set("limit", LIMIT.toString());

		if (title && genre) {
			throw new Error("title and genre cannot be used together");
		}

		if (title) {
			params.set("title", title);
		}

		if (genre) {
			params.set("genre", genre);
		}

		return `${API_URL}/api/movies?${params.toString()}`;
	},
};
