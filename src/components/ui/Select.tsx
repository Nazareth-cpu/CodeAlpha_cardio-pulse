import React, { forwardRef, useId } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  description?: string;
  error?: string;
  options?: SelectOption[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      id: customId,
      label,
      description,
      error,
      required,
      disabled,
      options,
      children,
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const selectId = customId || generatedId;
    const errorId = `${selectId}-error`;
    const descriptionId = `${selectId}-desc`;

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={selectId}
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
          <select
            ref={ref}
            id={selectId}
            required={required}
            disabled={disabled}
            aria-invalid={Boolean(error)}
            aria-describedby={cn(error ? errorId : undefined, description ? descriptionId : undefined)}
            className={cn(
              'w-full bg-white rounded-lg border text-sm text-[#12231E] transition-colors appearance-none cursor-pointer',
              'py-2 pl-3 pr-9 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1',
              error
                ? 'border-rose-400 focus-visible:border-rose-500 focus-visible:ring-rose-500'
                : 'border-slate-200 hover:border-slate-300 focus-visible:border-[#087F5B] focus-visible:ring-[#087F5B]',
              disabled && 'bg-slate-50 text-slate-400 cursor-not-allowed border-slate-200',
              className,
            )}
            {...props}
          >
            {options
              ? options.map((opt) => (
                  <option key={opt.value} value={opt.value} disabled={opt.disabled}>
                    {opt.label}
                  </option>
                ))
              : children}
          </select>

          <ChevronDown
            className="w-4 h-4 text-slate-400 absolute right-3 pointer-events-none"
            aria-hidden="true"
          />
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

Select.displayName = 'Select';
