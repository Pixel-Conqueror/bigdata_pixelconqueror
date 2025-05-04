import {
	Badge,
	Grid,
	Group,
	Rating,
	Table,
	TableData,
	TableProps,
	Text,
	Title,
} from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { apiService, querykeys } from "../services/api_service";

export const MovieDetails = () => {
	const { movieId } = useParams<{ movieId: string }>();
	const { data: movie } = useQuery({
		queryKey: querykeys.movieDetails(Number(movieId)),
		queryFn: () => apiService.getMovieDetails(Number(movieId)),
	});

	if (!movie) return null;

	const ratingData: TableData = {
		caption: "Distribution des notes",
		head: ["Note", "Nombre"],
		body: Object.entries(movie.rating_distribution ?? {})
			.sort((a, b) => Number(b[1]) - Number(a[1]))
			.map(([rating, count]) => [
				<Rating value={Number(rating)} readOnly />,
				count,
			]),
	};

	const topReviewsData: TableData = {
		caption: "Meilleures notes",
		head: ["Utilisateur", "Note"],
		body: movie.top_reviews.map((review) => [
			review.username,
			<Rating value={review.rating} readOnly />,
		]),
	};

	const worstReviewsData: TableData = {
		caption: "Pires notes",
		head: ["Utilisateur", "Note"],
		body: movie.worst_reviews.map((review) => [
			review.username,
			<Rating value={review.rating} readOnly />,
		]),
	};

	const commonProps: TableProps = {
		striped: true,
		highlightOnHover: true,
		withTableBorder: true,
		withColumnBorders: true,
		verticalSpacing: "sm",
		styles: {
			table: {
				borderRadius: "var(--mantine-radius-md)",
			},
		},
	};

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

			<Grid grow>
				<Grid.Col span={1}>
					{movie.rating_distribution ? (
						<Table data={ratingData} {...commonProps} />
					) : (
						<Text>Aucune distribution de notes disponible</Text>
					)}
				</Grid.Col>
				<Grid.Col span={2}>
					{movie.top_reviews.length > 0 ? (
						<Table data={topReviewsData} {...commonProps} />
					) : (
						<Text>Aucune note disponible</Text>
					)}
				</Grid.Col>
				<Grid.Col span={2}>
					{movie.worst_reviews.length > 0 ? (
						<Table data={worstReviewsData} {...commonProps} />
					) : (
						<Text>Aucune note disponible</Text>
					)}
				</Grid.Col>
			</Grid>
		</>
	);
};
