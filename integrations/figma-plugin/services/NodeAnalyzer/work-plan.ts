/**
 * @file services/NodeAnalyzer/work-plan.ts
 * @description Work plan creation for component conversion
 */

import type {
  FigmaNodeInfo,
  ComponentWorkPlan,
  WorkPlanStep,
  DependencyInfo,
} from '../../types';

import { classifyComponent } from './classification';

/**
 * Traverse tree looking for instances
 */
function traverseForInstances(
  nodeInfo: FigmaNodeInfo,
  callback: (node: FigmaNodeInfo) => void
): void {
  if (nodeInfo.isInstance) {
    callback(nodeInfo);
  }

  if (nodeInfo.children) {
    for (const child of nodeInfo.children) {
      traverseForInstances(child, callback);
    }
  }
}

/**
 * Find dependencies of a component
 */
export function findDependencies(
  nodeInfo: FigmaNodeInfo,
  nodeCache: Map<string, FigmaNodeInfo>
): DependencyInfo[] {
  const dependencies: DependencyInfo[] = [];

  traverseForInstances(nodeInfo, (instanceInfo) => {
    if (instanceInfo.mainComponentId) {
      dependencies.push({
        nodeId: instanceInfo.mainComponentId,
        nodeName: instanceInfo.name,
        level: 'atom', // Will be resolved later
        isExternal: !nodeCache.has(instanceInfo.mainComponentId),
      });
    }
  });

  return dependencies;
}

/**
 * Create a work plan for converting a component
 */
export function createWorkPlan(
  nodeInfo: FigmaNodeInfo,
  nodeCache: Map<string, FigmaNodeInfo>
): ComponentWorkPlan {
  const classification = classifyComponent(nodeInfo);
  const dependencies = findDependencies(nodeInfo, nodeCache);

  const steps: WorkPlanStep[] = [
    {
      id: `${nodeInfo.id}-step-1`,
      order: 1,
      action: 'extract_tokens',
      description: 'Extract design tokens (colors, spacing, typography, effects)',
      estimatedTokens: 500,
      status: 'pending',
    },
    {
      id: `${nodeInfo.id}-step-2`,
      order: 2,
      action: 'analyze_variants',
      description: `Analyze ${Object.keys(nodeInfo.variantProperties || {}).length} variant dimensions`,
      estimatedTokens: 300,
      status: 'pending',
    },
    {
      id: `${nodeInfo.id}-step-3`,
      order: 3,
      action: 'map_props',
      description: 'Map Figma properties to component props',
      estimatedTokens: 400,
      status: 'pending',
    },
    {
      id: `${nodeInfo.id}-step-4`,
      order: 4,
      action: 'generate_code',
      description: `Generate ${classification.level} component code`,
      estimatedTokens: 800,
      status: 'pending',
    },
  ];

  // Add storybook step if applicable
  if (classification.level === 'atom' || classification.level === 'molecule') {
    steps.push({
      id: `${nodeInfo.id}-step-5`,
      order: 5,
      action: 'create_stories',
      description: 'Create Storybook stories',
      estimatedTokens: 300,
      status: 'pending',
    });
  }

  return {
    componentId: nodeInfo.id,
    componentName: nodeInfo.name,
    classification,
    dependencies,
    steps,
    totalEstimatedTokens: steps.reduce((sum, step) => sum + step.estimatedTokens, 0),
    createdAt: new Date(),
  };
}
