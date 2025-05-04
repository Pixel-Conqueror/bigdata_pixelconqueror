import { useDebouncedValue } from "@mantine/hooks";
import { useState } from "react";

export function useDebounceState<T>(value: T, delay: number = 300) {
	const [storedValue, setStoredValue] = useState(value);
	const [debouncedValue] = useDebouncedValue(storedValue, delay);
	return { storedValue, debouncedValue, setStoredValue };
}
