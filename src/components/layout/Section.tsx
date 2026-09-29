import React from 'react';
import { cn } from '../../lib/utils';

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  title?: string;
  description?: string;
  headerAction?: React.ReactNode;
}

export function Section({
  className,
  title,
  description,
  headerAction,
  children,
  ...props
}: SectionProps) {
  return (
    <section className={cn('py-6 sm:py-8', className)} {...props}>
      {(title || description || headerAction) && (
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
          <div>
            {title && (
              <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-[#12231E]">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-xs sm:text-sm text-[#65756F] mt-1 max-w-2xl leading-relaxed">
                {description}
              </p>
            )}
          </div>
          {headerAction && <div className="shrink-0">{headerAction}</div>}
        </div>
      )}
      {children}
    </section>
  );
}
