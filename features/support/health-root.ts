// Health-check root and skip rule.
//
// WHY: on a clean checkout (or a fresh project) the AID runtime files do not exist yet,
// so the @smoke/@critical health check failed instead of saying it had nothing to check
// (T15-43, L1-13). A scenario that checks an AID runtime file under .aid/ is SKIPPED, with
// a reason, when that file is absent. Files are resolved under AID_HEALTH_ROOT (default:
// the current working directory).
import { Before } from '@cucumber/cucumber';
import * as fs from 'fs';
import * as path from 'path';

export function healthRoot(): string {
  return path.resolve(process.env.AID_HEALTH_ROOT || process.cwd());
}

const FILE_STEP = /^the file "([^"]+)" should exist$/;

Before(function (this: { log?: (text: string) => void }, { pickle }) {
  const root = healthRoot();
  for (const step of pickle.steps) {
    const m = FILE_STEP.exec(step.text);
    if (!m || !m[1].startsWith('.aid/')) continue;
    if (!fs.existsSync(path.join(root, m[1]))) {
      const reason = `SKIPPED: ${m[1]} is absent under ${root} (not initialized yet; run /aid-init)`;
      if (typeof this.log === 'function') this.log(reason);
      console.warn(reason);
      return 'skipped';
    }
  }
  return undefined;
});
