import { ACTIVE_EVENT } from '../events';

interface HeaderProps {
  onLogoTap?: () => void;
  right?: React.ReactNode;
}

export function Header({ onLogoTap, right }: HeaderProps) {
  return (
    <header className="flex items-center justify-between gap-4 px-4 sm:px-8 pt-4 sm:pt-6 pb-2 flex-shrink-0">
      {/* tapping the logo 5x opens the debug panel */}
      <button onClick={onLogoTap} className="flex items-center gap-2.5 cursor-default" aria-label="Gemini Motion Lab">
        <span className="flex gap-1">
          <span className="w-2 h-2 rounded-full bg-google-blue" />
          <span className="w-2 h-2 rounded-full bg-google-red" />
          <span className="w-2 h-2 rounded-full bg-google-yellow" />
          <span className="w-2 h-2 rounded-full bg-google-green" />
        </span>
        <span className="font-semibold text-ink text-base sm:text-lg tracking-tight">Gemini Motion Lab</span>
      </button>

      <div className="flex items-center gap-3">
        {right}
        {ACTIVE_EVENT && (
          <span className="hidden sm:flex items-center gap-2 rounded-full bg-white border border-line pl-2 pr-3.5 py-1.5 shadow-card">
            <img src="/devfest-mark.png" alt="" className="h-4 w-auto" />
            <span className="text-sm font-semibold text-ink">{ACTIVE_EVENT.title}</span>
          </span>
        )}
      </div>
    </header>
  );
}
