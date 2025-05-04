import { TableProps } from "@mantine/core";

export const getCommonTableProps = (): TableProps => ({
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
});
