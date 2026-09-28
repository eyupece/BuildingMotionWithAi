import type { AvatarStyle, LocationTheme } from './types';

// DevFest themes, picked with VITE_EVENT in frontend/.env
export interface DevFestEvent {
  title: string;
  avatarStyle: AvatarStyle;
  locationTheme: LocationTheme;
}

export const EVENTS: Record<string, DevFestEvent> = {
  kastamonu: {
    title: 'DevFest Kastamonu 2026',
    avatarStyle: {
      id: 'kastamonu-gravur',
      name: 'Kastamonu Gravür',
      description: 'Vintage Anatolian engraving',
      emoji: '🪡',
      color: '#8B5E34',
      previewImage: '/previews/kastamonu-gravur.png',
    },
    locationTheme: {
      id: 'kastamonu',
      name: 'Kastamonu',
      description: 'Castle, konaks and clock tower',
      emoji: '🏰',
      color: '#A0783C',
      previewImage: '/previews/kastamonu.png',
    },
  },
  trabzon: {
    title: 'DevFest Trabzon 2026',
    avatarStyle: {
      id: 'rembrandt',
      name: 'Rembrandt',
      description: 'Dutch Golden Age oil portrait',
      emoji: '🖼️',
      color: '#7A4A24',
      previewImage: '/previews/rembrandt.png',
    },
    locationTheme: {
      id: 'trabzon',
      name: 'Trabzon',
      description: 'Black Sea harbor, Sümela, tea hills',
      emoji: '⛵',
      color: '#5C6B3A',
      previewImage: '/previews/trabzon.png',
    },
  },
};

const eventKey =
  (import.meta as { env?: { VITE_EVENT?: string } }).env?.VITE_EVENT?.trim().toLowerCase() ?? '';

export const ACTIVE_EVENT: DevFestEvent | null = EVENTS[eventKey] ?? null;
