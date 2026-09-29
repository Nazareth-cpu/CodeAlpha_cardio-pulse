import React, { forwardRef, useId } from 'react';
import { Check } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  description?: string;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      className,
      id: customId,
      label,
      description,
      error,
      checked,
      disabled,
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const checkboxId = customId || generatedId;
    const descId = `${checkboxId}-desc`;

    return (
      <div className="flex items-start gap-2.5">
        <div className="relative flex items-center justify-center mt-0.5">
          <input
            ref={ref}
            id={checkboxId}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            aria-describedby={description ? descId : undefined}
            className={cn(
              'peer h-4 w-4 shrink-0 rounded border border-slate-300 bg-white appearance-none cursor-pointer transition-colors',
              'checked:bg-[#087F5B] checked:border-[#087F5B]',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#087F5B] focus-visible:ring-offset-1',
              disabled && 'cursor-not-allowed bg-slate-100 border-slate-200',
              className,
            )}
            {...props}
          />
          <Check
            className="w-3 h-3 text-white pointer-events-none absolute hidden peer-checked:block stroke-[3]"
            aria-hidden="true"
          />
        </div>

        {(label || description) && (
          <div className="flex flex-col">
            {label && (
              <label
                htmlFor={checkboxId}
                className={cn(
                  'text-xs font-semibold text-[#12231E] cursor-pointer select-none',
                  disabled && 'cursor-not-allowed opacity-60',
                )}
              >
                {label}
              </label>
            )}
            {description && (
              <p id={descId} className="text-xs text-[#65756F]">
                {description}
              </p>
            )}
            {error && (
              <p role="alert" className="text-xs text-rose-600 font-medium mt-0.5">
                {error}
              </p>
            )}
          </div>
        )}
      </div>
    );
  },
);

Checkbox.displayName = 'Checkbox';
