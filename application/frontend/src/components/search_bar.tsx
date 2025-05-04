import { TextInput } from "@mantine/core";

interface SearchBarProps {
	searchQuery: string;
	onChange: (value: string) => void;
}

export const SearchBar = ({ searchQuery, onChange }: SearchBarProps) => (
	<TextInput
		placeholder="Rechercher"
		value={searchQuery}
		onChange={(e) => onChange(e.target.value)}
	/>
);
