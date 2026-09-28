// Small inline icons so we don't pull in an icon library
type P = { className?: string };
const base = { width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };

export const UploadIcon = ({ className }: P) => (
  <svg {...base} className={className}><path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 9.5a4 4 0 0 1-.5 8.5" /><path d="M12 12v8M9 15l3-3 3 3" /></svg>
);
export const SparkIcon = ({ className }: P) => (
  <svg {...base} className={className}><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" /><path d="M19 15l.7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7z" /></svg>
);
export const FaceIcon = ({ className }: P) => (
  <svg {...base} className={className}><circle cx="12" cy="12" r="9" /><path d="M9 10h.01M15 10h.01M8.5 14.5a4.5 4.5 0 0 0 7 0" /></svg>
);
export const FilmIcon = ({ className }: P) => (
  <svg {...base} className={className}><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M3 7l3-4h3l-3 4M10 7l3-4h3l-3 4M17 7l3-4" /></svg>
);
export const QrIcon = ({ className }: P) => (
  <svg {...base} className={className}><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><path d="M14 14h3v3M21 14v.01M14 21h3M21 17v4h-1" /></svg>
);
export const CameraIcon = ({ className }: P) => (
  <svg {...base} className={className}><rect x="2" y="6" width="14" height="12" rx="2" /><path d="M16 10l6-3v10l-6-3" /></svg>
);
export const ArrowLeft = ({ className }: P) => (
  <svg {...base} className={className}><path d="M19 12H5M11 6l-6 6 6 6" /></svg>
);
export const ArrowRight = ({ className }: P) => (
  <svg {...base} className={className}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
);
export const CheckIcon = ({ className }: P) => (
  <svg {...base} strokeWidth={3} className={className}><path d="M5 12.5l4.5 4.5L19 7" /></svg>
);
export const CloseIcon = ({ className }: P) => (
  <svg {...base} className={className}><path d="M6 6l12 12M18 6L6 18" /></svg>
);
export const RetryIcon = ({ className }: P) => (
  <svg {...base} className={className}><path d="M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4" /></svg>
);
