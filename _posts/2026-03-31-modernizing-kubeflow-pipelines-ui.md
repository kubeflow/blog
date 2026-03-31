---
toc: true
layout: post
comments: true
title: "Modernizing Kubeflow Pipelines UI"
hide: false
categories: [pipelines]
permalink: /modernizing-kubeflow-pipelines-ui/
author: Manaswini Das
---

The Kubeflow Pipelines web interface has been upgraded from React 16 to React 19 — a modernization effort that touches every layer of the frontend stack. Whether you use the UI to manage pipelines day-to-day or contribute to the codebase, here's what this means for you.

## What's changing for users

You don't need to do anything differently. Your bookmarks, workflows, and browser all work exactly as before. But under the hood, the UI is now built on a modern foundation that delivers tangible improvements:

### A faster, more responsive interface

React 18 introduced automatic batching, which reduces unnecessary re-renders across the UI. In practice, this means pages like Run Details, Experiment Details, and the pipeline creation flow respond faster to your interactions. Forms validate without flicker, and multi-step workflows feel snappier. The production bundle size stayed exactly the same — 0% increase — so page load times are unchanged.

### Smoother pipeline graph navigation

The pipeline DAG visualization (the graph you see when inspecting a pipeline's structure) has been migrated from the deprecated react-flow-renderer to @xyflow/react. This brings improved pan, zoom, and drag performance, especially on larger or more complex pipeline graphs. If you've ever experienced sluggishness when navigating a deeply nested pipeline, this upgrade directly addresses that.

### Improved charts and metrics display

Run metrics and comparison charts now use Recharts instead of the deprecated react-vis library. The new charting library renders more efficiently, handles edge cases better, and provides cleaner visual output when comparing run results side by side.

### Better accessibility

The component library migration from Material-UI v3 to MUI v5 brings improved keyboard navigation, better ARIA attribute coverage, and more consistent focus management across dialogs, tables, and form elements. These improvements make the UI more usable with screen readers and keyboard-only workflows.

### No breaking changes

Every user-facing feature works the same way it did before. The API contracts are unchanged. If you use the KFP Python SDK or REST API to interact with the platform, nothing changes on your end. This upgrade was purely a frontend modernization — zero impact on backend behavior, pipeline execution, or artifact storage.

## Why we made this change

The KFP frontend had been running on React 16 (released in 2017) with Material-UI v3, Create React App, and Jest/Enzyme for testing. This created compounding issues:

- **Security exposure.** React 16 and 17 no longer receive security patches, and dozens of transitive dependencies were locked to outdated versions because of React peer constraints.
- **Stalled ecosystem.** Modern libraries — including improved data-fetching, visualization, and accessibility tools — dropped support for React 16/17. Staying behind meant the UI couldn't benefit from upstream improvements.
- **Contributor friction.** The legacy CRA + Jest + Enzyme toolchain was slow to build, brittle to test, and increasingly difficult for new contributors to set up. Modernizing the stack lowers the barrier to contribution.

## How we got here

Rather than attempting a single risky version jump, we followed a deps-first, bump-last strategy: upgrade every dependency to be forward-compatible before touching React itself. A custom React peer compatibility gate in CI prevented regressions at every step. The work was executed across **20+** pull requests in strict dependency order.

### React 16 → 17: Rebuilding the foundation

Before React could move forward, the entire build and test toolchain had to be replaced. Create React App was swapped for Vite, Jest + Enzyme gave way to Vitest + Testing Library, and Material-UI was upgraded from v3 to v4 to unblock the React 17 peer range. The deprecated react-vis charting library was replaced with Recharts. With those blockers cleared, the React 17 bump itself was a small, low-risk change.

### React 17 → 18: The biggest leap

This phase required the most dependency work. Storybook jumped from v6 straight to v10 on the Vite builder. Material-UI v4 was migrated to MUI v5 with Emotion. react-query moved to @tanstack/react-query v4. react-flow-renderer was replaced with @xyflow/react. After all ecosystem deps cleared the peer gate, the React 18 core bump landed — followed by careful stabilization of automatic batching behavior in class components that were reading stale state.

### React 18 → 19: The final stretch

A deprecation audit at React 18.3 found zero React-specific warnings. A final dependency sweep cleared the last peer blockers (react-ace, transitive react-redux). The React 19 bump resolved the final allowlist entry and handled a small set of API changes like the removal of forwardRef in test mocks.

## The full stack transformation

Over the course of this effort, virtually every layer of the frontend stack was modernized:

| Layer                | Before                   | After                    |
| -------------------- | ------------------------ | ------------------------ |
| React                | 16                       | 19                       |
| Build system         | Create React App + Craco | Vite                     |
| Test framework       | Jest + Enzyme            | Vitest + Testing Library |
| UI component library | Material-UI v3           | MUI v5 + Emotion         |
| Data fetching        | react-query v3           | @tanstack/react-query v4 |
| Pipeline graph       | react-flow-renderer v9   | @xyflow/react            |
| Charts               | react-vis                | Recharts                 |
| Storybook            | 6 (Webpack)              | 10 (Vite)                |

## By the numbers

- 20+ PRs merged across the entire React 16-to-19 effort
- **15 tracked milestones** executed in strict dependency order
- **0% bundle size increase** — page load times unchanged
- **0 React deprecation warnings** at the 18.3 checkpoint audit
- **0 breaking changes** to user-facing features or APIs

## Want to contribute?

The full execution plan with every PR, issue, and dependency graph is tracked in the [react-18-19-upgrade-checklist.md](https://github.com/kubeflow/pipelines/blob/master/frontend/docs/react-18-19-upgrade-checklist.md). Look for miscellaneous bugs, report bugs, help with reviews and help improve our documentation.

Huge thanks to [@jeffspahr](https://github.com/jeffspahr), [@kanishka-commits](https://github.com/kanishka-commits), [@PR3MM](https://github.com/PR3MM), [@jsonmp-k8](https://github.com/jsonmp-k8), [@dpanshug](https://github.com/dpanshug), and [@rishi-jat](https://github.com/rishi-jat) for contributing to this effort and reviewing all the contributions leading up to this milestone!
