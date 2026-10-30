import React from 'react';

interface PageHeaderProps {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  icon,
  badge,
  actions,
}) => {
  return (
    <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-2xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900 shadow-sm shrink-0">
          {icon}
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">
              {title}
            </h1>
            {badge}
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
            {subtitle}
          </p>
        </div>
      </div>
      {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
    </div>
  );
};
