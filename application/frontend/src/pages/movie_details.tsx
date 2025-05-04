import { BarChart } from "@mantine/charts";
import {
	Badge,
	Group,
	Rating,
	RatingProps,
	SimpleGrid,
	Table,
	TableData,
	Text,
	Title,
} from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { InternalLink } from "../components/generics/internal_link";
import { getCommonTableProps } from "../lib/table";
import { apiService, querykeys } from "../services/api_service";

export const MovieDetails = () => {
	const { movieId } = useParams<{ movieId: string }>();
	const { data: movie } = useQuery({
		queryKey: querykeys.movieDetails(Number(movieId)),
		queryFn: () => apiService.getMovieDetails(Number(movieId)),
	});

	if (!movie) return null;

	const commonRatingProps: RatingProps = {
		readOnly: true,
		fractions: 2,
	};
	const ratingData: TableData = {
		caption: "Distribution des notes",
		head: ["Note", "Nombre"],
		body: Object.entries(movie.rating_distribution ?? {})
			.sort((a, b) => Number(b[0]) - Number(a[0]))
			.map(([rating, count]) => [
				<Rating value={Number(rating)} {...commonRatingProps} />,
				<Group gap={4}>
					{count}{" "}
					<Text c="dimmed">
						({Math.round((Number(count) / movie.total_ratings) * 100)}%)
					</Text>
				</Group>,
			]),
		...getCommonTableProps(),
	};

	const topReviewsData: TableData = {
		caption: "Meilleures notes",
		head: ["Utilisateur", "Note"],
		body: movie.top_reviews.map((review) => [
			<InternalLink to={`/users/${review.userId}`}>
				{review.username}
			</InternalLink>,
			<Rating value={review.rating} {...commonRatingProps} />,
		]),
		...getCommonTableProps(),
	};

	const worstReviewsData: TableData = {
		caption: "Pires notes",
		head: ["Utilisateur", "Note"],
		body: movie.worst_reviews.map((review) => [
			<InternalLink to={`/users/${review.userId}`}>
				{review.username}
			</InternalLink>,
			<Rating value={review.rating} {...commonRatingProps} />,
		]),
		...getCommonTableProps(),
	};

	const chartData = movie.rating_distribution
		? Object.entries(movie.rating_distribution)
				.map(([rating, count]) => ({
					rating: Number(rating),
					count,
					percentage: Math.round((Number(count) / movie.total_ratings) * 100),
					color: `blue.3`,
				}))
				.sort((a, b) => a.rating - b.rating)
		: [];

	return (
		<>
			<Title order={2} mb="md">
				{movie.title}
			</Title>

			<Group align="center" gap="xs">
				<Text>Genres:</Text>
				{movie.genres.map((genre) => (
					<Badge key={genre}>{genre}</Badge>
				))}
			</Group>
			<Text mb="md">
				Note moyenne: {movie.avg_rating} ({movie.total_ratings} votes)
			</Text>

			<Title order={3} mb="md">
				Distribution des notes
			</Title>
			<SimpleGrid cols={2}>
				{movie.rating_distribution ? (
					<Table data={ratingData} />
				) : (
					<Text>Aucune distribution de notes disponible</Text>
				)}
				{movie.rating_distribution && (
					<BarChart
						data={chartData}
						dataKey="rating"
						series={[
							{ name: "count", label: "Nombre de votes", color: "blue.6" },
						]}
						tickLine="y"
						gridAxis="xy"
						valueFormatter={(value: number) => `${value}%`}
						xAxisLabel="Note"
						yAxisLabel="Nombre de votes"
					/>
				)}
			</SimpleGrid>

			<Title order={3} mt="md" mb="md">
				Détails des notes
			</Title>
			<SimpleGrid cols={2}>
				{movie.top_reviews.length > 0 ? (
					<Table data={topReviewsData} />
				) : (
					<Text>Aucune note disponible</Text>
				)}
				{movie.worst_reviews.length > 0 ? (
					<Table data={worstReviewsData} />
				) : (
					<Text>Aucune note disponible</Text>
				)}
			</SimpleGrid>
		</>
	);
};
