import React, { forwardRef, useId } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  error?: string;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      id: customId,
      label,
      description,
      error,
      required,
      disabled,
      leftAddon,
      rightAddon,
      type = 'text',
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const inputId = customId || generatedId;
    const errorId = `${inputId}-error`;
    const descriptionId = `${inputId}-desc`;

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-semibold text-[#12231E] tracking-tight flex items-center justify-between"
          >
            <span>
              {label}
              {required && <span className="text-rose-500 ml-0.5" aria-hidden="true">*</span>}
            </span>
          </label>
        )}

        {description && (
          <p id={descriptionId} className="text-xs text-[#65756F]">
            {description}
          </p>
        )}

        <div className="relative flex items-center">
          {leftAddon && (
            <div className="absolute left-3 flex items-center pointer-events-none text-slate-400">
              {leftAddon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            type={type}
            required={required}
            disabled={disabled}
            aria-invalid={Boolean(error)}
            aria-describedby={cn(error ? errorId : undefined, description ? descriptionId : undefined)}
            className={cn(
              'w-full bg-white rounded-lg border text-sm text-[#12231E] placeholder:text-slate-400 transition-colors',
              'py-2 px-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1',
              leftAddon ? 'pl-9' : 'pl-3',
              rightAddon ? 'pr-9' : 'pr-3',
              error
                ? 'border-rose-400 focus-visible:border-rose-500 focus-visible:ring-rose-500'
                : 'border-slate-200 hover:border-slate-300 focus-visible:border-[#087F5B] focus-visible:ring-[#087F5B]',
              disabled && 'bg-slate-50 text-slate-400 cursor-not-allowed border-slate-200',
              className,
            )}
            {...props}
          />

          {rightAddon && (
            <div className="absolute right-3 flex items-center pointer-events-none text-slate-400">
              {rightAddon}
            </div>
          )}
        </div>

        {error && (
          <p id={errorId} role="alert" className="text-xs text-rose-600 font-medium">
            {error}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';
