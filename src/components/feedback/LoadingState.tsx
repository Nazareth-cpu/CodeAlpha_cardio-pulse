import React from 'react';
import { Spinner } from '../ui/Spinner';
import { cn } from '../../lib/utils';

export interface LoadingStateProps {
  message?: string;
  subtext?: string;
  isFullScreen?: boolean;
  className?: string;
}

export function LoadingState({
  message = 'Loading data...',
  subtext,
  isFullScreen = false,
  className,
}: LoadingStateProps) {
  return (
    <div
      role="status"
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center',
        isFullScreen ? 'fixed inset-0 z-50 bg-[#F6FAF8]/90 backdrop-blur-xs' : 'py-16',
        className,
      )}
    >
      <Spinner size="lg" label={message} />
      <p className="text-sm font-semibold text-[#12231E] mt-4">{message}</p>
      {subtext && <p className="text-xs text-[#65756F] mt-1">{subtext}</p>}
    </div>
  );
}
