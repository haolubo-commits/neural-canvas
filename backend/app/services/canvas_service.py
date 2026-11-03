"""
Canvas Graph & Topological Operations Service for NeuralCanvas.
Manages nodes, directed connections, topological ordering, and cycle checks.
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.canvas import CanvasNode, CanvasEdge, NodeExecutionStatus
from app.schemas.canvas import CanvasNodeCreate, CanvasNodeUpdate, CanvasEdgeCreate


class CanvasService:
    @staticmethod
    def create_node(db: Session, session_id: str, node_in: CanvasNodeCreate) -> CanvasNode:
        """Creates and stores a new canvas node."""
        node_id = node_in.node_id or f"node_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()

        db_node = CanvasNode(
            node_id=node_id,
            session_id=session_id,
            node_type=node_in.node_type.value,
            label=node_in.label,
            position_x=node_in.position_x,
            position_y=node_in.position_y,
            width=node_in.width,
            height=node_in.height,
            data=node_in.data or {},
            execution_status=node_in.execution_status.value,
            created_at=now,
            updated_at=now,
        )
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return db_node

    @staticmethod
    def get_node(db: Session, session_id: str, node_id: str) -> Optional[CanvasNode]:
        """Retrieves a single node by ID and session."""
        return db.query(CanvasNode).filter(
            CanvasNode.session_id == session_id,
            CanvasNode.node_id == node_id,
        ).first()

    @staticmethod
    def find_node_by_label_or_id(db: Session, session_id: str, identifier: str) -> Optional[CanvasNode]:
        """Finds a node by exact ID or case-insensitive label match."""
        node = db.query(CanvasNode).filter(
            CanvasNode.session_id == session_id,
            CanvasNode.node_id == identifier,
        ).first()
        if not node:
            node = db.query(CanvasNode).filter(
                CanvasNode.session_id == session_id,
                CanvasNode.label.ilike(f"%{identifier}%"),
            ).first()
        return node

    @staticmethod
    def list_nodes(db: Session, session_id: str) -> List[CanvasNode]:
        """Lists all nodes belonging to a session."""
        return db.query(CanvasNode).filter(CanvasNode.session_id == session_id).all()

    @staticmethod
    def update_node(
        db: Session, session_id: str, node_id: str, node_in: CanvasNodeUpdate
    ) -> Optional[CanvasNode]:
        """Updates spatial or data attributes of an existing node."""
        node = CanvasService.get_node(db, session_id, node_id)
        if not node:
            return None

        update_data = node_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "execution_status" and value:
                setattr(node, field, value.value if hasattr(value, "value") else value)
            elif value is not None:
                setattr(node, field, value)

        node.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(node)
        return node

    @staticmethod
    def delete_node(db: Session, session_id: str, node_id: str) -> bool:
        """Deletes a node and associated edges."""
        node = CanvasService.get_node(db, session_id, node_id)
        if not node:
            return False

        # Associated edges are deleted via CASCADE
        db.delete(node)
        db.commit()
        return True

    @staticmethod
    def create_edge(db: Session, session_id: str, edge_in: CanvasEdgeCreate) -> CanvasEdge:
        """Connects two nodes via a directed edge."""
        edge_id = edge_in.edge_id or f"edge_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()

        db_edge = CanvasEdge(
            edge_id=edge_id,
            session_id=session_id,
            source_node_id=edge_in.source_node_id,
            target_node_id=edge_in.target_node_id,
            source_handle=edge_in.source_handle,
            target_handle=edge_in.target_handle,
            edge_type=edge_in.edge_type,
            created_at=now,
        )
        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)
        return db_edge

    @staticmethod
    def list_edges(db: Session, session_id: str) -> List[CanvasEdge]:
        """Lists all directed connections in a session."""
        return db.query(CanvasEdge).filter(CanvasEdge.session_id == session_id).all()

    @staticmethod
    def delete_edge(db: Session, session_id: str, edge_id: str) -> bool:
        """Deletes a directed edge."""
        edge = db.query(CanvasEdge).filter(
            CanvasEdge.session_id == session_id,
            CanvasEdge.edge_id == edge_id,
        ).first()
        if not edge:
            return False

        db.delete(edge)
        db.commit()
        return True

    @staticmethod
    def analyze_graph_topology(db: Session, session_id: str) -> Dict[str, Any]:
        """
        Analyzes the directed graph topology: in/out degrees, root nodes, leaf nodes,
        and cycle detection.
        """
        nodes = CanvasService.list_nodes(db, session_id)
        edges = CanvasService.list_edges(db, session_id)

        in_degree: Dict[str, int] = {n.node_id: 0 for n in nodes}
        out_degree: Dict[str, int] = {n.node_id: 0 for n in nodes}
        adj_list: Dict[str, List[str]] = {n.node_id: [] for n in nodes}

        for e in edges:
            if e.source_node_id in out_degree:
                out_degree[e.source_node_id] += 1
            if e.target_node_id in in_degree:
                in_degree[e.target_node_id] += 1
            if e.source_node_id in adj_list:
                adj_list[e.source_node_id].append(e.target_node_id)

        root_nodes = [nid for nid, deg in in_degree.items() if deg == 0]
        leaf_nodes = [nid for nid, deg in out_degree.items() if deg == 0]

        # Cycle detection via Kahn's algorithm
        queue = [nid for nid in root_nodes]
        visited_count = 0
        in_deg_copy = in_degree.copy()

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for neighbor in adj_list.get(curr, []):
                in_deg_copy[neighbor] -= 1
                if in_deg_copy[neighbor] == 0:
                    queue.append(neighbor)

        has_cycle = visited_count < len(nodes)

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "root_nodes": root_nodes,
            "leaf_nodes": leaf_nodes,
            "has_cycles": has_cycle,
        }
