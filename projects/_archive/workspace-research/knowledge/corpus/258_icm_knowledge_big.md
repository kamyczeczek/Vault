---
type: Concept
id: 258_icm_knowledge_big
title: "ICM_knowledge.md (part 259/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

/warehouses/${warehouseId}/products

updateStock: (productId: string, quantity: number): Promise

/products/${productId}/stock

method: 'PATCH',

body: JSON.stringify({ quantity })

TypeScript Conventions

Strict mode always on

No any — use unknown with type narrowing instead

#### Discriminated unions with type guard functions:

type EditorTab =

| { type: 'file'; path: string; content: string }

| { type: 'terminal'; sessionId: string }

| { type: 'diff'; leftPath: string; rightPath: string };

function isFileTab(tab: EditorTab): tab is EditorTab & { type: 'file' } {

return tab.type === 'file';

Interfaces for object shapes, types for unions and aliases

PascalCase for types/interfaces, no I prefix (User not IUser)

CSS / Styling

#### Scoped styles in components:
