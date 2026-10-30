import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';

export type AlertType = 'error' | 'warning' | 'info' | 'success';

interface AlertBannerProps {
  type?: AlertType;
  title?: string;
  message: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

const styles: Record<
  AlertType,
  { container: string; icon: React.ReactNode; text: string; close: string }
> = {
  error: {
    container: 'bg-rose-50 dark:bg-rose-950/50 border-rose-200 dark:border-rose-900',
    icon: <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />,
    text: 'text-rose-900 dark:text-rose-200',
    close: 'text-rose-600 hover:text-rose-800 dark:text-rose-400 dark:hover:text-rose-200',
  },
  warning: {
    container: 'bg-amber-50 dark:bg-amber-950/50 border-amber-200 dark:border-amber-900',
    icon: <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />,
    text: 'text-amber-900 dark:text-amber-200',
    close: 'text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-200',
  },
  info: {
    container: 'bg-sky-50 dark:bg-sky-950/50 border-sky-200 dark:border-sky-900',
    icon: <Info className="w-5 h-5 text-sky-600 dark:text-sky-400 shrink-0" />,
    text: 'text-sky-900 dark:text-sky-200',
    close: 'text-sky-600 hover:text-sky-800 dark:text-sky-400 dark:hover:text-sky-200',
  },
  success: {
    container: 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-200 dark:border-emerald-900',
    icon: <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />,
    text: 'text-emerald-900 dark:text-emerald-200',
    close: 'text-emerald-600 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-200',
  },
};

export const AlertBanner: React.FC<AlertBannerProps> = ({
  type = 'info',
  title,
  message,
  onClose,
  className = '',
}) => {
  const currentStyle = styles[type];

  return (
    <div
      className={`p-4 rounded-xl border flex items-start gap-3 transition-all ${currentStyle.container} ${className}`}
      role="alert"
    >
      {currentStyle.icon}
      <div className={`flex-1 text-sm ${currentStyle.text}`}>
        {title && <h4 className="font-semibold mb-1">{title}</h4>}
        <div>{message}</div>
      </div>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className={`p-1 rounded-lg transition-colors ${currentStyle.close}`}
          aria-label="Dismiss alert"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
