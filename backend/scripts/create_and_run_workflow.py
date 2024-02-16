from shortuuid import uuid
import requests
from pprint import pprint
from server.database.tables import WorkflowTable, NodeDataTypes
from typing import Any

from server.routers.workflows import NodeDataHandle


URL = "http://localhost:8081"
VERBOSE = False


def verbose(*args):
    if VERBOSE:
        print(*args)


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.HTTPError as e:
            if e.response is not None:
                print("--------------------------------------------------\n\n")
                print(f"Error for request: {func.__name__}  :  {args},  {kwargs}")
                print(f"HTTPError: {e.response.status_code} {e.response.reason}\n")
                print("--------------------------------------------------\n")
                if e.response.json():
                    pprint(e.response.json())
                else:
                    print(e.response.text)
                exit(1)
            else:
                raise

    return wrapper


@exception_handler
def get(path, query: dict | None = None, headers: dict | None = None) -> dict:
    url = f'{URL}/{path.lstrip("/")}'.rstrip("/") + "/"
    verbose("GET", url, query, headers)
    response = requests.get(url, params=query, headers=headers)
    response.raise_for_status()
    return response.json()


@exception_handler
def post(path, data: dict |None = None, headers: dict | None = None) -> dict:
    url = f'{URL}/{path.lstrip("/")}'.rstrip("/") 
    verbose("POST", url, data, headers)
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

def get_all_workflows() -> list[WorkflowTable.Workflow]:
    data = get(f"/workflows")
    return [WorkflowTable.Workflow(**x) for x in data]


def get_workflow(workflow_id: str) -> WorkflowTable.Workflow:
    data = get(f"/workflows/{workflow_id}/")
    return WorkflowTable.Workflow(**data)


def create_workflow(name: str, owner: str) -> WorkflowTable.Workflow:
    data = post("/workflows/", {"Name": name, "Owner": owner})
    return WorkflowTable.Workflow(**data)


def create_node(workflow_id: str, address: str, version: int) -> WorkflowTable.Node:
    node = post(
        f"/workflows/{workflow_id}/nodes/", {"Address": address, "Version": version}
    )
    return WorkflowTable.Node(**node)


def get_nodes(workflow_id: str) -> list[WorkflowTable.Node]:
    data = get(f"/workflows/{workflow_id}/nodes/")
    return [WorkflowTable.Node(**x) for x in data]


def get_node(workflow_id: str, node_id: str) -> WorkflowTable.Node:
    data = get(f"/workflows/{workflow_id}/nodes/{node_id}")
    return WorkflowTable.Node(**data)


def add_data_to_node(
    workflow_id: str, node_id: str, node_data_type: NodeDataTypes, key: str, data: Any
) -> WorkflowTable.Node:
    data = post(
        f"/workflows/{workflow_id}/nodes/{node_id}/data/",
        {"Key": key, "Type": node_data_type, "Data": data},
    )
    return WorkflowTable.Node(**data)


def get_node_data(workflow_id: str, node_id: str) -> list[WorkflowTable.Node]:
    data = get(
        f"/workflows/{workflow_id}/nodes/{node_id}/data/",
    )
    return [WorkflowTable.Node(**x) for x in data]


def add_edge_to_workflow(
    workflow_id: str, from_data: NodeDataHandle, to_data: NodeDataHandle
) -> WorkflowTable.Edge:
    edge = post(
        f"/workflows/{workflow_id}/edges", data={"From": from_data.model_dump(), "To": to_data.model_dump()}
    )
    return WorkflowTable.Edge(**edge)


def get_edge_from_workflow(workflow_id: str, edge_id: str) -> WorkflowTable.Edge:
    edge = get(f"/workflows/{workflow_id}/edges/{edge_id}")
    return WorkflowTable.Edge(**edge)

def run_workflow(workflow_id):
    run = post(f'/workflows/{workflow_id}/run')
    a=1

if __name__ == "__main__":
    test_id = uuid()
    workflow_owner = f"Test Owner {test_id}"
    workflow_name = f"Test Workflow {test_id}"

    print("Creating Workflow...")
    workflow = create_workflow(workflow_name, workflow_owner)
    print(f" - {workflow.ID}")

    assert get_workflow(workflow.ID).ID == workflow.ID
    print("✅\n\n")

    # --------------------------------------------------

    print("Creating String Producer Node...")
    node = create_node(
        workflow_id=workflow.ID,
        address="nodes.builtins.producers.StringProducer",
        version=0,
    )
    print(f" - {node.ID}")

    assert get_node(workflow.ID, node.ID).ID == node.ID
    print("✅\n\n")

    # --------------------------------------------------

    print("Adding Data to String Producer Node...")
    node = add_data_to_node(
        workflow_id=workflow.ID,
        node_id=node.ID,
        node_data_type="options",
        key="options",
        data={"value": f"Test Data: {test_id}"},
    )

    node_w_data = get_node(workflow.ID, node.ID)
    assert node_w_data.ID == node.ID
    assert node_w_data.Data["options"].Type == "options"
    assert isinstance(node_w_data.Data["options"].Value, dict)
    assert node_w_data.Data["options"].Value["value"] == f"Test Data: {test_id}"
    print("✅\n\n")

    print("Adding HTTP Get Request Node...")
    request_node = create_node(
        workflow_id=workflow.ID,
        address="nodes.builtins.requests.HTTPGetRequest",
        version=0,
    )
    print(f" - {request_node.ID}")

    assert get_node(workflow.ID, request_node.ID).ID == request_node.ID
    print("✅\n\n")

    print("Creating new Edge from String Producer to HTTP Get...")
    edge = add_edge_to_workflow(
        workflow.ID,
        from_data=NodeDataHandle(NodeID=node.ID, Key="output"),
        to_data=NodeDataHandle(NodeID=request_node.ID, Key="url"),
    )
    print(f" - {edge.ID}")
    assert get_edge_from_workflow(workflow.ID, edge.ID).ID == edge.ID
    print("✅\n\n")

    run_workflow(workflow_id = workflow.ID)

    print("\n\nAll Good! 😎")
