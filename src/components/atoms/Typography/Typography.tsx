import { ReactNode, ElementType } from 'react';
import clsx from 'clsx';
import styles from './Typography.module.css';

type TypographyVariant =
  | 'h1'
  | 'h2'
  | 'h3'
  | 'h4'
  | 'h5'
  | 'h6'
  | 'body-lg'
  | 'body'
  | 'body-sm'
  | 'caption'
  | 'overline'
  | 'label';

type TypographyColor =
  | 'primary'
  | 'secondary'
  | 'muted'
  | 'inverse'
  | 'error'
  | 'success';

export interface TypographyProps {
  /** Content to render */
  children: ReactNode;
  /** Typography style variant */
  variant?: TypographyVariant;
  /** Override the root element */
  as?: ElementType;
  /** Text color */
  color?: TypographyColor;
  /** Additional CSS class */
  className?: string;
  /** ID for accessibility */
  id?: string;
}

const variantToTag: Record<TypographyVariant, ElementType> = {
  h1: 'h1',
  h2: 'h2',
  h3: 'h3',
  h4: 'h4',
  h5: 'h5',
  h6: 'h6',
  'body-lg': 'p',
  body: 'p',
  'body-sm': 'p',
  caption: 'span',
  overline: 'span',
  label: 'span',
};

export const Typography = ({
  children,
  variant = 'body',
  as,
  color = 'primary',
  className,
  id,
}: TypographyProps) => {
  const Component = as || variantToTag[variant];

  return (
    <Component
      id={id}
      className={clsx(
        styles.typography,
        styles[variant],
        styles[`color-${color}`],
        className
      )}
    >
      {children}
    </Component>
  );
};

Typography.displayName = 'Typography';
export default Typography;
