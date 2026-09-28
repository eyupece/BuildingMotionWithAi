import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Pipeline } from '../components/Pipeline';
import { QrIcon, RetryIcon } from '../components/Icons';

interface ResultScreenProps {
  recordedVideoUrl: string;
  avatarImageUrl: string;
  generatedVideoUrl: string | null;
  onShare: () => void;
  onTryAgain: () => void;
  onTimeout: () => void;
}

const IDLE_TIMEOUT = 5 * 60 * 1000; // 5 minutes

export function ResultScreen({
  recordedVideoUrl,
  avatarImageUrl,
  generatedVideoUrl,
  onShare,
  onTryAgain,
  onTimeout,
}: ResultScreenProps) {
  const originalRef = useRef<HTMLVideoElement>(null);
  const avatarRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const resetTimer = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(onTimeout, IDLE_TIMEOUT);
  };

  useEffect(() => {
    if (originalRef.current) originalRef.current.play();
    if (avatarRef.current) avatarRef.current.play();
    resetTimer();
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-8 pt-2 pb-6 flex flex-col gap-5" onPointerDown={resetTimer}>
      <div className="card px-4 sm:px-8 py-5">
        <Pipeline current="veo" done />
      </div>

      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold text-ink tracking-tight">Your avatar is ready</h1>
        <p className="text-muted mt-1">Same move, new you.</p>
      </motion.div>

      <div className="grid sm:grid-cols-2 gap-4 sm:gap-5 flex-1 min-h-0">
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
          className="card p-2 flex flex-col"
        >
          <div className="relative flex-1 min-h-[220px] rounded-2xl overflow-hidden bg-[#202124]">
            <video ref={originalRef} src={recordedVideoUrl} loop playsInline muted className="absolute inset-0 w-full h-full object-cover" />
          </div>
          <p className="px-2 pt-2.5 pb-1 font-semibold text-ink">You</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.25 }}
          className="card p-2 flex flex-col"
          style={{ boxShadow: '0 0 0 3px #34A85333, 0 12px 32px rgba(60,64,67,0.14)' }}
        >
          <div className="relative flex-1 min-h-[220px] rounded-2xl overflow-hidden bg-[#202124] flex items-center justify-center">
            {generatedVideoUrl ? (
              <video ref={avatarRef} src={generatedVideoUrl} loop playsInline muted className="absolute inset-0 w-full h-full object-cover" />
            ) : (
              <div className="flex flex-col items-center gap-3 p-6 text-center">
                <img src={avatarImageUrl} alt="Generated avatar" className="w-32 h-32 rounded-2xl object-cover" />
                <p className="text-white/70 text-sm">Video generation failed. Tap Try Again.</p>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2.5 px-2 pt-2.5 pb-1">
            <img src={avatarImageUrl} alt="" className="w-7 h-7 rounded-lg object-cover" />
            <p className="font-semibold text-ink">Your avatar</p>
            <span className="ml-auto text-xs font-medium text-google-green bg-[#34A853]/10 rounded-full px-2.5 py-1">Veo</span>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex flex-col-reverse sm:flex-row gap-3 sm:justify-center"
      >
        <button onClick={onTryAgain} className="btn-secondary sm:min-w-[200px]">
          <RetryIcon className="w-5 h-5" /> Try Again
        </button>
        <button onClick={onShare} className="btn-primary sm:min-w-[200px]" style={{ background: '#EA4335', boxShadow: '0 6px 20px rgba(234,67,53,0.35)' }}>
          <QrIcon className="w-5 h-5" /> Share
        </button>
      </motion.div>
    </div>
  );
}
