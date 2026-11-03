"""
Main API v1 router consolidating sessions, nodes, edges, and action endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import sessions, nodes, edges, actions

api_router = APIRouter()

api_router.include_router(sessions.router)
api_router.include_router(nodes.router)
api_router.include_router(edges.router)
api_router.include_router(actions.router)
