// Cucumber World - Shared State Between Steps
// Run install.sh on Mac/Linux for the full template
import { setWorldConstructor, World, IWorldOptions } from '@cucumber/cucumber';

export interface ICustomWorld {
  // Add your shared properties here
}

export class CustomWorld extends World implements ICustomWorld {
  constructor(options: IWorldOptions) {
    super(options);
  }
}

setWorldConstructor(CustomWorld);
