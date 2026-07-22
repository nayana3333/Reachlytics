"use client";

import { KeyboardEvent, MouseEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Background, Controls, Edge, Handle, Node, NodeProps, Position, ReactFlow } from "@xyflow/react";
import { AgentDetailPanel } from "@/components/simulation/AgentDetailPanel";
import { Button } from "@/components/ui/Button";
import { GraphEdge, GraphNode, PersonaDetail } from "@/lib/types";

function nodeColor(node: GraphNode) {
  if (node.action === "never_shown" || node.action === "skipped") return "#C9C5BC";
  return node.in_target ? "#2563EB" : "#F97316";
}

function nodeShadow(node: GraphNode) {
  if (node.action === "never_shown" || node.action === "skipped") return "0 1px 2px rgba(0,0,0,0.08)";
  return node.in_target ? "0 1px 3px rgba(0,0,0,0.14)" : "0 1px 3px rgba(0,0,0,0.14)";
}

function separatePositions(nodes: GraphNode[]) {
  const placed: Array<{ id: string; x: number; y: number }> = [];
  const minDistance = 24;

  return nodes.map((node, index) => {
    let x = node.x ?? 80 + ((index * 137) % 780);
    let y = node.y ?? 40 + ((index * 83) % 380);
    let attempts = 0;

    while (
      attempts < 24 &&
      placed.some((placedNode) => Math.hypot(placedNode.x - x, placedNode.y - y) < minDistance)
    ) {
      x += 18 + (attempts % 4) * 6;
      y += attempts % 2 === 0 ? 14 : -14;
      attempts += 1;
    }

    placed.push({ id: node.id, x, y });
    return { ...node, x, y };
  });
}

type AgentNodeData = {
  graphNode: GraphNode;
  isSelected: boolean;
  onSelect: (nodeId: string) => void;
};

function AgentNode({ data }: NodeProps<Node<AgentNodeData>>) {
  const node = data.graphNode;

  return (
    <div className="relative h-5 w-5">
      <Handle
        type="target"
        position={Position.Left}
        className="!h-0 !w-0 !border-0 !bg-transparent"
        isConnectable={false}
      />
      <div
        title={`${node.label}: ${node.action}`}
        data-tooltip={node.label}
        aria-label={`Inspect ${node.label}`}
        className={`graph-node-dot h-5 w-5 cursor-pointer rounded-full border-2 ${data.isSelected ? "border-ink ring-4 ring-accent/20" : "border-white"}`}
        onClick={(event: MouseEvent<HTMLDivElement>) => {
          event.stopPropagation();
          data.onSelect(node.id);
        }}
        onKeyDown={(event: KeyboardEvent<HTMLDivElement>) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            data.onSelect(node.id);
          }
        }}
        role="button"
        tabIndex={0}
        style={{ background: nodeColor(node), boxShadow: nodeShadow(node) }}
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!h-0 !w-0 !border-0 !bg-transparent"
        isConnectable={false}
      />
    </div>
  );
}

const nodeTypes = { agentNode: AgentNode };

export function GraphView({
  nodes,
  edges,
  personas
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  personas: PersonaDetail[];
}) {
  const [currentRound, setCurrentRound] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const nodeKey = useMemo(() => nodes.map((node) => node.id).join("|"), [nodes]);
  const maxRound = useMemo(
    () => Math.max(0, ...nodes.map((node) => node.round ?? 0)),
    [nodes]
  );
  const personaById = useMemo(
    () => new Map(personas.map((persona) => [persona.id, persona])),
    [personas]
  );
  const visibleNodeIds = useMemo(
    () =>
      new Set(
        nodes
          .filter((node) => node.round !== null ? node.round <= currentRound : currentRound >= maxRound)
          .map((node) => node.id)
      ),
    [currentRound, maxRound, nodes]
  );
  const positionedNodes = useMemo(() => separatePositions(nodes), [nodes]);

  const selectNode = useCallback((nodeId: string) => {
    setSelectedId(nodeId);
  }, []);

  const [prevNodeKey, setPrevNodeKey] = useState(nodeKey);
  if (nodeKey !== prevNodeKey) {
    setPrevNodeKey(nodeKey);
    setCurrentRound(0);
    setSelectedId(null);
  }

  useEffect(() => {
    if (!maxRound || currentRound >= maxRound) return;
    const timer = window.setInterval(() => {
      setCurrentRound((round) => Math.min(round + 1, maxRound));
    }, 800);
    return () => window.clearInterval(timer);
  }, [currentRound, maxRound]);

  const flowNodes = useMemo<Node[]>(
    () =>
      positionedNodes.filter((node) => visibleNodeIds.has(node.id)).map((node, index) => ({
        id: node.id,
        position: {
          x: node.x ?? 80 + ((index * 137) % 780),
          y: node.y ?? 40 + ((index * 83) % 380)
        },
        data: {
          graphNode: node,
          isSelected: selectedId === node.id,
          onSelect: selectNode
        },
        type: "agentNode"
      })),
    [positionedNodes, selectNode, selectedId, visibleNodeIds]
  );

  const flowEdges = useMemo<Edge[]>(
    () =>
      edges
        .filter((edge) => edge.source && visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target))
        .map((edge) => ({
          id: edge.id,
          source: edge.source as string,
          target: edge.target,
          animated: edge.type === "direct_share",
          style: {
            stroke: edge.type === "direct_share" ? "#9F3F2F" : "#A9A49A",
            strokeDasharray: edge.type === "algorithmic_push" ? "4 4" : undefined,
            strokeWidth: selectedId && (edge.source === selectedId || edge.target === selectedId) ? 3 : 1.5
          }
        })),
    [edges, selectedId, visibleNodeIds]
  );

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_340px]">
      <div className="h-[560px] border border-line bg-white shadow-instrument">
        <div className="flex items-center justify-between gap-4 border-b border-line px-5 py-4">
          <div>
            <p className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-muted">02 Spread</p>
            <p className="mt-1 text-xs text-muted">Round {Math.min(currentRound, maxRound)} of {maxRound || 0}. Teal=in-target, amber=outside-target, grey=skipped or not shown.</p>
          </div>
          <Button
            variant="secondary"
            onClick={() => {
              setCurrentRound(0);
              setSelectedId(null);
            }}
            type="button"
          >
            Replay
          </Button>
        </div>
        <div className="graph-stage h-[496px]">
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            fitView
            nodeTypes={nodeTypes}
            nodesDraggable={false}
            onNodeClick={(_, node) => selectNode(node.id)}
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      </div>
      <AgentDetailPanel persona={selectedId ? personaById.get(selectedId) ?? null : null} onClose={() => setSelectedId(null)} />
    </div>
  );
}
