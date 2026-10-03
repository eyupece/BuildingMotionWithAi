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
      description: 'Kale, konaklar ve Saat Kulesi',
      emoji: '🏰',
      color: '#A0783C',
      previewImage: '/previews/kastamonu.png',
    },
    kit: {
      avatarStyle: {
        id: 'kastamonu-afis',
        name: 'Kastamonu Afişi',
        description: 'Afişteki tezgaha işleniyorsun',
        emoji: '🧵',
        color: '#A23B2A',
        previewImage: '/previews/kastamonu-afis.png',
      },
      theme: {
        id: 'kastamonu-afis',
        name: 'Kastamonu afişi',
        description: 'DevFest Kastamonu afişindeki tezgahta',
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
      description: 'Liman, Sümela ve çay bahçeleri',
      emoji: '⛵',
      color: '#5C6B3A',
      previewImage: '/previews/trabzon.png',
    },
    kit: {
      avatarStyle: {
        id: 'trabzon-afis',
        name: 'Trabzon Afişi',
        description: 'Afişteki altın çerçeveye çiziliyorsun',
        emoji: '🖼️',
        color: '#7A1F1F',
        previewImage: '/previews/trabzon-afis.png',
      },
      theme: {
        id: 'trabzon-afis',
        name: 'Trabzon afişi',
        description: 'DevFest Trabzon afişindeki altın çerçevede',
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
