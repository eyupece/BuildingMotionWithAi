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
      title="Dünyanı seç"
      subtitle="Veo avatarını buraya yerleştirecek"
      items={LOCATION_THEMES}
      cta={(t) => `${t.name} ile oluştur`}
      placeholder="Bir dünya seç"
      onSelect={onSelect}
      onBack={onBack}
      onTimeout={onTimeout}
    />
  );
}
