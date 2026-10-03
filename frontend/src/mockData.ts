import type { AvatarStyle, LocationTheme } from './types';
import { ACTIVE_EVENT } from './events';

const GRID_SIZE = 6;

const BASE_AVATAR_STYLES: AvatarStyle[] = [
  {
    id: 'pixel-hero',
    name: 'Pixel Hero',
    description: 'Retro piksel kahraman',
    emoji: '🎮',
    color: '#EA4335',
    previewImage: '/previews/pixel-hero.png',
  },
  {
    id: 'cyber-nova',
    name: 'Cyber Nova',
    description: 'Krom Google androidi',
    emoji: '🤖',
    color: '#4285F4',
    previewImage: '/previews/cyber-nova.png',
  },
  {
    id: 'watercolor-dream',
    name: 'Watercolor Dream',
    description: 'Suluboya siluet',
    emoji: '🎨',
    color: '#34A853',
    previewImage: '/previews/watercolor-dream.png',
  },
  {
    id: '3d-figurine',
    name: '3D Figurine',
    description: 'Koleksiyonluk figür',
    emoji: '🧸',
    color: '#FBBC05',
    previewImage: '/previews/3d-figurine.png',
  },
  {
    id: 'manga-ink',
    name: 'Manga Ink',
    description: 'Siyah beyaz manga',
    emoji: '✒️',
    color: '#9C27B0',
    previewImage: '/previews/manga-ink.png',
  },
  {
    id: 'brick-build',
    name: 'Brick Build',
    description: 'Oyuncak tuğlalardan',
    emoji: '🧱',
    color: '#FF6D00',
    previewImage: '/previews/brick-build.png',
  },
];

const BASE_LOCATION_THEMES: LocationTheme[] = [
  {
    id: 'lunar-surface',
    name: 'Ay Yüzeyi',
    description: 'Ufukta yükselen Dünya',
    emoji: '🌙',
    color: '#B8C4E8',
    previewImage: '/previews/lunar-surface.png',
  },
  {
    id: 'golden-desert',
    name: 'Altın Çöl',
    description: 'Kum tepelerinde antik kalıntılar',
    emoji: '🏜️',
    color: '#E8A94A',
    previewImage: '/previews/golden-desert.png',
  },
  {
    id: 'neon-city',
    name: 'Neon Şehir',
    description: 'Gece vakti siberpunk şehir',
    emoji: '🌃',
    color: '#E8487A',
    previewImage: '/previews/neon-city.png',
  },
  {
    id: 'space-station',
    name: 'Uzay İstasyonu',
    description: 'Yörüngedeki komuta merkezi',
    emoji: '🚀',
    color: '#4285F4',
    previewImage: '/previews/space-station.png',
  },
  {
    id: 'enchanted-forest',
    name: 'Büyülü Orman',
    description: 'Işıl ışıl parlayan orman',
    emoji: '🌲',
    color: '#34A853',
    previewImage: '/previews/enchanted-forest.png',
  },
  {
    id: 'underwater-palace',
    name: 'Su Altı Sarayı',
    description: 'Denizin altında antik tapınak',
    emoji: '🌊',
    color: '#00BCD4',
    previewImage: '/previews/underwater-palace.png',
  },
];

export const AVATAR_STYLES: AvatarStyle[] = ACTIVE_EVENT?.kit
  ? [ACTIVE_EVENT.kit.avatarStyle, ...BASE_AVATAR_STYLES].slice(0, GRID_SIZE)
  : BASE_AVATAR_STYLES;

export const LOCATION_THEMES: LocationTheme[] = ACTIVE_EVENT
  ? [ACTIVE_EVENT.locationTheme, ...BASE_LOCATION_THEMES].slice(0, GRID_SIZE)
  : BASE_LOCATION_THEMES;

export const PROCESSING_TIPS = [
  'Video Vertex AI üzerinde Veo 3.1 ile üretiliyor',
  'Gemini hareketini kare kare inceledi',
  'Avatarın canlanıyor',
  'Hareketin Veo için adım adım tarif edildi',
];

export const ANALYSIS_LINES = [
  'Vücut hareketi algılanıyor...',
  'Kollar: başın üstünde, geniş bir hareket',
  'Bacaklar: ağırlık soldan sağa geçiyor',
  'Tempo: orta | Enerji: yüksek',
  'Stil: akıcı, dans gibi',
];

export const mockDelay = (ms: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, ms));

// Returns a placeholder avatar image URL (colored data URL)
export function getMockAvatarImageUrl(styleColor: string): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
    <rect width="400" height="400" fill="${styleColor}" opacity="0.2" rx="20"/>
    <circle cx="200" cy="150" r="80" fill="${styleColor}" opacity="0.6"/>
    <rect x="120" y="250" width="160" height="120" rx="20" fill="${styleColor}" opacity="0.6"/>
    <text x="200" y="380" text-anchor="middle" font-size="24" fill="white" opacity="0.8">Avatar önizleme</text>
  </svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

export const SHARE_URL = 'https://cloud.google.com/next';
