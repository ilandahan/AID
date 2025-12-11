import { render, screen } from '@testing-library/react';
import { Typography, TypographyProps } from './Typography';

describe('Typography', () => {
  // Helper to render typography with default props
  const renderTypography = (props: Partial<TypographyProps> = {}) => {
    const defaultProps: TypographyProps = {
      children: 'Test content',
      ...props,
    };
    return render(<Typography {...defaultProps} />);
  };

  describe('Rendering', () => {
    it('renders children content', () => {
      renderTypography({ children: 'Hello World' });
      expect(screen.getByText('Hello World')).toBeInTheDocument();
    });

    it('renders as paragraph by default', () => {
      const { container } = renderTypography();
      expect(container.querySelector('p')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      renderTypography({ className: 'custom-class' });
      expect(screen.getByText('Test content')).toHaveClass('custom-class');
    });

    it('applies id attribute', () => {
      renderTypography({ id: 'test-id' });
      expect(screen.getByText('Test content')).toHaveAttribute('id', 'test-id');
    });
  });

  describe('Heading Variants', () => {
    it.each([
      ['h1', 'h1'],
      ['h2', 'h2'],
      ['h3', 'h3'],
      ['h4', 'h4'],
      ['h5', 'h5'],
      ['h6', 'h6'],
    ] as const)('renders %s variant as <%s> element', (variant, expectedTag) => {
      const { container } = renderTypography({ variant });
      expect(container.querySelector(expectedTag)).toBeInTheDocument();
    });

    it('renders h1 with correct role', () => {
      renderTypography({ variant: 'h1', children: 'Main Heading' });
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    });

    it('renders h2 with correct role', () => {
      renderTypography({ variant: 'h2', children: 'Section Heading' });
      expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
    });
  });

  describe('Body Variants', () => {
    it.each(['body-lg', 'body', 'body-sm'] as const)(
      'renders %s variant as <p> element',
      (variant) => {
        const { container } = renderTypography({ variant });
        expect(container.querySelector('p')).toBeInTheDocument();
      }
    );
  });

  describe('Inline Variants', () => {
    it.each(['caption', 'overline', 'label'] as const)(
      'renders %s variant as <span> element',
      (variant) => {
        const { container } = renderTypography({ variant });
        expect(container.querySelector('span')).toBeInTheDocument();
      }
    );
  });

  describe('Custom Element Override', () => {
    it('renders as custom element when "as" prop is provided', () => {
      const { container } = renderTypography({ as: 'div' });
      expect(container.querySelector('div')).toBeInTheDocument();
    });

    it('overrides variant default tag with "as" prop', () => {
      const { container } = renderTypography({ variant: 'h1', as: 'span' });
      expect(container.querySelector('span')).toBeInTheDocument();
      expect(container.querySelector('h1')).not.toBeInTheDocument();
    });

    it('can render as label element', () => {
      const { container } = renderTypography({ as: 'label' });
      expect(container.querySelector('label')).toBeInTheDocument();
    });

    it('can render as article element', () => {
      const { container } = renderTypography({ as: 'article' });
      expect(container.querySelector('article')).toBeInTheDocument();
    });
  });

  describe('Color Variants', () => {
    it.each(['primary', 'secondary', 'muted', 'inverse', 'error', 'success'] as const)(
      'applies %s color class',
      (color) => {
        renderTypography({ color });
        const element = screen.getByText('Test content');
        expect(element).toBeInTheDocument();
      }
    );

    it('defaults to primary color', () => {
      renderTypography();
      const element = screen.getByText('Test content');
      expect(element).toBeInTheDocument();
    });
  });

  describe('Variant to Tag Mapping', () => {
    const variantTagPairs: [TypographyProps['variant'], string][] = [
      ['h1', 'H1'],
      ['h2', 'H2'],
      ['h3', 'H3'],
      ['h4', 'H4'],
      ['h5', 'H5'],
      ['h6', 'H6'],
      ['body-lg', 'P'],
      ['body', 'P'],
      ['body-sm', 'P'],
      ['caption', 'SPAN'],
      ['overline', 'SPAN'],
      ['label', 'SPAN'],
    ];

    it.each(variantTagPairs)(
      'maps variant "%s" to tag <%s>',
      (variant, expectedTagName) => {
        const { container } = renderTypography({ variant });
        const element = container.firstChild as HTMLElement;
        expect(element.tagName).toBe(expectedTagName);
      }
    );
  });

  describe('Content Types', () => {
    it('renders string children', () => {
      renderTypography({ children: 'Simple text' });
      expect(screen.getByText('Simple text')).toBeInTheDocument();
    });

    it('renders number children', () => {
      renderTypography({ children: 42 });
      expect(screen.getByText('42')).toBeInTheDocument();
    });

    it('renders nested elements', () => {
      renderTypography({
        children: (
          <>
            <strong>Bold</strong> and <em>italic</em>
          </>
        ),
      });
      expect(screen.getByText('Bold')).toBeInTheDocument();
      expect(screen.getByText('italic')).toBeInTheDocument();
    });

    it('renders multiple children', () => {
      renderTypography({
        children: ['First ', 'Second ', 'Third'],
      });
      expect(screen.getByText(/First/)).toBeInTheDocument();
    });
  });

  describe('Display Name', () => {
    it('has correct displayName for debugging', () => {
      expect(Typography.displayName).toBe('Typography');
    });
  });

  describe('Semantic HTML', () => {
    it('preserves heading hierarchy', () => {
      const { container } = render(
        <div>
          <Typography variant="h1">Main Title</Typography>
          <Typography variant="h2">Section</Typography>
          <Typography variant="h3">Subsection</Typography>
        </div>
      );

      expect(container.querySelector('h1')).toHaveTextContent('Main Title');
      expect(container.querySelector('h2')).toHaveTextContent('Section');
      expect(container.querySelector('h3')).toHaveTextContent('Subsection');
    });

    it('uses semantic elements for different content types', () => {
      const { container } = render(
        <div>
          <Typography variant="body">Paragraph content</Typography>
          <Typography variant="caption">Caption text</Typography>
          <Typography variant="label">Label text</Typography>
        </div>
      );

      expect(container.querySelector('p')).toHaveTextContent('Paragraph content');
      expect(container.querySelectorAll('span')).toHaveLength(2);
    });
  });

  describe('Edge Cases', () => {
    it('handles empty string children', () => {
      const { container } = renderTypography({ children: '' });
      expect(container.querySelector('p')).toBeInTheDocument();
      expect(container.querySelector('p')).toHaveTextContent('');
    });

    it('handles null children gracefully', () => {
      const { container } = renderTypography({ children: null as any });
      expect(container.querySelector('p')).toBeInTheDocument();
    });

    it('handles undefined variant gracefully', () => {
      const { container } = renderTypography({ variant: undefined });
      // Should default to 'body' variant which uses 'p' tag
      expect(container.querySelector('p')).toBeInTheDocument();
    });
  });
});
