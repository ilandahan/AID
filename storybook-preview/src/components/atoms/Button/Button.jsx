import React from 'react';

/**
 * Button - Atomic Design: Atom
 *
 * A basic button component that serves as a building block
 * for more complex UI patterns.
 */
export const Button = ({
  label,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
  ...props
}) => {
  const baseStyles = {
    fontFamily: 'inherit',
    fontWeight: 600,
    border: 'none',
    borderRadius: '4px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    transition: 'all 0.2s ease',
  };

  const sizeStyles = {
    small: { padding: '8px 16px', fontSize: '12px' },
    medium: { padding: '12px 24px', fontSize: '14px' },
    large: { padding: '16px 32px', fontSize: '16px' },
  };

  const variantStyles = {
    primary: { backgroundColor: '#3B82F6', color: 'white' },
    secondary: { backgroundColor: '#6B7280', color: 'white' },
    outline: { backgroundColor: 'transparent', color: '#3B82F6', border: '2px solid #3B82F6' },
  };

  const style = {
    ...baseStyles,
    ...sizeStyles[size],
    ...variantStyles[variant],
  };

  return (
    <button
      type="button"
      style={style}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {label}
    </button>
  );
};

export default Button;
