# Introduction to AID

**AID (AI Development Methodology)** is a comprehensive framework designed to transform raw requirements into production-ready software using **Claude Code**. It bridges the gap between AI code generation and professional software engineering practices.

## What is AID?

AID is not just a tool; it's a **structured methodology** that guides you and your AI assistant through the entire software development life cycle (SDLC). It enforces discipline, maintains context, and ensures quality through a rigorous phase-gate system.

The core insight behind AID is that AI coding assistants often lack context and structure. Without guidance, they generate code that may be syntactically correct but architecturally flawed or inconsistent with project requirements. AID solves this by treating the AI as a junior developer who needs clear specs, defined tasks, and review processes.

## The Problem AID Solves

| Problem | AID Solution |
|---------|--------------|
| **AI generates code without context** | Phase gates enforce requirements verification before any code is written. |
| **Losing track across sessions** | A persistent Context Tracking system remembers every task and step. |
| **Inconsistent code quality** | Enforced TDD (Test Driven Development) and mandatory code reviews. |
| **Design-dev mismatch** | Direct integration with Figma to enforce design tokens as the source of truth. |
| **No learning from mistakes** | A built-in feedback loop and memory system that improves performance over time. |

## Key Features

### 1. Phase Gate System
The heart of AID is its 6-phase lifecycle. No phase can be skipped, and every transition requires passing a quality gate.
- **Phase 0: Discovery** - Research and feasibility.
- **Phase 1: PRD** - Product Requirements Document.
- **Phase 2: Tech Spec** - Architecture and technical detailed design.
- **Phase 3: Implementation Plan** - Task breakdown and JIRA integration.
- **Phase 4: Development** - TDD and code implementation.
- **Phase 5: QA & Ship** - Verification and deployment.

### 2. Context Tracking
AID maintains a JSON-based state file (`.aid/context.json`) that tracks exactly where you are in the project. You can close your terminal, come back a week later, and type `/good-morning` to resume exactly where you left off.

### 3. Role-Based Personas
AID switches "hats" depending on the task. It loads specific instructions (skills) for different roles:
- **Product Manager**: Focuses on user value, scope, and clarity.
- **Tech Lead**: Focuses on architecture, security, and patterns.
- **Developer**: Focuses on implementation, testing, and clean code.
- **QA Engineer**: Focuses on edge cases and validation.

### 4. Continuous Learning
AID includes a memory system that records feedback after every session. It analyzes this feedback to "learn" your preferences and improve its future responses.

## High-Level Architecture

AID operates as a layer on top of your project. It consists of:
- **Skills Library**: A collection of prompts and instructions for different phases and roles.
- **MCP Servers**: Integrations with external tools like Jira, GitHub, and Chrome.
- **State Management**: Local files that track project progress.
- **Slash Commands**: Shortcuts to trigger complex workflows (e.g., `/prd`, `/code-review`).

## Next Steps

Now that you understand the philosophy, learn how to set up AID in your environment in the [Getting Started](./02-getting-started.md) guide.
