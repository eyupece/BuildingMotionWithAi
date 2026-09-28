import { ChoiceScreen } from '../components/ChoiceScreen';
import { LOCATION_THEMES } from '../mockData';
import type { LocationTheme } from '../types';

interface LocationThemeScreenProps {
  onSelect: (theme: LocationTheme) => void;
  onBack: () => void;
  onTimeout: () => void;
}

export function LocationThemeScreen({ onSelect, onBack, onTimeout }: LocationThemeScreenProps) {
  return (
    <ChoiceScreen
      step={3}
      title="Choose your world"
      subtitle="Veo will place your avatar here"
      items={LOCATION_THEMES}
      cta={(t) => `Generate in ${t.name}`}
      placeholder="Select a world"
      onSelect={onSelect}
      onBack={onBack}
      onTimeout={onTimeout}
    />
  );
}
