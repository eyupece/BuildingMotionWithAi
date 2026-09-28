import { useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface DemoScreenProps {
  onTryAgain: () => void;
}

const DEMOS = [
  { label: 'Pixel Hero', file: '/demos/pixel-hero.mp4' },
  { label: 'Cyber Nova', file: '/demos/cyber-nova.mp4' },
  { label: 'Watercolor Dream', file: '/demos/watercolor-dream.mp4' },
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
        <h1 className="text-3xl sm:text-4xl font-bold text-ink tracking-tight">Demo mode</h1>
        <p className="text-muted mt-1">A few videos made with Gemini Motion Lab</p>
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

      <div className="grid grid-cols-3 gap-2 sm:gap-3">
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

      <button onClick={onTryAgain} className="btn-primary w-full">Try Again</button>
    </div>
  );
}
