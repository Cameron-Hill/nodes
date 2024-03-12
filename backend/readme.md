## Get Started

### Environment

Formatter: [Black]

### Install

    pip install -r requirements.txt

### Start dynamoDB LOCAL

Set DynamoDB local path

    set DYNAMODB_PATH=E:\Cambo\Docs\Dynamodb

Run Start Script

    ddb.bat

### Start Server

    uvicorn server.main:app --reload --port 8081

### Notes

#### Schemas

Schemas are used to control the connections between nodes and manage the flow of data throughout the workflow.

Schemas are produced in 2 ways.

First, A high level 'declarative' schema is created when the node is created. All inputs, options and outputs should have a type associated with them. Types can be simple (int, str, float, etc) or complex (Pydantic Models). This applies when we have an have not seen the data, but we have an expectation of what the data 'will be'. This schema is primarily used to validate the inputs and outputs of the node.

The second is a 'procedural' schema. This schema is created whenever we have a reference to the 'actual' data as well as the declarative schema. A procedural schema is created by the node itself once it has been hydrated with the data as long as that data is valid according to the declarative schema. The procedural schema will be used in place of the declarative schema whenever a procedural schema is available.

Sometimes, a node may consume or produce data with a schema that is not known at the time of creation. In this case, the node should be created with an 'Unknown' Type. Unknown types can be converted to known types using assertion nodes.

#### Assertion Nodes

Assertion nodes are used to convert unknown types to known types. An assertion node is defined by providing options to describe the expected type format. This will produce a procedural schema that can be used by other nodes.
Unknown data is then fed into an assertion node, and if the data is valid according to procedural schema, the data can flow to the next node. If the data is not valid, the assertion node will raise an error and halt the workflow.
