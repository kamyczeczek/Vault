---
type: Concept
id: 257_icm_knowledge_big
title: "ICM_knowledge.md (part 258/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

│  └── DateFormattingExtensions.swift

└── Utilities/           # Small helpers

└── DeviceCapabilities.swift

#### Key conventions:

PascalCase for files (Swift convention), but still descriptive

Feature-based grouping under Features/

CameraPermissions.swift not Permissions.swift — qualify the name

General Pattern (Any Language)

#### When you encounter a new language, apply this structure:

src/ (or equivalent)

├── [entry point]        # Minimal — just init and delegate

├── features/ or modules/    # Self-contained feature units

│  └── [feature_name]/

│    ├── [entry/index]    # Re-exports or module definition

│    ├── [types/models]   # Data structures for this feature

│    ├── [api/handlers]   # External interface (API calls, commands)

│    └── [service/logic]   # Business logic

├── services/          # Shared, cross-cutting services

├── models/ or types/      # Global data structures

├── platform/          # OS/environment-specific code

└── utils/           # Small, focused helpers

Code Style Conventions

Import Organization (JS/TS)

#### Organize imports in 3 groups, separated by blank lines:

// 1. Framework & language imports

import { ref, computed, watch, onMounted } from 'vue';

import { defineStore } from 'pinia';

// 2. Third-party libraries

import { format } from 'date-fns';

// 3. Local imports (project code)

import { useGlobalStore } from '@/stores/globalAppState';

import { request } from '@/services/apiClient';

import type { UserProfile } from './types';

Vue Component Structure

#### Always this order in single-file components:

Store references

Props & emits

Reactive state (ref, reactive)

Computed properties

Methods / handlers

Lifecycle hooks (onMounted, etc.)

Pinia Store Pattern

#### Always use composition API style:

export const useFeatureStore = defineStore('feature-name', () => {

const items = ref<Item[]>([]);

const selectedItem = ref<Item | null>(null);

const isInitialized = ref(false);

// Init guard — prevent double initialization

async function initialize() {

if (isInitialized.value) return;

items.value = await featureApi.loadItems();

isInitialized.value = true;

function selectItem(item: Item) {

selectedItem.value = item;

// Return everything that should be accessible

return { items, selectedItem, isInitialized, initialize, selectItem };

API Layer Pattern

#### Centralized request function + module-level API objects:

// services/apiClient.ts — single fetch wrapper, typed

export async function request

(path: string, options?: RequestInit): Promise

const response = await fetch(

${API_BASE}${path}

headers: { 'Content-Type': 'application/json' },

if (!response.ok) {

const error = await response.json().catch(() => ({ error: 'Request failed' }));

throw new Error(error.error || 'Request failed');

return response.json();

// modules/inventory/api.ts — module-specific API

export const inventoryApi = {

listProducts: (warehouseId: string): Promise<Product[]> =>
