import { Given, Then } from '@cucumber/cucumber';
import * as fs from 'fs';
import * as path from 'path';
import assert from 'assert';

let fileContent: string;
let parsedJson: Record<string, unknown>;

Given('the AID system is initialized', function () {
  const aidDir = path.resolve(process.cwd(), '.aid');
  assert.ok(fs.existsSync(aidDir), '.aid directory does not exist');
});

Then('the file {string} should exist', function (filePath: string) {
  const fullPath = path.resolve(process.cwd(), filePath);
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
