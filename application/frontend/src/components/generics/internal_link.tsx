import { Anchor } from "@mantine/core";
import { CSSProperties } from "react";
import { Link } from "react-router-dom";

interface InternalLinkProps {
	children: React.ReactNode;
	to: string;
	style?: CSSProperties;
	onClick?: () => void;
}

export const InternalLink = ({
	children,
	to,
	style,
	onClick,
}: InternalLinkProps) => (
	<Anchor component={Link} to={to} style={style} onClick={onClick}>
		{children}
	</Anchor>
);
