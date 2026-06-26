# ADR 0001: Platform Modular Monolith

## Decision

Game Game Go uses a modular monolith: one Python desktop app with a platform
shell and independent game modules.

## Consequences

- Games own their rules, state, runtime and presentation.
- Platform owns registry, services, shell scenes and composition.
- Architecture tests prevent legacy root imports and cross-game coupling.
