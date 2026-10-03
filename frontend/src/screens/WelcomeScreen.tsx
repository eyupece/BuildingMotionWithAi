import { motion } from 'framer-motion';
import { useState } from 'react';
import { ACTIVE_EVENT } from '../events';
import { AVATAR_STYLES, LOCATION_THEMES } from '../mockData';
import { Pipeline } from '../components/Pipeline';
import { ArrowRight, CheckIcon } from '../components/Icons';

interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const [consented, setConsented] = useState(false);
  const hero = [AVATAR_STYLES[0], LOCATION_THEMES[0], AVATAR_STYLES[1]];

  return (
    <div className="flex-1 flex flex-col justify-center px-4 sm:px-8 py-6 sm:py-8">
      <div className="mx-auto w-full max-w-6xl grid lg:grid-cols-[1.25fr_1fr] gap-10 lg:gap-14 items-center">
        {/* Left: copy + start */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="flex flex-col gap-5 sm:gap-6 text-center lg:text-left items-center lg:items-start"
        >
          {ACTIVE_EVENT && (
            <span className="flex sm:hidden items-center gap-2 rounded-full bg-white border border-line pl-2 pr-3.5 py-1.5 shadow-card">
              <img src="/devfest-mark.png" alt="" className="h-4 w-auto" />
              <span className="text-sm font-semibold text-ink">{ACTIVE_EVENT.title}</span>
            </span>
          )}

          <h1 className="text-5xl sm:text-6xl 2xl:text-7xl font-bold tracking-tight leading-[1.02] text-ink">
            Hareketini kaydet.
            <br />
            <span className="bg-gradient-to-r from-[#4285F4] via-[#A142F4] to-[#EA4335] bg-clip-text text-transparent">
              Kendini yapay zekayla gör.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-muted max-w-xl">
            Gemini hareketini anlıyor, Nano Banana avatarını çiziyor, Veo da onu aynı hareketi yaparken canlandırıyor.
          </p>

          {/* Consent */}
          <label
            htmlFor="privacy-consent"
            className="flex items-start gap-3 text-left rounded-2xl bg-white border border-line px-4 py-3.5 cursor-pointer max-w-xl w-full shadow-card"
          >
            <span
              className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-md mt-0.5 border-2 transition-colors"
              style={{
                background: consented ? '#4285F4' : '#FFFFFF',
                borderColor: consented ? '#4285F4' : '#DADCE0',
              }}
            >
              {consented && <CheckIcon className="w-4 h-4 text-white" />}
            </span>
            <span className="text-muted text-sm sm:text-base leading-relaxed">
              Bu demonun yüzümü kaydettiğini ve videoyu yapay zeka modelleriyle işlediğini biliyorum.
            </span>
            <input
              id="privacy-consent"
              type="checkbox"
              checked={consented}
              onChange={(e) => setConsented(e.target.checked)}
              className="sr-only"
              aria-label="Gizlilik onayı"
            />
          </label>

          <motion.button
            whileTap={consented ? { scale: 0.97 } : undefined}
            onClick={onStart}
            disabled={!consented}
            className="btn-primary w-full sm:w-auto px-12 text-xl"
          >
            Başla
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.div>

        {/* Right: preview collage */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.15, ease: 'easeOut' }}
          className="relative hidden sm:block mx-auto w-full max-w-md lg:max-w-[440px] aspect-square"
        >
          <div className="absolute inset-[8%] rounded-full bg-[#E8F0FE]" />
          {hero.map((item, i) => {
            const pos = [
              'left-[4%] top-[10%] w-[52%] rotate-[-5deg] z-10',
              'right-[2%] top-[4%] w-[44%] rotate-[4deg]',
              'right-[10%] bottom-[4%] w-[48%] rotate-[-2deg] z-20',
            ][i];
            return (
              <motion.div
                key={item.id}
                className={`absolute ${pos} card p-2 shadow-lift`}
                animate={{ y: [0, i % 2 ? 8 : -8, 0] }}
                transition={{ duration: 5 + i, repeat: Infinity, ease: 'easeInOut' }}
              >
                <img src={item.previewImage} alt={item.name} className="w-full aspect-square object-cover rounded-2xl" />
                <p className="px-1.5 pt-2 pb-1 text-sm font-semibold text-ink">{item.name}</p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>

      {/* Pipeline overview, same as the talk */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        className="mx-auto w-full max-w-3xl mt-8 lg:mt-10"
      >
        <Pipeline current="all" compact />
      </motion.div>
    </div>
  );
}
