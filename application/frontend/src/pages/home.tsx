import { Card, Grid, Pagination, Table, Title } from "@mantine/core";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { StatsGroup } from "../components/generics/stats/stats";
import { apiService, querykeys } from "../services/api_service";

const LIMIT = 50;

export const Home = () => {
	const [currentPage, setCurrentPage] = useState(1);

	const { data: shapesData } = useQuery({
		queryKey: querykeys.shapes,
		queryFn: apiService.getShape,
	});

	const { data: moviesData } = useQuery({
		queryKey: querykeys.movies(currentPage, LIMIT),
		queryFn: () => apiService.getMovies(currentPage, LIMIT),
		placeholderData: keepPreviousData,
	});

	const handlePageChange = (page: number) => setCurrentPage(page);

	const pagination = moviesData?.total_pages && (
		<Pagination
			total={moviesData?.total_pages}
			value={currentPage}
			onChange={handlePageChange}
			mt="md"
		/>
	);

	return (
		<Grid>
			<Grid.Col span={12}>
				<StatsGroup stats={shapesData!} />
			</Grid.Col>

			<Grid.Col span={12}>
				<Card withBorder>
					<Title order={2}>Films</Title>
					{pagination}
					<Table>
						<thead>
							<tr>
								<th>Titre</th>
								<th>Genres</th>
							</tr>
						</thead>
						<tbody>
							{moviesData?.movies.map((movie) => (
								<tr key={movie.movieId}>
									<td>{movie.title}</td>
									<td>{movie.genres.join(", ")}</td>
								</tr>
							))}
						</tbody>
					</Table>
					{pagination}
				</Card>
			</Grid.Col>
		</Grid>
	);
};
