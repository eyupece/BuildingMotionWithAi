import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { QRCodeSVG } from 'qrcode.react';
import { Pipeline, type StageKey } from '../components/Pipeline';
import { ArrowRight, QrIcon, RetryIcon, SparkIcon } from '../components/Icons';
import { PROCESSING_TIPS, getMockAvatarImageUrl } from '../mockData';
import { useApi, API_BASE } from '../hooks/useApi';
import type { AnalysisResult } from '../hooks/useApi';
import type { AvatarStyle, LocationTheme } from '../types';
import { isPosterStyle } from '../events';
import { DEMOS } from './DemoScreen';

interface ProcessingScreenProps {
  style: AvatarStyle;
  theme: LocationTheme;
  onComplete: (avatarImageUrl: string, videoUrl: string | null, videoId: string, shareUrl: string) => void;
  onError: () => void;
  onDemo: () => void;
  onNextPerson: () => void;
  recordedVideoUrl: string;
  recordedBlob: Blob | null;
}

type Phase = 'analyzing' | 'creating' | 'generating';

const TOTAL_POLL_ESTIMATE = 18;
const POLL_INTERVAL_MS = 5000;

export function ProcessingScreen({
  style,
  theme,
  onComplete,
  onError,
  onDemo,
  onNextPerson,
  recordedVideoUrl,
  recordedBlob,
}: ProcessingScreenProps) {
  const [phase, setPhase] = useState<Phase>('analyzing');
  const [analysisLines, setAnalysisLines] = useState<string[]>([]);
  const [avatarImageUrl, setAvatarImageUrl] = useState<string | null>(null);
  const [showAvatar, setShowAvatar] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);
  const [fatalError, setFatalError] = useState(false);
  const [fatalErrorMessage, setFatalErrorMessage] = useState<string | null>(null);
  const [allApiFailed, setAllApiFailed] = useState(false);
  const [currentShareUrl, setCurrentShareUrl] = useState<string | null>(null);
  const { uploadVideo, analyzeVideo, generateAvatar, generateVideo, pollStatus } = useApi();

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      let analysis: AnalysisResult | null = null;
      let videoId: string | null = null;
      let shareUrl: string | null = null;
      let apiSucceeded = false;

      // Phase 1: Analyzing
      setPhase('analyzing');

      if (recordedBlob) {
        try {
          const uploadResult = await uploadVideo(recordedBlob);
          if (cancelled) return;
          videoId = uploadResult.video_id;
          shareUrl = uploadResult.share_url;
          setCurrentShareUrl(uploadResult.share_url);

          analysis = await analyzeVideo(videoId, (phaseText) => {
            if (!cancelled) {
              setAnalysisLines((prev) => [...prev, phaseText]);
            }
          });
          apiSucceeded = true;
        } catch (err) {
          // Upload or analysis failed — surface the error
          if (!cancelled) {
            setFatalErrorMessage(err instanceof Error ? err.message : null);
            setFatalError(true);
          }
          return;
        }
      } else {
        const { ANALYSIS_LINES, mockDelay } = await import('../mockData');
        for (let i = 0; i <= ANALYSIS_LINES.length; i++) {
          if (cancelled) return;
          setAnalysisLines(ANALYSIS_LINES.slice(0, i));
          await mockDelay(800);
        }
        await mockDelay(1000);
      }

      if (cancelled) return;

      // Phase 2: Creating avatar
      setPhase('creating');
      let imgUrl = getMockAvatarImageUrl(style.color);

      if (videoId) {
        try {
          const { avatar_image_url } = await generateAvatar({
            video_id: videoId,
            avatar_style: style.id,
          });
          imgUrl = avatar_image_url;
          apiSucceeded = true;
        } catch {
          // Keep mock image on error
        }
      }

      if (cancelled) return;
      setAvatarImageUrl(imgUrl);
      setShowAvatar(true);
      await new Promise((r) => setTimeout(r, 1500));

      // Phase 3: Generating video
      if (cancelled) return;
      setPhase('generating');

      const resolvedVideoId = videoId ?? 'unknown';
      const resolvedShareUrl = shareUrl ?? `${API_BASE}/share/${resolvedVideoId}`;

      const tipInterval = setInterval(() => {
        if (!cancelled) {
          setTipIndex((i) => (i + 1) % PROCESSING_TIPS.length);
        }
      }, 3000);

      const MAX_POLL_RETRIES = 3;
      let resultUrl: string | null = null;

      try {
        const { operation_id } = await generateVideo({
          video_id: resolvedVideoId,
          avatar_image_url: imgUrl,
          motion_analysis: (analysis ?? {}) as Record<string, unknown>,
          avatar_style: style.id,
          location_theme: theme.id,
        });
        apiSucceeded = true;

        // Poll with retries — same operation_id, never re-generate
        let pollRetry = 0;
        while (pollRetry < MAX_POLL_RETRIES && !cancelled) {
          pollRetry++;
          if (pollRetry > 1) {
            setVideoProgress(0);
            // Wait a bit before retrying poll
            await new Promise((r) => setTimeout(r, 3000));
          }

          let attempts = 0;
          let pollFailed = false;
          while (!cancelled) {
            await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
            if (cancelled) break;

            const statusRes = await pollStatus(operation_id);
            attempts++;
            setVideoProgress(Math.min(attempts / TOTAL_POLL_ESTIMATE, 0.95));

            if (statusRes.status === 'complete') {
              if (statusRes.result_url) resultUrl = statusRes.result_url;
              pollFailed = false;
              break;
            }
            if (statusRes.status === 'failed') {
              pollFailed = true;
              break;
            }
          }

          if (!pollFailed) break; // Success — exit retry loop
          // pollFailed && more retries → loop back and re-poll
        }

        if (!cancelled) {
          setVideoProgress(1);
          await new Promise((r) => setTimeout(r, 500));
        }
      } catch (err) {
        // generateVideo() itself failed
        clearInterval(tipInterval);
        if (!cancelled) {
          setFatalErrorMessage(err instanceof Error ? err.message : null);
          setAllApiFailed(!apiSucceeded);
          setFatalError(true);
        }
        return;
      }

      clearInterval(tipInterval);

      if (!cancelled) {
        onComplete(imgUrl, resultUrl, resolvedVideoId, resolvedShareUrl);
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, [style, recordedVideoUrl, recordedBlob, onComplete]); // eslint-disable-line react-hooks/exhaustive-deps

  // Fatal error screen
  if (fatalError) {
    return (
      <div className="flex-1 flex items-center justify-center px-4 sm:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="card flex flex-col items-center gap-5 px-6 sm:px-12 py-10 text-center max-w-lg w-full"
        >
          <div className="w-20 h-20 rounded-full flex items-center justify-center bg-[#EA4335]/10 text-google-red">
            <SparkIcon className="w-9 h-9" />
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-ink">Bir şeyler ters gitti</h2>
          <p className="text-muted text-lg">Şu an yapay zeka servislerine bağlanamadık.</p>
          {fatalErrorMessage && (
            <p className="text-google-red text-xs font-mono w-full break-all px-3 py-2 rounded-xl bg-[#EA4335]/10">
              {fatalErrorMessage}
            </p>
          )}
          <div className="flex flex-col gap-3 w-full mt-2">
            <button onClick={onError} className="btn-primary w-full">
              <RetryIcon className="w-5 h-5" /> Tekrar dene
            </button>
            {allApiFailed && DEMOS.length > 0 && (
              <button onClick={onDemo} className="btn-secondary w-full">Demo izle</button>
            )}
          </div>
        </motion.div>
      </div>
    );
  }

  const stage: StageKey =
    phase === 'analyzing' ? (currentShareUrl ? 'gemini' : 'upload') : phase === 'creating' ? 'banana' : 'veo';

  return (
    <div className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-8 pt-2 pb-6 flex flex-col gap-5">
      <div className="card px-4 sm:px-8 py-5">
        <Pipeline current={stage} />
      </div>

      <div className="flex-1 grid lg:grid-cols-[1fr_340px] gap-5 min-h-0">
        {/* Stage content */}
        <div className="card relative overflow-hidden flex items-center justify-center px-5 sm:px-10 py-8 min-h-[360px]">
          <AnimatePresence mode="wait">
            {phase === 'analyzing' && (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                className="w-full max-w-2xl flex flex-col gap-5"
              >
                <div>
                  <p className="eyebrow mb-1" style={{ color: '#A142F4' }}>{currentShareUrl ? 'Gemini' : 'Yükleniyor'}</p>
                  <h2 className="text-2xl sm:text-3xl font-bold text-ink">Hareketin analiz ediliyor</h2>
                </div>
                <div className="grid sm:grid-cols-[160px_1fr] gap-4 items-stretch">
                  <video
                    src={recordedVideoUrl}
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="hidden sm:block w-full h-full max-h-48 object-cover rounded-2xl bg-faint"
                  />
                  <div className="rounded-2xl bg-[#202124] p-4 sm:p-5 font-mono text-[13px] sm:text-sm min-h-[176px]">
                    <div className="text-[#9AA0A6] mb-2">{'// motion_analysis.json'}</div>
                    {analysisLines.length === 0 && (
                      <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1.2, repeat: Infinity }} className="text-[#9AA0A6]">
                        waiting for Gemini...
                      </motion.div>
                    )}
                    {analysisLines.map((line, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3 }}
                        className="flex gap-2 leading-relaxed"
                      >
                        <span style={{ color: '#C58AF9' }}>›</span>
                        <span className={i === analysisLines.length - 1 ? 'text-white' : 'text-[#BDC1C6]'}>{line}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {phase === 'creating' && (
              <motion.div
                key="creating"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                className="flex flex-col items-center gap-5 text-center"
              >
                <div>
                  <p className="eyebrow mb-1" style={{ color: '#E37400' }}>Nano Banana</p>
                  <h2 className="text-2xl sm:text-3xl font-bold text-ink">{style.name} avatarın çiziliyor</h2>
                </div>
                <div className="relative w-56 h-56 sm:w-64 sm:h-64 rounded-3xl overflow-hidden" style={{ background: `${style.color}18` }}>
                  {!showAvatar ? (
                    <motion.div
                      animate={{ x: ['-100%', '200%'] }}
                      transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                      className="absolute inset-y-0 w-1/2"
                      style={{ background: `linear-gradient(90deg, transparent 0%, ${style.color}55 50%, transparent 100%)` }}
                    />
                  ) : (
                    avatarImageUrl && (
                      <>
                        <motion.div
                          className="absolute inset-0 z-10 bg-white pointer-events-none"
                          initial={{ opacity: 0.9 }}
                          animate={{ opacity: 0 }}
                          transition={{ duration: 0.5, delay: 0.1 }}
                        />
                        <motion.img
                          src={avatarImageUrl}
                          alt="Avatarın"
                          className={`w-full h-full ${isPosterStyle(style.id) ? 'object-contain' : 'object-cover'}`}
                          initial={{ scale: 0.6, opacity: 0, filter: 'blur(20px)' }}
                          animate={{ scale: 1, opacity: 1, filter: 'blur(0px)' }}
                          transition={{
                            scale: { type: 'spring', stiffness: 180, damping: 18 },
                            opacity: { duration: 1.0, ease: 'easeOut' },
                            filter: { duration: 1.0, ease: 'easeOut' },
                          }}
                        />
                      </>
                    )
                  )}
                </div>
              </motion.div>
            )}

            {phase === 'generating' && (
              <motion.div
                key="generating"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                className="w-full max-w-xl flex flex-col items-center gap-6 text-center"
              >
                <div>
                  <p className="eyebrow mb-1" style={{ color: '#34A853' }}>Veo</p>
                  <h2 className="text-2xl sm:text-3xl font-bold text-ink">Sahne hazırlanıyor: {theme.name}</h2>
                </div>

                <div className="flex items-center gap-3 sm:gap-5">
                  {avatarImageUrl && (
                    <img src={avatarImageUrl} alt="Avatarın" className="w-28 h-28 sm:w-36 sm:h-36 rounded-2xl object-cover shadow-card" />
                  )}
                  <motion.div
                    animate={{ x: [0, 6, 0] }}
                    transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                    className="text-muted"
                  >
                    <ArrowRight className="w-6 h-6" />
                  </motion.div>
                  <img src={theme.previewImage} alt={theme.name} className="w-28 h-28 sm:w-36 sm:h-36 rounded-2xl object-cover shadow-card" />
                </div>

                <div className="w-full">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted">Video oluşturuluyor</span>
                    <span className="font-semibold text-ink">{Math.round(videoProgress * 100)}%</span>
                  </div>
                  <div className="h-2.5 w-full rounded-full bg-faint overflow-hidden">
                    <motion.div
                      className="h-full rounded-full bg-google-green"
                      animate={{ width: `${Math.max(videoProgress, 0.03) * 100}%` }}
                      transition={{ duration: 0.6, ease: 'easeOut' }}
                    />
                  </div>
                </div>

                <AnimatePresence mode="wait">
                  <motion.p
                    key={tipIndex}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.35 }}
                    className="text-muted text-sm"
                  >
                    {PROCESSING_TIPS[tipIndex]}
                  </motion.p>
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* QR + next person, as soon as the upload is done */}
        <div className="card flex flex-col items-center justify-center gap-4 p-6 text-center">
          {currentShareUrl ? (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center gap-4 w-full">
              <div className="flex lg:flex-col items-center gap-4 text-left lg:text-center">
                <div className="p-3 bg-white rounded-2xl border border-line flex-shrink-0">
                  <QRCodeSVG value={currentShareUrl} size={132} bgColor="#ffffff" fgColor="#202124" level="M" />
                </div>
                <div>
                  <p className="text-ink font-semibold text-lg">Telefonunla okut</p>
                  <p className="text-muted text-sm">Video hazır olunca orada açılacak. Burada beklemene gerek yok.</p>
                </div>
              </div>
              <button onClick={onNextPerson} className="btn-secondary w-full">
                Sıradaki kişi
              </button>
            </motion.div>
          ) : (
            <div className="flex flex-col items-center gap-3 text-muted">
              <QrIcon className="w-10 h-10 text-line" />
              <p className="text-sm">Yükleme bitince QR kodun burada çıkacak.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
