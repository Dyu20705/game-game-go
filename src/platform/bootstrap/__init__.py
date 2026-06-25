"""Composition root for wiring platform services and public game adapters."""

from .composition import build_default_registry, build_platform_context

__all__ = ["build_default_registry", "build_platform_context"]
