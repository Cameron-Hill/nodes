from create_and_run_workflow import get_all_workflows, get_workflow, get_node_data, get_node, get_nodes


if __name__ == "__main__":
    print('Fetching workflows...')
    workflows = get_all_workflows()
    print(f'Found {len(workflows)}')
    if not workflows:
        print('No workflows found')
        exit(0)
    workflow = workflows[0]

    print(f'Getting workflow: {workflow.ID}')
    assert get_workflow(workflow_id=workflow.ID).ID == workflow.ID
    print('Good 👍')

    print('Getting nodes for workflow')
    nodes = get_nodes(workflow.ID)

    print(f'Workflow has {len(nodes)} Nodes.. Nice 👌')
