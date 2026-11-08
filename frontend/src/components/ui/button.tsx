// Editable shadcn/ui Button, adapted to the canonical Stitch proportions.
import * as React from 'react';
import { Slot } from 'radix-ui';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';

const buttonVariants = cva('button inline-flex items-center justify-center gap-2 disabled:pointer-events-none disabled:opacity-50', {
  variants: { variant: { default: 'button-primary', outline: 'button-outline', ghost: 'button-ghost' } },
  defaultVariants: { variant: 'outline' },
});
export function Button({ className, variant, asChild = false, ...props }: React.ComponentProps<'button'> & VariantProps<typeof buttonVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot.Root : 'button';
  return <Comp type="button" className={cn(buttonVariants({ variant, className }))} {...props} />;
}
