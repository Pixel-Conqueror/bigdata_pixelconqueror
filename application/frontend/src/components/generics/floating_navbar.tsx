import {
	Box,
	Burger,
	Drawer,
	Group,
	rem,
	useMantineTheme,
} from "@mantine/core";
import { useDisclosure, useHeadroom, useMediaQuery } from "@mantine/hooks";
import { useEffect } from "react";
import { projectName } from "../../config/project";
import { InputMovieRedirect } from "../input_movie_redirect";
import { ApiStatus } from "./api_status";
import { InternalLink } from "./internal_link";

interface FloatingNavbarProps {
	width: string;
}

export function FloatingNavbar({ width }: FloatingNavbarProps) {
	const theme = useMantineTheme();
	const [opened, handler] = useDisclosure(false);
	const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`, false);
	const pinned = useHeadroom({ fixedAt: 120 });

	useEffect(() => {
		if (opened && !isMobile) {
			handler.close();
		}
	}, [handler, isMobile, opened]);

	return (
		<Box
			style={{
				zIndex: 9,
				position: "sticky",
				top: 0,
				left: 0,
				right: 0,
				height: rem(60),
				backgroundColor: "light-dark(var(--mantine-color-gray-0), #1b2028)",
				paddingInline: "var(--mantine-spacing-lg)",
				paddingBlock: "var(--mantine-spacing-sm)",
				transform: `translate3d(0, ${pinned ? 0 : rem(-110)}, 0)`,
				transition: "transform 400ms ease",
			}}
		>
			<Group
				justify="space-between"
				style={{ maxWidth: "100%", width, marginInline: "auto" }}
			>
				<Group>
					{isMobile && <Burger opened={opened} onClick={handler.toggle} />}
					<InternalLink style={{ fontSize: rem(24) }} to="/">
						{projectName}
					</InternalLink>
				</Group>

				{!isMobile && (
					<Group gap="xs">
						<InputMovieRedirect />
						<ApiStatus />
					</Group>
				)}
			</Group>

			{/* Mobile drawer */}
			<Drawer
				opened={opened}
				onClose={handler.close}
				padding="md"
				title={projectName}
				zIndex={999999}
			>
				<InputMovieRedirect />
				<ApiStatus />
			</Drawer>
		</Box>
	);
}
