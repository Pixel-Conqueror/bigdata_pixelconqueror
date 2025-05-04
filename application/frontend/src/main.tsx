import "@mantine/charts/styles.css";
import "@mantine/core/styles.css";
import { createRoot } from "react-dom/client";
import { AppRouter } from "./app/app_router";

createRoot(document.getElementById("root")!).render(<AppRouter />);
