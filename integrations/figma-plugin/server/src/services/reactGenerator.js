/**
 * @file reactGenerator.js
 * @description Generates React component files from Figma component data.
 *              Creates .tsx, .module.css, index.ts, and .test.tsx files.
 * @related
 *   - ./aidExporter.js - Main export logic, calls this generator
 *   - ../index.js - Server entry point
 * @created 2025-12-29
 */

const fs = require('fs');
const path = require('path');

// Always generate tests and storybook files (mandatory for design system quality)
const GENERATE_TESTS = true;
const GENERATE_STORYBOOK = true;

/**
 * Generate React component files from export data
 * @param {Object} exportData - The export data from aidExporter
 * @param {string} outputDir - Directory to write files to
 * @returns {Object} Result with generated file paths
 */
async function generateReactComponent(exportData, outputDir) {
  console.log('[ReactGenerator] 🚀 Starting React component generation...');
  console.log('[ReactGenerator] Input name:', exportData.name);
  console.log('[ReactGenerator] Output directory:', outputDir);

  const componentName = toPascalCase(exportData.name);
  const componentDir = path.join(outputDir, componentName);

  console.log('[ReactGenerator] Component name (PascalCase):', componentName);
  console.log('[ReactGenerator] Component directory:', componentDir);

  // Ensure component directory exists
  await fs.promises.mkdir(componentDir, { recursive: true });
  console.log('[ReactGenerator] ✅ Directory created/verified');

  const files = {
    component: path.join(componentDir, `${componentName}.tsx`),
    styles: path.join(componentDir, `${componentName}.module.css`),
    index: path.join(componentDir, 'index.ts'),
    types: path.join(componentDir, `${componentName}.types.ts`)
  };

  // Optionally add test file
  if (GENERATE_TESTS) {
    files.test = path.join(componentDir, `${componentName}.test.tsx`);
    console.log('[ReactGenerator] 📝 Test file will be generated');
  }

  // Optionally add Storybook story file
  if (GENERATE_STORYBOOK) {
    files.stories = path.join(componentDir, `${componentName}.stories.tsx`);
    console.log('[ReactGenerator] 📖 Storybook story will be generated');
  }

  console.log('[ReactGenerator] 📁 Files to generate:', Object.keys(files));

  // Generate all files
  const writePromises = [
    fs.promises.writeFile(files.component, generateComponentCode(exportData, componentName)),
    fs.promises.writeFile(files.styles, generateStylesCode(exportData, componentName)),
    fs.promises.writeFile(files.index, generateIndexCode(componentName)),
    fs.promises.writeFile(files.types, generateTypesCode(exportData, componentName))
  ];

  // Conditionally add test file generation
  if (GENERATE_TESTS) {
    writePromises.push(fs.promises.writeFile(files.test, generateTestCode(componentName)));
  }

  // Conditionally add Storybook story generation
  if (GENERATE_STORYBOOK) {
    writePromises.push(fs.promises.writeFile(files.stories, generateStoryCode(exportData, componentName)));
  }

  await Promise.all(writePromises);

  console.log(`[ReactGenerator] ✅ All files written successfully`);

  const generatedFiles = Object.keys(files).map(key => path.basename(files[key]));

  console.log('[ReactGenerator] 📋 Generated files list:', generatedFiles);
  console.log(`[ReactGenerator] ✨ React component generated at ${componentDir}`);

  return {
    success: true,
    componentName,
    componentDir,
    files: generatedFiles
  };
}

/**
 * Convert string to PascalCase
 */
function toPascalCase(str) {
  return str
    .split(/[\s\-_\/]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

/**
 * Convert string to kebab-case
 */
function toKebabCase(str) {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

/**
 * Generate the main component TSX file
 * Uses forwardRef pattern and clsx for className composition (atomic-design skill)
 */
function generateComponentCode(exportData, componentName) {
  const { metadata, variants = [] } = exportData;
  const hasVariants = variants.length > 0;
  const level = metadata?.level || 'molecule';
  const description = metadata?.description || `${componentName} component`;
  const ariaLabel = metadata?.ariaLabel || '';

  // Determine component type based on level
  const elementType = getElementType(level, componentName);

  // Get HTML element type for ref typing
  const refType = getRefType(elementType);

  // Generate variant default
  const defaultVariant = hasVariants ? (variants[0]?.name || variants[0] || 'default') : null;

  return `/**
 * @component ${componentName}
 * @description ${description}
 * @level ${level}
 * @generated Exported from Figma via AID Plugin
 */

import { forwardRef } from 'react';
import clsx from 'clsx';
import styles from './${componentName}.module.css';
import type { ${componentName}Props } from './${componentName}.types';

/**
 * ${componentName}
 *
 * ${description}
 */
export const ${componentName} = forwardRef<${refType}, ${componentName}Props>(
  (
    {
      className,
      children,${hasVariants ? `\n      variant = '${defaultVariant}',` : ''}
      'data-testid': testId,
      ...props
    },
    ref
  ) => {
    return (
      <${elementType}
        ref={ref}
        className={clsx(
          styles['${toKebabCase(componentName)}'],${hasVariants ? `\n          variant && styles[\`variant-\${variant}\`],` : ''}
          className
        )}
        data-testid={testId || '${toKebabCase(componentName)}'}${ariaLabel ? `\n        aria-label="${ariaLabel}"` : ''}
        {...props}
      >
        {children}
      </${elementType}>
    );
  }
);

${componentName}.displayName = '${componentName}';

export default ${componentName};
`;
}

/**
 * Generate the CSS module file
 * Uses CSS custom properties (variables) for design tokens (atomic-design skill)
 */
function generateStylesCode(exportData, componentName) {
  const { tokens = [], variants = [], metadata } = exportData;
  const kebabName = toKebabCase(componentName);
  const level = metadata?.level || 'molecule';

  // Extract design tokens as CSS custom properties
  const tokenVariables = tokens
    .filter(t => t.type && t.value && t.name)
    .map(token => {
      const varName = `--${kebabName}-${toKebabCase(token.name || token.type)}`;
      const cssValue = tokenValueToCss(token.value, token.type);
      return cssValue ? `  ${varName}: ${cssValue};` : null;
    })
    .filter(Boolean)
    .join('\n');

  // Generate styles using the CSS variables
  const tokenStyles = tokens
    .filter(t => t.type && t.value && t.name)
    .map(token => {
      const cssProperty = tokenTypeToCssProperty(token.type);
      const varName = `--${kebabName}-${toKebabCase(token.name || token.type)}`;
      return cssProperty ? `  ${cssProperty}: var(${varName});` : null;
    })
    .filter(Boolean)
    .join('\n');

  // Generate variant styles with CSS variables
  const variantStyles = variants
    .map(v => {
      const variantName = typeof v === 'string' ? v : v.name;
      const variantKebab = toKebabCase(variantName);
      return `.variant-${variantKebab} {
  /* Variant: ${variantName} */
  /* Override CSS variables here for variant-specific styling */
}`;
    })
    .join('\n\n');

  // Determine appropriate responsive breakpoints based on level
  const responsiveStyles = getResponsiveStyles(level, kebabName);

  return `/**
 * ${componentName} Styles
 * @level ${level}
 * @generated Exported from Figma via AID Plugin
 *
 * Uses CSS custom properties for theming flexibility.
 * Override variables in parent scope to customize appearance.
 */

/* CSS Custom Properties (Design Tokens) */
.${kebabName} {
${tokenVariables || '  /* No design tokens exported */'}
}

/* Base Component Styles */
.${kebabName} {
  box-sizing: border-box;
  position: relative;
${tokenStyles ? '\n' + tokenStyles : ''}
}

/* Variant Styles */
${variantStyles || '/* No variants defined */'}

/* Interactive States */
.${kebabName}:focus-visible {
  outline: 2px solid var(--color-focus, #0066cc);
  outline-offset: 2px;
}

/* Responsive Styles */
${responsiveStyles}
`;
}

/**
 * Generate responsive CSS based on component level
 */
function getResponsiveStyles(level, kebabName) {
  const baseResponsive = `/* Tablet (768px and below) */
@media (max-width: 768px) {
  .${kebabName} {
    /* Tablet adjustments */
  }
}

/* Mobile (480px and below) */
@media (max-width: 480px) {
  .${kebabName} {
    /* Mobile adjustments */
  }
}`;

  // Templates and organisms may need more complex responsive handling
  if (level === 'templates' || level === 'organisms') {
    return `/* Large screens (1200px and above) */
@media (min-width: 1200px) {
  .${kebabName} {
    /* Large screen adjustments */
  }
}

${baseResponsive}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  .${kebabName} {
    animation: none;
    transition: none;
  }
}`;
  }

  return baseResponsive;
}

/**
 * Generate the barrel export index file
 */
function generateIndexCode(componentName) {
  return `/**
 * ${componentName} barrel export
 * @generated Exported from Figma via AID Plugin
 */

export { ${componentName}, default } from './${componentName}';
export type { ${componentName}Props } from './${componentName}.types';
`;
}

/**
 * Generate the test file
 */
function generateTestCode(componentName) {
  const kebabName = toKebabCase(componentName);

  return `/**
 * ${componentName} Tests
 * @generated Exported from Figma via AID Plugin
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { ${componentName} } from './${componentName}';

describe('${componentName}', () => {
  it('renders without crashing', () => {
    render(<${componentName}>Test content</${componentName}>);
    expect(screen.getByTestId('${kebabName}')).toBeInTheDocument();
  });

  it('renders children correctly', () => {
    render(<${componentName}>Hello World</${componentName}>);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<${componentName} className="custom-class">Content</${componentName}>);
    expect(screen.getByTestId('${kebabName}')).toHaveClass('custom-class');
  });

  it('passes data-testid prop', () => {
    render(<${componentName} data-testid="custom-test-id">Content</${componentName}>);
    expect(screen.getByTestId('custom-test-id')).toBeInTheDocument();
  });
});
`;
}

/**
 * Generate Storybook story file
 */
function generateStoryCode(exportData, componentName) {
  const { metadata, variants = [] } = exportData;
  const level = metadata?.level || 'molecules';
  const description = metadata?.description || `${componentName} component`;
  const hasVariants = variants.length > 0;

  // Generate variant stories
  const variantStories = hasVariants
    ? variants.map(v => {
        const variantName = typeof v === 'string' ? v : v.name;
        const storyName = toPascalCase(variantName);
        return `
export const ${storyName}: Story = {
  args: {
    variant: '${variantName}',
    children: '${componentName} - ${variantName}',
  },
};`;
      }).join('\n')
    : '';

  // Determine argTypes based on variants
  const variantArgTypes = hasVariants
    ? `    variant: {
      control: 'select',
      options: [${variants.map(v => `'${typeof v === 'string' ? v : v.name}'`).join(', ')}],
      description: 'Visual variant of the component',
    },`
    : '';

  return `/**
 * ${componentName} Storybook Stories
 * @generated Exported from Figma via AID Plugin
 */

import type { Meta, StoryObj } from '@storybook/react';
import { ${componentName} } from './${componentName}';

/**
 * ${description}
 *
 * ## Usage
 * \`\`\`tsx
 * import { ${componentName} } from '@/components/${level}/${componentName}';
 *
 * <${componentName}>Content</${componentName}>
 * \`\`\`
 */
const meta: Meta<typeof ${componentName}> = {
  title: 'Components/${toPascalCase(level)}/${componentName}',
  component: ${componentName},
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: '${description.replace(/'/g, "\\'")}',
      },
    },
  },
  argTypes: {
    children: {
      control: 'text',
      description: 'Content to display inside the component',
    },
    className: {
      control: 'text',
      description: 'Additional CSS class names',
    },
${variantArgTypes}
  },
};

export default meta;
type Story = StoryObj<typeof ${componentName}>;

/**
 * Default ${componentName} appearance
 */
export const Default: Story = {
  args: {
    children: '${componentName}',
  },
};

/**
 * ${componentName} with custom class
 */
export const WithClassName: Story = {
  args: {
    children: '${componentName}',
    className: 'custom-class',
  },
};
${variantStories}
`;
}

/**
 * Generate the types file
 */
function generateTypesCode(exportData, componentName) {
  const { variants = [], metadata } = exportData;
  const hasVariants = variants.length > 0;

  const variantType = hasVariants
    ? `\n/**\n * Available variants for ${componentName}\n */\nexport type ${componentName}Variant = ${variants.map(v => `'${typeof v === 'string' ? v : v.name}'`).join(' | ')};\n`
    : '';

  const variantProp = hasVariants
    ? `  /**\n   * Visual variant of the component\n   * @default '${variants[0]?.name || 'default'}'\n   */\n  variant?: ${componentName}Variant;\n`
    : '';

  return `/**
 * ${componentName} Type Definitions
 * @generated Exported from Figma via AID Plugin
 */

import type { HTMLAttributes, ReactNode } from 'react';
${variantType}
/**
 * Props for the ${componentName} component
 */
export interface ${componentName}Props extends HTMLAttributes<HTMLElement> {
  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * Child elements
   */
  children?: ReactNode;
${variantProp}
  /**
   * Test ID for testing purposes
   */
  'data-testid'?: string;
}
`;
}

/**
 * Get appropriate HTML element type based on atomic level
 */
function getElementType(level, componentName) {
  const name = componentName.toLowerCase();

  // Button components
  if (name.includes('button') || name.includes('btn')) return 'button';

  // Link components
  if (name.includes('link')) return 'a';

  // Input components
  if (name.includes('input') || name.includes('textfield')) return 'input';

  // List components
  if (name.includes('list')) return 'ul';
  if (name.includes('listitem')) return 'li';

  // Navigation
  if (name.includes('nav')) return 'nav';

  // Header/Footer
  if (name.includes('header')) return 'header';
  if (name.includes('footer')) return 'footer';

  // Section/Article
  if (name.includes('section')) return 'section';
  if (name.includes('article')) return 'article';

  // Images
  if (name.includes('image') || name.includes('avatar') || name.includes('icon')) return 'span';

  // Default based on level
  switch (level) {
    case 'atoms':
      return 'span';
    case 'molecules':
      return 'div';
    case 'organisms':
      return 'section';
    case 'templates':
      return 'div';
    default:
      return 'div';
  }
}

/**
 * Get TypeScript ref type for HTML element
 */
function getRefType(elementType) {
  const refTypeMap = {
    'div': 'HTMLDivElement',
    'span': 'HTMLSpanElement',
    'button': 'HTMLButtonElement',
    'a': 'HTMLAnchorElement',
    'input': 'HTMLInputElement',
    'ul': 'HTMLUListElement',
    'li': 'HTMLLIElement',
    'nav': 'HTMLElement',
    'header': 'HTMLElement',
    'footer': 'HTMLElement',
    'section': 'HTMLElement',
    'article': 'HTMLElement',
    'form': 'HTMLFormElement',
    'img': 'HTMLImageElement',
    'label': 'HTMLLabelElement',
    'select': 'HTMLSelectElement',
    'textarea': 'HTMLTextAreaElement'
  };
  return refTypeMap[elementType] || 'HTMLElement';
}

/**
 * Map token type to CSS property
 */
function tokenTypeToCssProperty(tokenType) {
  const mapping = {
    'color': 'color',
    'backgroundColor': 'background-color',
    'background': 'background-color',
    'fontSize': 'font-size',
    'fontFamily': 'font-family',
    'fontWeight': 'font-weight',
    'lineHeight': 'line-height',
    'letterSpacing': 'letter-spacing',
    'borderRadius': 'border-radius',
    'borderWidth': 'border-width',
    'borderColor': 'border-color',
    'padding': 'padding',
    'margin': 'margin',
    'gap': 'gap',
    'boxShadow': 'box-shadow',
    'opacity': 'opacity'
  };
  return mapping[tokenType] || null;
}

/**
 * Convert token value to CSS value
 */
function tokenValueToCss(value, type) {
  if (value === null || value === undefined) return null;

  // Already a CSS value
  if (typeof value === 'string') return value;

  // Color objects
  if (type === 'color' || type === 'backgroundColor' || type === 'background') {
    if (typeof value === 'object' && value.r !== undefined) {
      const r = Math.round(value.r * 255);
      const g = Math.round(value.g * 255);
      const b = Math.round(value.b * 255);
      const a = value.a !== undefined ? value.a : 1;
      return a < 1
        ? `rgba(${r}, ${g}, ${b}, ${a.toFixed(2)})`
        : `rgb(${r}, ${g}, ${b})`;
    }
  }

  // Numeric values with units
  if (typeof value === 'number') {
    if (['fontSize', 'borderRadius', 'borderWidth', 'padding', 'margin', 'gap'].includes(type)) {
      return `${value}px`;
    }
    if (type === 'lineHeight') {
      return value > 3 ? `${value}px` : value.toFixed(2);
    }
    if (type === 'fontWeight') {
      return String(value);
    }
    if (type === 'opacity') {
      return value.toFixed(2);
    }
    return String(value);
  }

  return null;
}

/**
 * Generate React component files and return contents (no disk write)
 * Used for cloud deployments where we return file contents to client
 * @param {Object} exportData - The export data from aidExporter
 * @returns {Object} Result with file contents
 */
function generateReactComponentContents(exportData) {
  console.log('[ReactGenerator] 🚀 Generating React component contents (in-memory)...');
  console.log('[ReactGenerator] Input name:', exportData.name);

  const componentName = toPascalCase(exportData.name);
  const level = exportData.metadata?.level || 'molecule';

  console.log('[ReactGenerator] Component name (PascalCase):', componentName);

  // Generate all file contents
  const fileContents = {
    [`${componentName}.tsx`]: generateComponentCode(exportData, componentName),
    [`${componentName}.module.css`]: generateStylesCode(exportData, componentName),
    ['index.ts']: generateIndexCode(componentName),
    [`${componentName}.types.ts`]: generateTypesCode(exportData, componentName),
  };

  // Always include test and storybook files (mandatory)
  fileContents[`${componentName}.test.tsx`] = generateTestCode(componentName);
  fileContents[`${componentName}.stories.tsx`] = generateStoryCode(exportData, componentName);

  const files = Object.keys(fileContents);
  console.log('[ReactGenerator] 📋 Generated files:', files);

  return {
    success: true,
    componentName,
    level,
    relativePath: `components/${level}/${componentName}`,
    files,
    fileContents
  };
}

module.exports = {
  generateReactComponent,
  generateReactComponentContents,
  toPascalCase,
  toKebabCase
};
