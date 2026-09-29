import type { LocationTheme } from './types';

// DevFest themes, picked with VITE_EVENT in frontend/.env
// Only the location is event specific. Avatar styles stay the codelab ones,
// so people can be a Pixel Hero in Kastamonu.
export interface DevFestEvent {
  title: string;
  locationTheme: LocationTheme;
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
