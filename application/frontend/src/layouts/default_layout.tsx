import { Box, rem } from "@mantine/core";
import { Outlet } from "react-router-dom";
import { FloatingNavbar } from "../components/generics/floating_navbar";

const LAYOUT_WIDTH = "1500px";
const DefaultLayout = () => (
	<>
		{/* Floating navbar */}
		<FloatingNavbar width={LAYOUT_WIDTH} />

		{/* Page content */}
		<Box
			style={{
				paddingInline: "var(--mantine-spacing-lg)",
				flex: 1,
			}}
		>
			<Box
				style={{
					height: "100%",
					maxWidth: "100%",
					width: LAYOUT_WIDTH,
					marginInline: "auto",
					marginBlock: rem(60),
				}}
			>
				<Outlet />
			</Box>
		</Box>
	</>
);

export default DefaultLayout;
