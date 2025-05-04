import { Text } from "@mantine/core";
import { ShapesData } from "../../../types";
import classes from "./stats.module.css";

interface StatsGroupProps {
	stats: ShapesData;
}

const format_number = (number: number) =>
	new Intl.NumberFormat("fr-FR").format(number);

export function StatsGroup({ stats }: StatsGroupProps) {
	const data = [
		{
			title: "Films",
			stats: format_number(stats.total_movies),
			description: "Nombres de films dans la base de données",
		},
		{
			title: "Utilisateurs",
			stats: format_number(stats.total_users),
			description: "Nombres d'utilisateurs dans la base de données",
		},
		{
			title: "Notes",
			stats: format_number(stats.total_ratings),
			description: `Cela représente une moyenne de ~${format_number(
				Math.round(stats.total_ratings / stats.total_users)
			)} notes par utilisateur`,
		},
	];
	const statsComponents = data.map((stat) => (
		<div key={stat.title} className={classes.stat}>
			<Text className={classes.count}>{stat.stats}</Text>
			<Text className={classes.title}>{stat.title}</Text>
			<Text className={classes.description}>{stat.description}</Text>
		</div>
	));
	return <div className={classes.root}>{statsComponents}</div>;
}
