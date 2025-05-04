import { HealthStatus, MoviesResponse, ShapesData } from "../types/index";

const API_URL = "http://localhost:5001";

export const querykeys = {
	health: ["health"],
	shapes: ["shapes"],
	movies: (page: number, limit: number) => ["movies", page, limit],
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

	async getMovies(
		page: number = 1,
		limit: number = 50
	): Promise<MoviesResponse> {
		const response = await fetch(
			`${API_URL}/api/movies?page=${page}&limit=${limit}`
		);
		return response.json();
	},
};
