// Requirements 43.1, 43.7, 43.8: UI presentation and currency conversion.
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Button } from '../src/components/ui/button';
import { money } from '../src/lib/format';

describe('editable accessible primitives', () => {
  it('supports keyboard-compatible selected controls', () => {
    let clicked = false;
    render(<Button aria-pressed onClick={() => { clicked = true; }}>Normal</Button>);
    fireEvent.click(screen.getByRole('button', { name: 'Normal' }));
    expect(clicked).toBe(true);
    expect(screen.getByRole('button').getAttribute('aria-pressed')).toBe('true');
  });
  it('converts only presentation and preserves missing values', () => {
    expect(money(111.65, 'EUR', 1.1165)).toContain('100');
    expect(money(111.65, 'USD', 1.1165)).toContain('112');
    expect(money(null, 'USD', 1.1165)).toBe('Unavailable');
  });
});
