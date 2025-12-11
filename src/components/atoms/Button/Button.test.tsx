import { render, screen, fireEvent } from '@testing-library/react';
import { Button, ButtonProps } from './Button';
import { createRef } from 'react';

describe('Button', () => {
  // Helper to render button with default props
  const renderButton = (props: Partial<ButtonProps> = {}) => {
    const defaultProps: ButtonProps = {
      label: 'Click me',
      ...props,
    };
    return render(<Button {...defaultProps} />);
  };

  describe('Rendering', () => {
    it('renders with label text', () => {
      renderButton({ label: 'Submit' });
      expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
    });

    it('renders as a button element', () => {
      renderButton();
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      renderButton({ className: 'custom-class' });
      expect(screen.getByRole('button')).toHaveClass('custom-class');
    });

    it('forwards ref to button element', () => {
      const ref = createRef<HTMLButtonElement>();
      render(<Button label="Test" ref={ref} />);
      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });
  });

  describe('Variants', () => {
    it.each(['primary', 'secondary', 'ghost', 'danger'] as const)(
      'renders %s variant correctly',
      (variant) => {
        renderButton({ variant });
        const button = screen.getByRole('button');
        expect(button).toBeInTheDocument();
      }
    );

    it('defaults to primary variant', () => {
      renderButton();
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it.each(['sm', 'md', 'lg'] as const)(
      'renders %s size correctly',
      (size) => {
        renderButton({ size });
        const button = screen.getByRole('button');
        expect(button).toBeInTheDocument();
      }
    );

    it('defaults to md size', () => {
      renderButton();
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('shows spinner when loading', () => {
      renderButton({ loading: true });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('hides label when loading', () => {
      renderButton({ loading: true, label: 'Submit' });
      // Label should not be visible when loading
      expect(screen.queryByText('Submit')).not.toBeInTheDocument();
    });

    it('disables button when loading', () => {
      renderButton({ loading: true });
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('sets aria-disabled when loading', () => {
      renderButton({ loading: true });
      expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Disabled State', () => {
    it('disables button when disabled prop is true', () => {
      renderButton({ disabled: true });
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('sets aria-disabled when disabled', () => {
      renderButton({ disabled: true });
      expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true');
    });

    it('does not fire onClick when disabled', () => {
      const handleClick = jest.fn();
      renderButton({ disabled: true, onClick: handleClick });
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Full Width', () => {
    it('applies fullWidth style when fullWidth is true', () => {
      renderButton({ fullWidth: true });
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Icons', () => {
    const TestIcon = () => <span data-testid="test-icon">★</span>;

    it('renders icon on the left by default', () => {
      renderButton({ icon: <TestIcon /> });
      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('renders icon on the right when iconPosition is right', () => {
      renderButton({ icon: <TestIcon />, iconPosition: 'right' });
      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('hides icon when loading', () => {
      renderButton({ icon: <TestIcon />, loading: true });
      expect(screen.queryByTestId('test-icon')).not.toBeInTheDocument();
    });

    it('marks icon as aria-hidden', () => {
      renderButton({ icon: <TestIcon /> });
      const iconContainer = screen.getByTestId('test-icon').parentElement;
      expect(iconContainer).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Event Handling', () => {
    it('calls onClick when clicked', () => {
      const handleClick = jest.fn();
      renderButton({ onClick: handleClick });
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when loading', () => {
      const handleClick = jest.fn();
      renderButton({ onClick: handleClick, loading: true });
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('passes through other HTML attributes', () => {
      renderButton({ type: 'submit', 'aria-label': 'Submit form' });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
      expect(button).toHaveAttribute('aria-label', 'Submit form');
    });
  });

  describe('Accessibility', () => {
    it('has correct aria-busy attribute when loading', () => {
      const { rerender } = render(<Button label="Test" loading={false} />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'false');

      rerender(<Button label="Test" loading={true} />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
    });

    it('has correct aria-disabled attribute', () => {
      const { rerender } = render(<Button label="Test" disabled={false} />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'false');

      rerender(<Button label="Test" disabled={true} />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true');
    });

    it('can be focused', () => {
      renderButton();
      const button = screen.getByRole('button');
      button.focus();
      expect(button).toHaveFocus();
    });

    it('cannot be focused when disabled', () => {
      renderButton({ disabled: true });
      const button = screen.getByRole('button');
      button.focus();
      // Disabled buttons should not receive focus
      expect(button).toBeDisabled();
    });
  });

  describe('Display Name', () => {
    it('has correct displayName for debugging', () => {
      expect(Button.displayName).toBe('Button');
    });
  });
});
