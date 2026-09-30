import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { AvatarStyleCard } from './AvatarStyleCard';
import { ArrowLeft, ArrowRight } from './Icons';
import { ACTIVE_EVENT } from '../events';
import type { AvatarStyle } from '../types';

interface ChoiceScreenProps<T extends AvatarStyle> {
  step: number;
  title: string;
  subtitle: string;
  items: T[];
  cta: (item: T) => string;
  placeholder: string;
  onSelect: (item: T) => void;
  onBack: () => void;
  onTimeout: () => void;
}

const IDLE_TIMEOUT = 5 * 60 * 1000; // 5 minutes

// Shared layout for the avatar style and location pickers
export function ChoiceScreen<T extends AvatarStyle>({
  step, title, subtitle, items, cta, placeholder, onSelect, onBack, onTimeout,
}: ChoiceScreenProps<T>) {
  const [selected, setSelected] = useState<T | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const eventIds = ACTIVE_EVENT ? [ACTIVE_EVENT.locationTheme.id, ACTIVE_EVENT.kit?.avatarStyle.id] : [];

  const resetTimer = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(onTimeout, IDLE_TIMEOUT);
  };

  useEffect(() => {
    resetTimer();
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex-1 flex flex-col w-full max-w-6xl mx-auto px-4 sm:px-8 pt-2" onPointerDown={resetTimer}>
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="flex-shrink-0 mb-4 sm:mb-5">
        <button onClick={onBack} className="inline-flex items-center gap-1.5 text-muted hover:text-ink text-sm font-medium mb-3">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="eyebrow mb-1">Step {step} of 3</p>
            <h1 className="text-3xl sm:text-4xl font-bold text-ink tracking-tight">{title}</h1>
            <p className="text-muted mt-1">{subtitle}</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-rows-2 gap-3 sm:gap-4 lg:flex-1 lg:min-h-0">
        {items.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="h-full lg:min-h-0"
          >
            <AvatarStyleCard
              style={item}
              isSelected={selected?.id === item.id}
              onSelect={() => setSelected(item)}
              badge={eventIds.includes(item.id) ? 'DevFest' : undefined}
            />
          </motion.div>
        ))}
      </div>

      {/* sticky so the button stays reachable on phones */}
      <div className="sticky bottom-0 flex-shrink-0 -mx-4 sm:mx-0 px-4 sm:px-0 pt-4 pb-4 sm:pb-6 bg-gradient-to-t from-canvas via-canvas/95 to-transparent">
        <button
          onClick={() => selected && onSelect(selected)}
          disabled={!selected}
          className="btn-primary w-full"
          style={selected ? { background: selected.color, boxShadow: `0 6px 20px ${selected.color}55` } : undefined}
        >
          {selected ? cta(selected) : placeholder}
          {selected && <ArrowRight className="w-5 h-5" />}
        </button>
      </div>
    </div>
  );
}
