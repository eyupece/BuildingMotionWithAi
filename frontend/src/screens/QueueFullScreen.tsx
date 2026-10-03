import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { API_BASE } from '../hooks/useApi';

interface QueueFullScreenProps {
  onReady: () => void;
}

export function QueueFullScreen({ onReady }: QueueFullScreenProps) {
  const [activeJobs, setActiveJobs] = useState(0);
  const [maxJobs, setMaxJobs] = useState(3);
  const cancelledRef = useRef(false);

  useEffect(() => {
    cancelledRef.current = false;

    const poll = async () => {
      while (!cancelledRef.current) {
        try {
          const res = await fetch(`${API_BASE}/api/queue/status`);
          if (res.ok) {
            const data = await res.json();
            setActiveJobs(data.active_jobs);
            setMaxJobs(data.max_jobs);
            if (data.available) {
              onReady();
              return;
            }
          }
        } catch {
          // Network error — keep polling
        }
        await new Promise((r) => setTimeout(r, 3000));
      }
    };

    poll();
    return () => {
      cancelledRef.current = true;
    };
  }, [onReady]);

  return (
    <div className="flex-1 flex items-center justify-center px-4 sm:px-8 py-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="card flex flex-col items-center gap-5 px-6 sm:px-12 py-10 text-center max-w-lg w-full"
      >
        <h2 className="text-3xl sm:text-4xl font-bold text-ink">Şu an dolu</h2>
        <p className="text-muted text-lg">
          {maxJobs} video sırasının hepsi şu an kullanımda. Sıra birazdan sana gelecek.
        </p>

        <div className="flex items-center gap-3 mt-2">
          {Array.from({ length: maxJobs }).map((_, i) => (
            <motion.div
              key={i}
              animate={i < activeJobs ? { opacity: [0.5, 1, 0.5] } : { opacity: 1 }}
              transition={i < activeJobs ? { duration: 1.5, repeat: Infinity, ease: 'easeInOut', delay: i * 0.3 } : {}}
              className="w-12 h-3 rounded-full"
              style={{ background: i < activeJobs ? '#34A853' : '#E8EAED' }}
            />
          ))}
        </div>
        <p className="text-muted text-sm">{activeJobs}/{maxJobs} video işleniyor</p>

        <motion.p
          animate={{ opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          className="text-muted text-sm"
        >
          Boş yer bekleniyor...
        </motion.p>
      </motion.div>
    </div>
  );
}
