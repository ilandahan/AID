/** Skill-scoped Write/Edit guard. Matches the standalone shell/Python guard.
 * Runs without shell interpolation, external runtimes, or filesystem reads.
 * Malformed input remains fail-open, as in the original guard.
 */
let input = '';
for await (const chunk of process.stdin) input += chunk;
let path;
try {
  const value = JSON.parse(input)?.tool_input?.file_path;
  path = typeof value === 'string' ? value.replaceAll('\\', '/') : '';
} catch {
  process.exit(0);
}
const allowed = [
  /\.aid\/pipeline\/state\.json$/,
  /\.aid\/pipeline\/autoresearch\//,
  /\.aid\/pipeline\/outer-counters\.sidecar$/,
];
const protectedPaths = [
  /\/criteria\/[^/]+\.ya?ml$/,
  /\/AGENT-PROMPT\.md$/,
  /\.aid\/[^ ]*\.json$/,
  /\.mcp\.json$/,
  /\/\.claude\/skills\//,
];
if (!allowed.some(pattern => pattern.test(path)) &&
    protectedPaths.some(pattern => pattern.test(path))) {
  console.log(JSON.stringify({
    permissionDecision: 'deny',
    message: '[autoresearch] Blocked: ' + path + ' is part of the FROZEN eval harness ' +
      '(criteria/prompts/pipeline config/skills). Editing it mid-pass makes the score ' +
      'meaningless. Edit only the target artifact; harness changes happen outside AR runs.',
  }));
}
