import React from 'react';

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export const ScoreBadge: React.FC<ScoreBadgeProps> = ({ score, size = 'md' }) => {
  let colorClasses = 'from-emerald-500 to-teal-600 text-white shadow-emerald-500/20';
  if (score < 50) {
    colorClasses = 'from-rose-500 to-red-600 text-white shadow-rose-500/20';
  } else if (score < 75) {
    colorClasses = 'from-amber-500 to-orange-600 text-white shadow-amber-500/20';
  }

  const sizeClasses = {
    sm: 'px-2.5 py-1 text-xs font-bold',
    md: 'px-3.5 py-1.5 text-sm font-extrabold',
    lg: 'px-5 py-2.5 text-lg font-black',
  }[size];

  return (
    <div
      className={`inline-flex items-center rounded-xl bg-gradient-to-r ${colorClasses} ${sizeClasses} shadow-md tracking-tight`}
    >
      <span>{score.toFixed(1)}%</span>
    </div>
  );
};
