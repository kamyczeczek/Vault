---
description: Answer-layer pilot - fresh subagent, all tools denied by config
mode: subagent
model: opencode/glm-5.3-flash-free
steps: 4
permissions:
  - action: "*"
    resource: "*"
    effect: deny
  - action: read
    resource: "*"
    effect: allow
  - action: read
    resource: "**/the-pragmatic-programmer-retrieval/**"
    effect: deny
  - action: read
    resource: "**/data/**"
    effect: deny
  - action: read
    resource: "**/eval/**"
    effect: deny
  - action: read
    resource: "**/db/**"
    effect: deny
  - action: read
    resource: "**/scripts/**"
    effect: deny
  - action: read
    resource: "**/starter/**"
    effect: deny
---

Odpowiedz wyłącznie w oparciu o fragmenty podane w zadaniu użytkownika. Nie masz dostępu do narzędzi. Nie szukaj informacji nigdzie indziej.
