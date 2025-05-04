import { MantineProvider } from "@mantine/core";
import React from "react";

export const BaseLayout = ({ children }: React.PropsWithChildren) => (
	<MantineProvider>{children}</MantineProvider>
);
