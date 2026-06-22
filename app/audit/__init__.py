"""Audit Bounded Context - immutable audit trail.

Subscribes to domain events from other BCs (currently iam/) and persists
audit log records in MongoDB.
"""
