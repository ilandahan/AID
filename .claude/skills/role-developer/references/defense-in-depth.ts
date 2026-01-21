/**
 * Defense-in-Depth Validation Pattern
 * 
 * When fixing bugs caused by invalid data, validate at EVERY layer.
 * Single-point validation can be bypassed by different code paths.
 * 
 * @see role-developer.md - Defense-in-Depth Validation section
 */

import { existsSync, statSync } from 'fs';
import { normalize, resolve } from 'path';
import { tmpdir } from 'os';

// =============================================================================
// THE PROBLEM
// =============================================================================

/*
Bug: Empty `projectDir` caused `git init` to run in source code directory

Data flow:
1. Test setup → empty string
2. Project.create(name, '')
3. WorkspaceManager.createWorkspace('')
4. git init runs in process.cwd() ← BUG MANIFESTS HERE

Single-point fix (WRONG):
- Add check in gitInit() → but other code paths can still pass empty string

Defense-in-depth fix (RIGHT):
- Add validation at EVERY layer
- Make the bug structurally impossible
*/

// =============================================================================
// LAYER 1: ENTRY POINT VALIDATION
// =============================================================================

/**
 * Layer 1: Reject obviously invalid input at API boundary
 * 
 * This is the first line of defense. Catches most issues early.
 */
interface CreateProjectOptions {
  name: string;
  workingDirectory: string;
  description?: string;
}

export function createProject(options: CreateProjectOptions): Project {
  const { name, workingDirectory } = options;

  // Layer 1: Entry point validation
  if (!name?.trim()) {
    throw new Error('Project name cannot be empty');
  }

  if (!workingDirectory?.trim()) {
    throw new Error('Working directory cannot be empty');
  }

  if (!existsSync(workingDirectory)) {
    throw new Error(`Working directory does not exist: ${workingDirectory}`);
  }

  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`Working directory is not a directory: ${workingDirectory}`);
  }

  // Proceed with validated data
  return new Project(name.trim(), workingDirectory);
}

// =============================================================================
// LAYER 2: BUSINESS LOGIC VALIDATION
// =============================================================================

/**
 * Layer 2: Ensure data makes sense for this specific operation
 * 
 * Even if Layer 1 passes, this layer validates for the specific use case.
 * Different operations may have different requirements.
 */
class WorkspaceManager {
  async createWorkspace(projectDir: string, sessionId: string): Promise<Workspace> {
    // Layer 2: Business logic validation
    if (!projectDir) {
      throw new Error('projectDir is required for workspace initialization');
    }

    if (!sessionId) {
      throw new Error('sessionId is required for workspace tracking');
    }

    // Additional business rule: projectDir must be absolute
    if (!projectDir.startsWith('/')) {
      throw new Error(`projectDir must be absolute path, got: ${projectDir}`);
    }

    return this.initWorkspace(projectDir, sessionId);
  }

  private async initWorkspace(dir: string, session: string): Promise<Workspace> {
    // Implementation...
    return { dir, session } as Workspace;
  }
}

// =============================================================================
// LAYER 3: ENVIRONMENT GUARDS
// =============================================================================

/**
 * Layer 3: Prevent dangerous operations in specific contexts
 * 
 * Some operations are dangerous only in certain environments.
 * Add guards that are context-aware.
 */
class WorktreeManager {
  async gitInit(directory: string): Promise<void> {
    // Layer 3: Environment guard for tests
    if (process.env.NODE_ENV === 'test') {
      const normalized = normalize(resolve(directory));
      const tempDir = normalize(resolve(tmpdir()));

      if (!normalized.startsWith(tempDir)) {
        throw new Error(
          `SAFETY: Refusing git init outside temp directory during tests.\n` +
          `  Attempted: ${directory}\n` +
          `  Allowed: ${tempDir}/*\n` +
          `  This prevents tests from modifying source code.`
        );
      }
    }

    // Layer 3: Environment guard for CI
    if (process.env.CI === 'true') {
      const cwd = process.cwd();
      if (directory === cwd || directory === '.') {
        throw new Error(
          `SAFETY: Refusing git init in CI working directory.\n` +
          `  This is likely a bug - specify explicit directory.`
        );
      }
    }

    await this.executeGitInit(directory);
  }

  private async executeGitInit(dir: string): Promise<void> {
    // Implementation...
  }
}

// =============================================================================
// LAYER 4: DEBUG INSTRUMENTATION
// =============================================================================

/**
 * Layer 4: Capture context for forensics
 * 
 * When other layers fail, this helps diagnose the issue.
 * Log enough context to understand what happened.
 */
interface Logger {
  debug(message: string, context: Record<string, unknown>): void;
  warn(message: string, context: Record<string, unknown>): void;
}

class InstrumentedWorktreeManager {
  constructor(private logger: Logger) { }

  async gitInit(directory: string): Promise<void> {
    // Layer 4: Debug instrumentation
    const context = {
      directory,
      cwd: process.cwd(),
      nodeEnv: process.env.NODE_ENV,
      ci: process.env.CI,
      stack: new Error().stack?.split('\n').slice(1, 6).join('\n'),
      timestamp: new Date().toISOString(),
    };

    this.logger.debug('gitInit called', context);

    // Warn on suspicious patterns
    if (!directory || directory === '.' || directory === process.cwd()) {
      this.logger.warn('gitInit called with suspicious directory', {
        ...context,
        warning: 'Directory appears to be current working directory',
      });
    }

    // Proceed with operation (other layers will validate)
    await this.executeGitInit(directory);
  }

  private async executeGitInit(dir: string): Promise<void> {
    // Implementation...
  }
}

// =============================================================================
// COMPLETE EXAMPLE: ALL LAYERS TOGETHER
// =============================================================================

/**
 * Complete example showing all four layers working together
 */
class SecureProjectService {
  constructor(
    private logger: Logger,
    private workspaceManager: WorkspaceManager,
    private worktreeManager: WorktreeManager,
  ) { }

  async createProject(name: string, directory: string): Promise<Project> {
    // LAYER 1: Entry validation
    if (!name?.trim()) {
      throw new Error('Project name required');
    }
    if (!directory?.trim()) {
      throw new Error('Directory required');
    }
    if (!existsSync(directory)) {
      throw new Error(`Directory not found: ${directory}`);
    }

    // LAYER 4: Instrumentation (before risky operations)
    this.logger.debug('createProject starting', {
      name,
      directory,
      cwd: process.cwd(),
      stack: new Error().stack,
    });

    // LAYER 2: Business logic (in workspace manager)
    const workspace = await this.workspaceManager.createWorkspace(
      directory,
      `session-${Date.now()}`
    );

    // LAYER 3: Environment guards (in worktree manager)
    await this.worktreeManager.gitInit(workspace.dir);

    return new Project(name, directory);
  }
}

// =============================================================================
// WHY ALL FOUR LAYERS ARE NECESSARY
// =============================================================================

/*
During testing, each layer caught bugs the others missed:

Layer 1 catches:
- Empty/null inputs
- Non-existent paths
- Wrong types

Layer 2 catches:
- Valid input that doesn't make sense for operation
- Missing required context (sessionId, etc.)
- Business rule violations

Layer 3 catches:
- Operations safe in prod but dangerous in test
- CI-specific safety requirements
- Environment-specific constraints

Layer 4 catches:
- Helps diagnose when other layers fail
- Provides forensic data for debugging
- Identifies patterns of misuse

Real result from implementing all 4 layers:
- All 1847 tests passed
- Bug became impossible to reproduce
- Similar bugs prevented automatically
*/

// =============================================================================
// TYPES (for compilation)
// =============================================================================

interface Project {
  name: string;
  directory: string;
}

class Project implements Project {
  constructor(public name: string, public directory: string) { }
}

interface Workspace {
  dir: string;
  session: string;
}

export { WorkspaceManager, WorktreeManager, InstrumentedWorktreeManager, SecureProjectService };
