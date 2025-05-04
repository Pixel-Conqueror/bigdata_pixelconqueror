import { LoadingOverlay } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import {
	QueryClient,
	QueryClientProvider,
	useIsFetching,
	useIsMutating,
} from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { BaseLayout } from "../layouts/_base_layout";
import DefaultLayout from "../layouts/default_layout";
import { Home } from "../pages/home";
import { MovieDetails } from "../pages/movie_details";
import { UserDetails } from "../pages/user_details";
import { apiService, querykeys } from "../services/api_service";

const query_client = new QueryClient({
	defaultOptions: {
		queries: {
			staleTime: 1000 * 60 * 5,
			gcTime: 1000 * 60 * 10,
		},
	},
});

const router = createBrowserRouter([
	{
		path: "/",
		element: <DefaultLayout />,
		children: [
			{
				index: true,
				element: <Home />,
				loader: () =>
					Promise.all([
						query_client.prefetchQuery({
							queryKey: querykeys.health,
							queryFn: apiService.getHealth,
						}),
						query_client.prefetchQuery({
							queryKey: querykeys.shapes,
							queryFn: apiService.getShape,
						}),
						query_client.prefetchQuery({
							queryKey: querykeys.movies(1, 50),
							queryFn: () => apiService.getMovies({ page: 1 }),
						}),
					]),
			},
			{
				path: "/movies/:movieId",
				element: <MovieDetails />,
				loader: ({ params }) => {
					const movieId = params.movieId;
					if (!movieId) {
						throw new Error("Movie ID is required");
					}
					return apiService.getMovieDetails(Number(movieId));
				},
			},
			{
				path: "/users/:userId",
				element: <UserDetails />,
				loader: ({ params }) => {
					const userId = params.userId;
					if (!userId) {
						throw new Error("User ID is required");
					}
					return apiService.getUserDetails({
						userId: Number(userId),
						page: 1,
					});
				},
			},
		],
	},
]);

const GlobalLoader = () => {
	const isFetching = useIsFetching();
	const isMutating = useIsMutating();
	const isLoading = isFetching > 0 || isMutating > 0;

	return <LoadingOverlay visible={isLoading} overlayProps={{ blur: 2 }} />;
};

export const AppRouter = () => (
	<BaseLayout>
		<QueryClientProvider client={query_client}>
			<Notifications position="top-right" />
			<GlobalLoader />
			<RouterProvider router={router} />
		</QueryClientProvider>
	</BaseLayout>
);
