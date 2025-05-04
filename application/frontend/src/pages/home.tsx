import {
	Button,
	Card,
	Group,
	Pagination,
	Stack,
	Table,
	Title,
} from "@mantine/core";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { GenderFilter } from "../components/gender_filter";
import { StatsGroup } from "../components/generics/stats/stats";
import { SearchBar } from "../components/search_bar";
import { useDebounceState } from "../hooks/use_debounce_state";
import { apiService, querykeys } from "../services/api_service";

const LIMIT = 50;

export const Home = () => {
	const [currentPage, setCurrentPage] = useState(1);
	const {
		storedValue: searchQuery,
		debouncedValue: debouncedSearchQuery,
		setStoredValue: setSearchQuery,
	} = useDebounceState<string>("");
	const {
		storedValue: selectedGender,
		debouncedValue: debouncedSelectedGender,
		setStoredValue: setSelectedGender,
	} = useDebounceState<string | null>(null);

	const { data: shapesData } = useQuery({
		queryKey: querykeys.shapes,
		queryFn: apiService.getShape,
	});

	const { data: moviesData } = useQuery({
		queryKey: querykeys.movies(
			currentPage,
			LIMIT,
			debouncedSearchQuery,
			debouncedSelectedGender
		),
		queryFn: () =>
			apiService.getMovies({
				page: currentPage,
				title: debouncedSearchQuery,
				genre: debouncedSelectedGender ?? undefined,
			}),
		placeholderData: keepPreviousData,
	});

	const handlePageChange = (page: number) => setCurrentPage(page);
	const resetPage = () => setCurrentPage(1);
	const reset = () => {
		resetPage();
		setSearchQuery("");
		setSelectedGender(null);
	};

	const handleGenderChange = (gender: string | null) => {
		setSelectedGender(gender);
		setSearchQuery("");
		resetPage();
	};

	const handleSearchChange = (query: string) => {
		setSearchQuery(query);
		setSelectedGender(null);
		resetPage();
	};

	const tableHeader = (
		<Group justify="space-between">
			<Group>
				<SearchBar searchQuery={searchQuery} onChange={handleSearchChange} />
				{shapesData && (
					<GenderFilter
						genders={shapesData?.genres ?? []}
						selectedGender={selectedGender}
						onChange={handleGenderChange}
					/>
				)}
				<Button variant="light" color="red" onClick={reset}>
					Reset
				</Button>
			</Group>
			<Pagination
				total={moviesData?.total_pages ?? 0}
				value={currentPage}
				onChange={handlePageChange}
			/>
		</Group>
	);

	return (
		<Stack>
			<StatsGroup stats={shapesData!} />
			<Card withBorder>
				<Title order={2} mb="sm">
					Films
				</Title>
				{tableHeader}
				<Table mt="md" mb="md">
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
						{moviesData?.movies.length === 0 && (
							<tr>
								<td colSpan={2} align="center">
									No movies found
								</td>
							</tr>
						)}
					</tbody>
				</Table>
				{tableHeader}
			</Card>
		</Stack>
	);
};
