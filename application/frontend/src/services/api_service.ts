import { HealthStatus, MoviesResponse, ShapesData } from "../types/index";

const API_URL = "http://localhost:5001";
const LIMIT = 50;

interface GetMoviesParams {
	page: number;
	title?: string;
	genre?: string;
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
