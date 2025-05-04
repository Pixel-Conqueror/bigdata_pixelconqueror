import {
	Badge,
	Grid,
	Group,
	Rating,
	RatingProps,
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
			.sort((a, b) => Number(b[1]) - Number(a[1]))
			.map(([rating, count]) => [
				<Rating value={Number(rating)} {...commonRatingProps} />,
				count,
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
						<Table data={ratingData} />
					) : (
						<Text>Aucune distribution de notes disponible</Text>
					)}
				</Grid.Col>
				<Grid.Col span={2}>
					{movie.top_reviews.length > 0 ? (
						<Table data={topReviewsData} />
					) : (
						<Text>Aucune note disponible</Text>
					)}
				</Grid.Col>
				<Grid.Col span={2}>
					{movie.worst_reviews.length > 0 ? (
						<Table data={worstReviewsData} />
					) : (
						<Text>Aucune note disponible</Text>
					)}
				</Grid.Col>
			</Grid>
		</>
	);
};
