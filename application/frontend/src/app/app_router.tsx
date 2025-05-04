import { LoadingOverlay } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import {
	QueryClient,
	QueryClientProvider,
	useIsFetching,
	useIsMutating,
} from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { BaseLayout } from "../layouts/_base_layout";
import DefaultLayout from "../layouts/default_layout";
import { Home } from "../pages/home";
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
				loader: async () => {
					await Promise.all([
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
							queryFn: () => apiService.getMovies(1, 50),
						}),
					]);
					return null;
				},
			},
		],
	},
]);

const GlobalLoader = () => {
	const [initialized, setInitialized] = useState(false);
	const isFetching = useIsFetching();
	const isMutating = useIsMutating();

	const isLoading = isFetching > 0 || isMutating > 0;
	useEffect(() => {
		if (!initialized && !isLoading) {
			setInitialized(true);
		}
	}, [initialized, isLoading]);

	const showLoader = isLoading && !initialized;
	return <LoadingOverlay visible={showLoader} overlayProps={{ blur: 2 }} />;
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
