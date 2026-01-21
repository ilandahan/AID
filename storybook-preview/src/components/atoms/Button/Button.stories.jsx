import { Button } from './Button';

export default {
  title: 'Atoms/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline'],
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
    },
  },
};

export const Primary = {
  args: {
    label: 'Primary Button',
    variant: 'primary',
  },
};

export const Secondary = {
  args: {
    label: 'Secondary Button',
    variant: 'secondary',
  },
};

export const Outline = {
  args: {
    label: 'Outline Button',
    variant: 'outline',
  },
};

export const Small = {
  args: {
    label: 'Small Button',
    size: 'small',
  },
};

export const Large = {
  args: {
    label: 'Large Button',
    size: 'large',
  },
};

export const Disabled = {
  args: {
    label: 'Disabled Button',
    disabled: true,
  },
};
