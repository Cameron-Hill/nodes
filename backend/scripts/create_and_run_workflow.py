from shortuuid import uuid
import requests
from pprint import pprint
from server.database.tables import WorkflowTable, NodeDataTypes
from typing import Any

URL = "http://localhost:8081"


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
    print("GET", url, query, headers)
    response = requests.get(url, params=query, headers=headers)
    response.raise_for_status()
    return response.json()


@exception_handler
def post(path, data: dict, headers: dict | None = None) -> dict:
    url = f'{URL}/{path.lstrip("/")}'.rstrip("/") + "/"
    print("POST", url, data, headers)
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

def get_nodes(workflow_id:str) -> list[WorkflowTable.Node]:
    data = get(f"/workflows/{workflow_id}/nodes/")
    return [WorkflowTable.Node(**x) for x in data]

def get_node(workflow_id: str, node_id: str) -> WorkflowTable.Node:
    data = get(f"/workflows/{workflow_id}/nodes/{node_id}")
    return WorkflowTable.Node(**data)


def add_data_to_node(
    workflow_id: str, node_id: str, node_data_type: NodeDataTypes, key: str, data: Any
) -> WorkflowTable.NodeData:
    data = post(
        f"/workflows/{workflow_id}/nodes/{node_id}/data/",
        {"Key": key, "Type": node_data_type, "Data": data},
    )
    return WorkflowTable.NodeData(**data)

def get_node_data(workflow_id: str, node_id:str)-> list[WorkflowTable.NodeData]:
    data = get(
        f"/workflows/{workflow_id}/nodes/{node_id}/data/",
    )
    return [WorkflowTable.NodeData(**x) for x in data]


if __name__ == "__main__":
    test_id = uuid()
    workflow_owner = f"Test Owner {test_id}"
    workflow_name = f"Test Workflow {test_id}"

    print("Creating Workflow...")
    workflow = create_workflow(workflow_name, workflow_owner)
    print(f"Created Workflow: {workflow.Name} with ID: {workflow.ID}")

    print("Verifying workflow ID")
    assert get_workflow(workflow.ID).ID == workflow.ID
    print("Good!\n\n")

    # --------------------------------------------------

    print("Creating Node...")
    node = create_node(
        workflow_id=workflow.ID,
        address="nodes.builtins.producers.StringProducer",
        version=0,
    )
    print(f"Created Node: {node.Address} with ID: {node.ID}")

    print("Verifying node ID")
    assert get_node(workflow.ID, node.ID).ID == node.ID
    print("Good!\n\n")

    # --------------------------------------------------

    print("Adding Data to Node...")
    node_data = add_data_to_node(
        workflow_id=workflow.ID,
        node_id=node.ID,
        node_data_type="options",
        key="options",
        data={"value": f"Test Data: {test_id}"},
    )
    print(f"Added Data to Node: {node_data.Key} with ID: {node_data.ID}")

    print("Verifying node Data in Workflow")
    workflow_node_data = get_node_data(workflow.ID, node.ID)
    assert node_data.ID in [x.ID for x in workflow_node_data]   
    print('\n\nAll Good! 😎')