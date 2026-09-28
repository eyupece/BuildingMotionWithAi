import { motion } from 'framer-motion';
import { UploadIcon, SparkIcon, FaceIcon, FilmIcon, QrIcon, CheckIcon } from './Icons';

// Same five stages and colors as the timeline in the talk deck
export const STAGES = [
  { key: 'upload', label: 'Upload', color: '#4285F4', Icon: UploadIcon },
  { key: 'gemini', label: 'Gemini', color: '#A142F4', Icon: SparkIcon },
  { key: 'banana', label: 'Nano Banana', color: '#F9AB00', Icon: FaceIcon },
  { key: 'veo', label: 'Veo', color: '#34A853', Icon: FilmIcon },
  { key: 'share', label: 'Share', color: '#EA4335', Icon: QrIcon },
] as const;

export type StageKey = (typeof STAGES)[number]['key'];

interface PipelineProps {
  // active stage; null = nothing started, 'all' = static overview with every stage lit
  current: StageKey | null | 'all';
  // mark the current stage as finished too
  done?: boolean;
  compact?: boolean;
}

export function Pipeline({ current, done = false, compact = false }: PipelineProps) {
  const idx = current === 'all' ? STAGES.length : current ? STAGES.findIndex((s) => s.key === current) : -1;
  const fill = current === 'all' ? 1 : Math.max(0, idx) / (STAGES.length - 1);
  const node = compact ? 'w-8 h-8 sm:w-10 sm:h-10' : 'w-10 h-10 sm:w-12 sm:h-12';

  return (
    <div className="relative w-full">
      {/* track, runs between the first and last node centers */}
      <div className={`absolute left-[10%] right-[10%] h-[3px] rounded-full bg-faint ${compact ? 'top-[15px] sm:top-[19px]' : 'top-[19px] sm:top-[23px]'}`}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: 'linear-gradient(90deg,#4285F4,#A142F4,#F9AB00,#34A853,#EA4335)' }}
          initial={false}
          animate={{ width: `${fill * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeInOut' }}
        />
      </div>

      <div className="relative grid grid-cols-5">
        {STAGES.map(({ key, label, color, Icon }, i) => {
          const isDone = current === 'all' || i < idx || (done && i === idx);
          const isActive = current !== 'all' && i === idx && !done;
          const lit = isDone || isActive;
          return (
            <div key={key} className="flex flex-col items-center gap-1.5">
              <motion.div
                className={`${node} relative rounded-full flex items-center justify-center border-2`}
                initial={false}
                animate={{
                  backgroundColor: lit ? color : '#FFFFFF',
                  borderColor: lit ? color : '#DADCE0',
                  color: lit ? '#FFFFFF' : '#9AA0A6',
                  scale: isActive ? 1.12 : 1,
                }}
                transition={{ duration: 0.4 }}
              >
                {isActive && (
                  <motion.span
                    className="absolute inset-0 rounded-full"
                    style={{ border: `2px solid ${color}` }}
                    animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                    transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut' }}
                  />
                )}
                {isDone && current !== 'all' ? <CheckIcon className="w-4 h-4 sm:w-5 sm:h-5" /> : <Icon className="w-4 h-4 sm:w-5 sm:h-5" />}
              </motion.div>
              <span
                className={`text-[10px] sm:text-xs font-medium text-center leading-tight ${compact ? 'hidden sm:block' : ''}`}
                style={{ color: isActive ? color : lit ? '#202124' : '#80868B' }}
              >
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
