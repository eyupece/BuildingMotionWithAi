import { motion } from 'framer-motion';
import { CheckIcon } from './Icons';
import type { AvatarStyle } from '../types';

interface AvatarStyleCardProps {
  style: AvatarStyle;
  isSelected: boolean;
  onSelect: () => void;
  badge?: string;
}

export function AvatarStyleCard({ style, isSelected, onSelect, badge }: AvatarStyleCardProps) {
  return (
    <motion.button
      onClick={onSelect}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.97 }}
      className="group relative flex flex-col w-full h-full text-left bg-white rounded-3xl p-2 border-2 transition-shadow"
      style={{
        borderColor: isSelected ? style.color : 'transparent',
        boxShadow: isSelected
          ? `0 0 0 4px ${style.color}22, 0 12px 32px rgba(60,64,67,0.14)`
          : '0 1px 2px rgba(60,64,67,0.08), 0 4px 16px rgba(60,64,67,0.06)',
      }}
    >
      <div
        className="relative flex-1 min-h-0 w-full aspect-square lg:aspect-auto rounded-2xl overflow-hidden"
        style={{ background: `${style.color}18` }}
      >
        <img
          src={style.previewImage}
          alt={style.name}
          className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.04]"
          loading="eager"
        />
        {badge && (
          <span className="absolute top-2 left-2 flex items-center gap-1.5 rounded-full bg-white/95 pl-1.5 pr-2.5 py-1 text-[11px] font-semibold text-ink shadow">
            <img src="/devfest-mark.png" alt="" className="h-3 w-auto" />
            {badge}
          </span>
        )}
        {isSelected && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute top-2 right-2 w-8 h-8 rounded-full flex items-center justify-center text-white shadow"
            style={{ background: style.color }}
          >
            <CheckIcon className="w-4 h-4" />
          </motion.div>
        )}
      </div>
      <div className="px-2 pt-2.5 pb-1.5 flex-shrink-0">
        <div className="font-semibold text-ink text-sm sm:text-base leading-tight line-clamp-1 sm:line-clamp-none break-words">{style.name}</div>
        <div className="text-muted text-xs sm:text-sm leading-snug truncate">{style.description}</div>
      </div>
    </motion.button>
  );
}
