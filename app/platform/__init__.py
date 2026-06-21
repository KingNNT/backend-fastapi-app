"""Platform — cross-cutting infrastructure shared across all Bounded Contexts.

Contains: configs, web middleware/handlers, DB connection managers, event bus
implementation, CLI tools. This package MUST NOT import from any BC (iam, audit).
"""
