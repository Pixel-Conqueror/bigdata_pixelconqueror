import { Select } from "@mantine/core";

interface GenderFilterProps {
	genders: string[];
	selectedGender: string | null;
	onChange: (value: string | null) => void;
}

export const GenderFilter = ({
	genders,
	selectedGender,
	onChange,
}: GenderFilterProps) => (
	<Select
		data={genders}
		value={selectedGender}
		onChange={(value) => onChange(value)}
		clearable
		searchable
		placeholder="Filtrer par genre"
	/>
);
