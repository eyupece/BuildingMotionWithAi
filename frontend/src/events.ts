import type { AvatarStyle, LocationTheme } from './types';

// DevFest themes, picked with VITE_EVENT in frontend/.env.
// locationTheme is a world for the codelab styles (a Pixel Hero in Kastamonu).
// kit puts you inside the event poster: picking it skips the world step.
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
        id: 'kastamonu-afis',
        name: 'Kastamonu Poster',
        description: 'Stitched onto the loom in the poster',
        emoji: '🧵',
        color: '#A23B2A',
        previewImage: '/previews/kastamonu-afis.png',
      },
      theme: {
        id: 'kastamonu-afis',
        name: 'the Kastamonu poster',
        description: 'On the loom in the DevFest Kastamonu poster',
        emoji: '🧵',
        color: '#A23B2A',
        previewImage: '/previews/kastamonu-afis.png',
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
    kit: {
      avatarStyle: {
        id: 'trabzon-afis',
        name: 'Trabzon Poster',
        description: 'Painted into the gold frame in the poster',
        emoji: '🖼️',
        color: '#7A1F1F',
        previewImage: '/previews/trabzon-afis.png',
      },
      theme: {
        id: 'trabzon-afis',
        name: 'the Trabzon poster',
        description: 'In the gold frame of the DevFest Trabzon poster',
        emoji: '🖼️',
        color: '#7A1F1F',
        previewImage: '/previews/trabzon-afis.png',
      },
    },
  },
};

const eventKey =
  (import.meta as { env?: { VITE_EVENT?: string } }).env?.VITE_EVENT?.trim().toLowerCase() ?? '';

export const ACTIVE_EVENT: DevFestEvent | null = EVENTS[eventKey] ?? null;

// Poster results are 4:5 posters, so show them whole instead of cropping
export const isPosterStyle = (id?: string) => !!id && id === ACTIVE_EVENT?.kit?.avatarStyle.id;
