/**
 * @file services/NodeAnalyzer/config.ts
 * @description Classification patterns for Atomic Design hierarchy
 */

export const ATOM_PATTERNS = {
  names: ['button', 'icon', 'input', 'label', 'text', 'link', 'badge', 'tag', 'avatar', 'checkbox', 'radio', 'switch', 'divider', 'spinner', 'skeleton'],
  maxChildren: 3,
  maxDepth: 2,
};

export const MOLECULE_PATTERNS = {
  names: ['form-field', 'search', 'menu-item', 'list-item', 'card-header', 'breadcrumb', 'pagination', 'tooltip', 'dropdown', 'select', 'date-picker'],
  minChildren: 2,
  maxChildren: 6,
  maxDepth: 3,
};

export const ORGANISM_PATTERNS = {
  names: ['card', 'header', 'footer', 'sidebar', 'modal', 'dialog', 'form', 'table', 'list', 'navbar', 'accordion', 'tabs', 'carousel'],
  minChildren: 3,
  minDepth: 2,
};

export const TEMPLATE_PATTERNS = {
  names: ['layout', 'template', 'page-layout', 'dashboard', 'auth-layout', 'grid'],
  isContainer: true,
};

export const CATEGORY_PATTERNS: Record<string, string[]> = {
  button: ['button', 'btn', 'cta'],
  input: ['input', 'text-field', 'textarea', 'field'],
  select: ['select', 'dropdown', 'picker', 'combobox'],
  checkbox: ['checkbox', 'check', 'toggle', 'switch'],
  radio: ['radio', 'option'],
  icon: ['icon', 'ico', 'svg'],
  text: ['text', 'label', 'heading', 'title', 'paragraph'],
  link: ['link', 'anchor'],
  card: ['card', 'tile', 'panel'],
  modal: ['modal', 'dialog', 'popup', 'overlay'],
  navigation: ['nav', 'menu', 'header', 'footer', 'sidebar', 'breadcrumb'],
  form: ['form', 'login', 'signup', 'register'],
  table: ['table', 'grid', 'list', 'data'],
  media: ['image', 'avatar', 'video', 'audio', 'media'],
};
