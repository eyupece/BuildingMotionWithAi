import { useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface DemoScreenProps {
  onTryAgain: () => void;
}

// Videos in public/demos, shown if the AI services are down during a live demo
export const DEMOS = [
  { label: 'Trabzon Afişi', file: '/demos/trabzon-afis.mp4' },
];

export function DemoScreen({ onTryAgain }: DemoScreenProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleSelect = (i: number) => {
    setActiveIndex(i);
    setTimeout(() => {
      if (videoRef.current) {
        videoRef.current.load();
        videoRef.current.play();
      }
    }, 50);
  };

  return (
    <div className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-8 pt-2 pb-6 flex flex-col gap-5">
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold text-ink tracking-tight">Demo modu</h1>
        <p className="text-muted mt-1">Bu demoyla yapılmış birkaç video</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.15 }}
        className="card p-2 flex-1 min-h-[260px]"
      >
        <video
          ref={videoRef}
          key={DEMOS[activeIndex].file}
          src={DEMOS[activeIndex].file}
          autoPlay
          loop
          playsInline
          muted
          className="w-full h-full max-h-[55vh] object-contain rounded-2xl bg-[#202124]"
        />
      </motion.div>

      {DEMOS.length > 1 && (
      <div className="grid gap-2 sm:gap-3" style={{ gridTemplateColumns: `repeat(${DEMOS.length}, minmax(0, 1fr))` }}>
        {DEMOS.map((demo, i) => (
          <button
            key={demo.file}
            onClick={() => handleSelect(i)}
            className="py-3 rounded-2xl text-sm sm:text-base font-semibold border-2 transition-colors"
            style={{
              background: activeIndex === i ? '#E8F0FE' : '#FFFFFF',
              borderColor: activeIndex === i ? '#4285F4' : '#DADCE0',
              color: activeIndex === i ? '#1967D2' : '#5F6368',
            }}
          >
            {demo.label}
          </button>
        ))}
      </div>
      )}

      <button onClick={onTryAgain} className="btn-primary w-full">Tekrar dene</button>
    </div>
  );
}
