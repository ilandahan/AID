import { Given, Then } from '@cucumber/cucumber';
import * as fs from 'fs';
import * as path from 'path';
import assert from 'assert';
import { healthRoot } from '../support/health-root';

let fileContent: string;
let parsedJson: Record<string, unknown>;

// Files are resolved under AID_HEALTH_ROOT (default: the current working directory).
// A scenario whose .aid/ file is absent is skipped by the Before hook in support/health-root.ts.

Given('the AID system is initialized', function () {
  const aidDir = path.join(healthRoot(), '.aid');
  assert.ok(fs.existsSync(aidDir), '.aid directory does not exist');
});

Then('the file {string} should exist', function (filePath: string) {
  const fullPath = path.join(healthRoot(), filePath);
  assert.ok(fs.existsSync(fullPath), `File ${filePath} does not exist`);
  fileContent = fs.readFileSync(fullPath, 'utf-8');
});

Then('the file should contain valid JSON', function () {
  try {
    parsedJson = JSON.parse(fileContent);
  } catch (e) {
    assert.fail(`File does not contain valid JSON: ${(e as Error).message}`);
  }
});

Then('the JSON should have a {string} field', function (fieldName: string) {
  assert.ok(
    fieldName in parsedJson,
    `JSON is missing required field: ${fieldName}`
  );
});
