import { ChoiceScreen } from '../components/ChoiceScreen';
import { AVATAR_STYLES } from '../mockData';
import type { AvatarStyle } from '../types';

interface AvatarStyleScreenProps {
  onSelect: (style: AvatarStyle) => void;
  onBack: () => void;
  onTimeout: () => void;
}

export function AvatarStyleScreen({ onSelect, onBack, onTimeout }: AvatarStyleScreenProps) {
  return (
    <ChoiceScreen
      step={2}
      title="Choose your style"
      subtitle="Nano Banana will draw your avatar in this style"
      items={AVATAR_STYLES}
      cta={(s) => `Continue with ${s.name}`}
      placeholder="Select a style"
      onSelect={onSelect}
      onBack={onBack}
      onTimeout={onTimeout}
    />
  );
}
