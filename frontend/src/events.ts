import type { AvatarStyle, LocationTheme } from './types';

// DevFest themes, picked with VITE_EVENT in frontend/.env.
// locationTheme is a world for the codelab styles (a Pixel Hero in Kastamonu).
// kit is the event's own look from its poster: picking its style skips the
// world step and always uses its own scene.
export interface DevFestEvent {
  title: string;
  locationTheme: LocationTheme;
  kit?: {
    avatarStyle: AvatarStyle;
    theme: LocationTheme;
  };
}

export const EVENTS: Record<string, DevFestEvent> = {
  kastamonu: {
    title: 'DevFest Kastamonu 2026',
    locationTheme: {
      id: 'kastamonu',
      name: 'Kastamonu',
      description: 'Castle, konaks and clock tower',
      emoji: '🏰',
      color: '#A0783C',
      previewImage: '/previews/kastamonu.png',
    },
    kit: {
      avatarStyle: {
        id: 'kastamonu-dokuma',
        name: 'Kastamonu Dokuma',
        description: 'Woven into a Kastamonu kilim',
        emoji: '🧶',
        color: '#A23B2A',
        previewImage: '/previews/kastamonu-dokuma.png',
      },
      theme: {
        id: 'kastamonu-tezgah',
        name: 'a Kastamonu kilim',
        description: 'Weaving room of an old Kastamonu mansion',
        emoji: '🧶',
        color: '#A23B2A',
        previewImage: '/previews/kastamonu-dokuma.png',
      },
    },
  },
  trabzon: {
    title: 'DevFest Trabzon 2026',
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
