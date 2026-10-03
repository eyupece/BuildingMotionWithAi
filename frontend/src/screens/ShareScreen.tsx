import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { QRCodeSVG } from 'qrcode.react';
import { useApi } from '../hooks/useApi';
import { Pipeline } from '../components/Pipeline';

interface ShareScreenProps {
  onDone: () => void;
  videoId: string;
  shareUrl: string;
}

const IDLE_TIMEOUT = 5 * 60 * 1000; // 5 minutes
const COUNTDOWN_S = 90;

export function ShareScreen({ onDone, videoId, shareUrl }: ShareScreenProps) {
  const [timeLeft, setTimeLeft] = useState(COUNTDOWN_S);
  const [composedVideoUrl, setComposedVideoUrl] = useState<string | null>(null);
  const [isComposing, setIsComposing] = useState(true);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { getShare } = useApi();

  // shareUrl comes from the upload response (backend's PUBLIC_BASE_URL/share/{videoId}),
  // ensuring both the loading screen QR and this QR always encode the same correct link.

  const startCountdown = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (countdownRef.current) clearInterval(countdownRef.current);

    setTimeLeft(COUNTDOWN_S);
    timerRef.current = setTimeout(onDone, IDLE_TIMEOUT);
    countdownRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          if (countdownRef.current) clearInterval(countdownRef.current);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
  };

  const resetTimer = () => {
    startCountdown();
  };

  useEffect(() => {
    // Start countdown immediately — QR is visible from the start
    startCountdown();

    // Compose video in background (for kiosk preview only)
    if (videoId) {
      getShare(videoId)
        .then((data) => {
          setComposedVideoUrl(data.download_url);
        })
        .catch(() => {
          // Composition failed — QR still works, user can compose on mobile
        })
        .finally(() => {
          setIsComposing(false);
        });
    } else {
      setIsComposing(false);
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-8 pt-2 pb-6 flex flex-col gap-5" onPointerDown={resetTimer}>
      <div className="card px-4 sm:px-8 py-5">
        <Pipeline current="share" done />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="flex-1 card grid md:grid-cols-[auto_1fr] gap-8 items-center p-6 sm:p-10"
      >
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-white rounded-3xl border border-line">
            <QRCodeSVG value={shareUrl} size={240} bgColor="#ffffff" fgColor="#202124" level="M" className="w-[200px] h-[200px] sm:w-[240px] sm:h-[240px]" />
          </div>
          {isComposing && (
            <motion.p
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
              className="text-muted text-sm"
            >
              Video hazırlanıyor...
            </motion.p>
          )}
        </div>

        <div className="flex flex-col gap-5 text-center md:text-left items-center md:items-start">
          <div>
            <h1 className="text-3xl sm:text-5xl font-bold text-ink tracking-tight">Videon için okut</h1>
            <p className="text-muted text-lg mt-2">Telefonuna indir, istediğin yerde paylaş.</p>
          </div>

          <AnimatePresence>
            {composedVideoUrl && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl overflow-hidden shadow-card bg-[#202124]"
                style={{ width: 150, aspectRatio: '9/16' }}
              >
                <video src={composedVideoUrl} autoPlay loop muted playsInline className="w-full h-full object-cover" />
              </motion.div>
            )}
          </AnimatePresence>

          <button onClick={onDone} className="btn-primary w-full sm:w-auto px-12">
            Baştan başla
          </button>
          <p className="text-muted text-sm">{timeLeft} sn sonra başa dönülecek</p>
        </div>
      </motion.div>
    </div>
  );
}
