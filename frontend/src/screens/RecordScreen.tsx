import { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCamera } from '../hooks/useCamera';
import { CountdownTimer } from '../components/CountdownTimer';
import { ProgressRing } from '../components/ProgressRing';
import { ArrowRight, CameraIcon, CloseIcon, RetryIcon } from '../components/Icons';

interface RecordScreenProps {
  onComplete: (blob: Blob, url: string) => void;
  onBack: () => void;
}

type RecordState = 'preview' | 'countdown' | 'recording' | 'playback' | 'interrupted';

const RECORD_DURATION = 5000;
const COUNTDOWN_START = 3;

export function RecordScreen({ onComplete, onBack }: RecordScreenProps) {
  const { videoRef, isReady, error, streamDropped, startCamera, stopCamera, startRecording, stopRecording } =
    useCamera();
  const playbackRef = useRef<HTMLVideoElement>(null);
  const [recordState, setRecordState] = useState<RecordState>('preview');
  const [countdown, setCountdown] = useState(COUNTDOWN_START);
  const [recordProgress, setRecordProgress] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null);
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    };
  }, [startCamera, stopCamera]);

  // Handle stream drop during recording
  useEffect(() => {
    if (streamDropped && (recordState === 'recording' || recordState === 'countdown')) {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      setRecordState('interrupted');
    }
  }, [streamDropped, recordState]);

  const handleRecord = useCallback(() => {
    if (recordState !== 'preview') return;
    setRecordState('countdown');
    setCountdown(COUNTDOWN_START);

    let c = COUNTDOWN_START;
    const interval = setInterval(() => {
      c--;
      if (c <= 0) {
        clearInterval(interval);
        setRecordState('recording');
        startRecording();

        const start = Date.now();
        progressIntervalRef.current = setInterval(() => {
          const elapsed = Date.now() - start;
          const progress = Math.min(elapsed / RECORD_DURATION, 1);
          setRecordProgress(progress);
          if (progress >= 1) {
            clearInterval(progressIntervalRef.current!);
          }
        }, 50);

        setTimeout(async () => {
          const blob = await stopRecording();
          if (blob) {
            const url = URL.createObjectURL(blob);
            setRecordedBlob(blob);
            setRecordedUrl(url);
            setRecordState('playback');
            setTimeout(() => {
              if (playbackRef.current) {
                playbackRef.current.src = url;
                playbackRef.current.play();
              }
            }, 100);
          }
        }, RECORD_DURATION);
      } else {
        setCountdown(c);
      }
    }, 1000);
  }, [recordState, startRecording, stopRecording]);

  const handleRetake = useCallback(() => {
    setRecordState('preview');
    setRecordProgress(0);
    setRecordedBlob(null);
    if (recordedUrl) {
      URL.revokeObjectURL(recordedUrl);
      setRecordedUrl(null);
    }
  }, [recordedUrl]);

  const handleRetakeAfterInterrupt = useCallback(() => {
    setRecordState('preview');
    setRecordProgress(0);
    startCamera();
  }, [startCamera]);

  const handleNext = useCallback(() => {
    if (recordedBlob && recordedUrl) {
      stopCamera();
      onComplete(recordedBlob, recordedUrl);
    }
  }, [recordedBlob, recordedUrl, stopCamera, onComplete]);

  // Camera permission error
  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center px-4 sm:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="card flex flex-col items-center gap-5 px-6 sm:px-12 py-10 text-center max-w-lg"
        >
          <div className="w-20 h-20 rounded-full flex items-center justify-center bg-[#EA4335]/10 text-google-red">
            <CameraIcon className="w-9 h-9" />
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-ink">Kamera izni gerekiyor</h2>
          <p className="text-muted text-lg">
            Hareketini kaydetmek için kamera izni ver. Tarayıcı ayarlarını kontrol edip tekrar dene.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 w-full mt-2">
            <button onClick={onBack} className="btn-secondary flex-1">Geri dön</button>
            <button onClick={() => startCamera()} className="btn-primary flex-1">Tekrar dene</button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col w-full max-w-5xl mx-auto px-4 sm:px-8 pt-2 pb-6">
      <div className="flex items-end justify-between gap-4 mb-4">
        <div>
          <p className="eyebrow mb-1">Adım 1 / 3</p>
          <h1 className="text-3xl sm:text-4xl font-bold text-ink tracking-tight">
            {recordState === 'playback' ? 'Beğendin mi?' : 'Hareketini kaydet'}
          </h1>
          <p className="text-muted mt-1">
            {recordState === 'playback'
              ? 'Bu video hareket analizi için Gemini\'ye gidecek.'
              : 'Belden yukarın kadraja girecek kadar geri çekil, sonra 5 saniyelik net bir hareket yap.'}
          </p>
        </div>
        {recordState === 'preview' && (
          <button onClick={onBack} className="flex-shrink-0 w-11 h-11 rounded-full bg-white border border-line flex items-center justify-center text-muted hover:text-ink" aria-label="Kapat">
            <CloseIcon className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Camera frame */}
      <div className="relative w-full aspect-[3/4] sm:aspect-video max-h-[62vh] rounded-3xl overflow-hidden bg-[#202124] shadow-lift ring-1 ring-black/5">
        <AnimatePresence>
          {recordState !== 'playback' && recordState !== 'interrupted' && (
            <motion.video
              key="camera"
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="absolute inset-0 w-full h-full object-cover"
              style={{ transform: 'scaleX(-1)' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
          )}
        </AnimatePresence>

        <AnimatePresence>
          {recordState === 'playback' && (
            <motion.video
              key="playback"
              ref={playbackRef}
              autoPlay
              loop
              playsInline
              muted
              className="absolute inset-0 w-full h-full object-cover"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
          )}
        </AnimatePresence>

        {/* framing guide */}
        {recordState === 'preview' && (
          <div className="absolute inset-[8%] rounded-[2rem] border-2 border-dashed border-white/35 pointer-events-none" />
        )}

        <AnimatePresence>
          {recordState === 'interrupted' && (
            <motion.div
              key="interrupted"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col items-center justify-center gap-4 px-6 text-center bg-canvas"
            >
              <h2 className="text-2xl sm:text-3xl font-bold text-ink">Kayıt yarıda kesildi</h2>
              <p className="text-muted text-lg">Kamera bağlantısı koptu. Videoyu tekrar çek.</p>
              <button onClick={handleRetakeAfterInterrupt} className="btn-primary mt-2">
                <RetryIcon className="w-5 h-5" /> Tekrar çek
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {recordState === 'countdown' && <CountdownTimer count={countdown} />}

        {recordState === 'recording' && (
          <div className="absolute top-4 left-4 flex items-center gap-2 bg-white/90 rounded-full px-3.5 py-1.5 shadow">
            <motion.div
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="w-2.5 h-2.5 rounded-full bg-google-red"
            />
            <span className="text-ink font-semibold text-sm">REC</span>
          </div>
        )}

        {recordState === 'playback' && (
          <div className="absolute top-4 left-4 bg-white/90 rounded-full px-3.5 py-1.5 shadow">
            <span className="text-ink font-semibold text-sm">Önizleme</span>
          </div>
        )}

        {!isReady && recordState === 'preview' && (
          <div className="absolute inset-0 flex items-center justify-center text-white/70">Kamera açılıyor...</div>
        )}
      </div>

      {/* Controls */}
      {recordState !== 'interrupted' && (
        <div className="flex items-center justify-center pt-5 min-h-[112px]">
          {recordState === 'preview' && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center gap-2">
              <button
                onClick={handleRecord}
                disabled={!isReady}
                className="w-20 h-20 rounded-full bg-white border-4 border-line flex items-center justify-center shadow-card disabled:opacity-50 hover:border-[#EA4335]/40 transition-colors"
                aria-label="Kaydet"
              >
                <div className="w-14 h-14 rounded-full bg-google-red" />
              </button>
              <p className="text-muted text-sm">Kaydetmek için dokun</p>
            </motion.div>
          )}

          {recordState === 'countdown' && (
            <div className="w-20 h-20 rounded-full bg-white border-4 border-faint flex items-center justify-center">
              <div className="w-14 h-14 rounded-full bg-google-red/30" />
            </div>
          )}

          {recordState === 'recording' && (
            <ProgressRing progress={recordProgress} size={84} strokeWidth={5} color="#EA4335">
              <div className="w-9 h-9 rounded-lg bg-google-red" />
            </ProgressRing>
          )}

          {recordState === 'playback' && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 w-full sm:w-auto">
              <button onClick={handleRetake} className="btn-secondary flex-1 sm:flex-none">
                <RetryIcon className="w-5 h-5" /> Tekrar çek
              </button>
              <button onClick={handleNext} className="btn-primary flex-1 sm:flex-none">
                Next <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
