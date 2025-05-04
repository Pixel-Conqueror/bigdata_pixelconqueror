import { Group, Text } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { apiService, querykeys } from "../../services/api_service";

export function ApiStatus() {
	const { data: health } = useQuery({
		queryKey: querykeys.health,
		queryFn: apiService.getHealth,
	});

	return (
		<Group>
			<Text>{health?.status}</Text>
			<Text>Database: {health?.db_status.ok ? "✅" : "❌"}</Text>
		</Group>
	);
}
