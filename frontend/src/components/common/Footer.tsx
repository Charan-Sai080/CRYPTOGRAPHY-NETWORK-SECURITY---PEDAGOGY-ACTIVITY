import React from 'react';
import { BookOpen, ExternalLink, ShieldCheck, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm transition-colors py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>
              Cryptography & Network Security (CNS) Pedagogy Activity &bull; Academic Lab Platform
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>FastAPI Swagger Docs</span>
              <ExternalLink className="w-3 h-3 opacity-60" />
            </a>
            <span>&bull;</span>
            <span>MIT License</span>
            <span>&bull;</span>
            <span className="inline-flex items-center gap-1">
              Engineered with <Heart className="w-3 h-3 text-rose-500 fill-rose-500" /> for Cryptographic Learning
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
