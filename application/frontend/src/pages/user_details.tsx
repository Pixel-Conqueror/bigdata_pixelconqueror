import {
	Badge,
	Card,
	Group,
	Pagination,
	Rating,
	Table,
	TableData,
	Text,
	Title,
} from "@mantine/core";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import { InternalLink } from "../components/generics/internal_link";
import { getCommonTableProps } from "../lib/table";
import { apiService, querykeys } from "../services/api_service";
export const UserDetails = () => {
	const { userId } = useParams<{ userId: string }>();
	const [currentPage, setCurrentPage] = useState(1);

	const { data: user } = useQuery({
		queryKey: querykeys.userDetails(Number(userId), currentPage),
		queryFn: () =>
			apiService.getUserDetails({
				userId: Number(userId),
				page: currentPage,
			}),
		placeholderData: keepPreviousData,
	});

	if (!user) return null;

	const handlePageChange = (page: number) => setCurrentPage(page);

	const notesData: TableData = {
		caption: "Notes",
		head: ["Film", "Genres", "Note", "Date"],
		body: user.ratings.map((rating) => [
			<InternalLink to={`/movies/${rating.movieId}`}>
				{rating.title}
			</InternalLink>,
			<Rating value={rating.rating} readOnly />,
			<Text>{new Date(rating.timestamp).toLocaleDateString("fr-FR")}</Text>,
		]),
		...getCommonTableProps(),
	};

	const recommendationsData: TableData = {
		caption: "Recommandations",
		head: ["Film", "Genres"],
		body: user.recommendations.map((movie) => [
			<InternalLink to={`/movies/${movie.movieId}`}>
				{movie.title}
			</InternalLink>,
			<Group gap="xs">
				{movie.genres.map((genre) => (
					<Badge key={genre}>{genre}</Badge>
				))}
			</Group>,
		]),
		...getCommonTableProps(),
	};

	const tableNotesHeader = (
		<Pagination
			total={Math.ceil(user?.total_ratings / 50) ?? 0}
			value={currentPage}
			onChange={handlePageChange}
		/>
	);

	const tableRecommendationsHeader = (
		<Pagination
			total={Math.ceil(user?.recommendations.length / 50) ?? 0}
			value={currentPage}
			onChange={handlePageChange}
		/>
	);

	return (
		<>
			<Title order={2}>{user.username}</Title>
			<Text mb="md">Nombre total de notes: {user.total_ratings}</Text>

			<Card withBorder mb="md">
				<Group justify="space-between" mb="md">
					<Title order={3}>Notes récentes</Title>
					{tableNotesHeader}
				</Group>
				<Table data={notesData} />
				<Group justify="flex-end">{tableNotesHeader}</Group>
			</Card>

			<Card withBorder>
				<Group justify="space-between" mb="md">
					<Title order={3}>Recommandations</Title>
					{tableRecommendationsHeader}
				</Group>
				<Table data={recommendationsData} />
				<Group justify="flex-end">{tableRecommendationsHeader}</Group>
			</Card>
		</>
	);
};
