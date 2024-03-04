import { create } from "zustand";
import { Node, Edge, OnSelectionChangeParams } from "reactflow";
import {
  WorkflowNode as WorkflowNodeData,
  Edge as WorkflowEdgeData,
} from "./data/api/workflowAPI";

export interface WorkflowNode extends Node {
  data: WorkflowNodeData;
}

type WorkflowEdge = Edge & { data?: WorkflowEdgeData };

export interface SelectionParams extends OnSelectionChangeParams {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface StoreState {
  selected: SelectionParams;
  setSelected: (selected: StoreState["selected"]) => void;
  removeNodeFromSelection: (node: WorkflowNode) => void;
  addNodeToSelection: (node: WorkflowNode) => void;
}

export const useStore = create<StoreState>((set) => ({
  selected: { edges: [], nodes: [] },
  setSelected: (selected) => set({ selected }),

  removeNodeFromSelection: (node) => {
    set((state) => {
      return {
        selected: {
          ...state.selected,
          nodes: state.selected.nodes.filter((n) => n.id !== node.id),
        },
      };
    });
  },

  addNodeToSelection: (node) => {
    set((state) => {
      if (!state.selected.nodes.find((n) => n.id === node.id)) {
        return {
          selected: {
            ...state.selected,
            nodes: [...state.selected.nodes, node],
          },
        };
      } else {
        return state;
      }
    });
  },
}));
