import { Table, TableHeader, TableHead, TableBody, TableCaption, TableCell, TableRow } from "../ui/table";
import { Node } from "@/api/nodeAPI";
import { MoreVertical } from "lucide-react"

export default function NodeTableSelector({ nodes, selected, setSelected }: { nodes: Node[], selected: Node | null, setSelected: (node: Node) => void}) {
  console.log(selected);
  return (
    <Table>
      <TableCaption>Select a Node</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Group</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {nodes.map((node) => {
          return (
            <TableRow key={node.Address} className={selected?.Address===node.Address? "bg-accent": ""} onClick={() => setSelected? setSelected(node): {}}>
              <TableCell>{node.Label}</TableCell>
              <TableCell>{node.Group}</TableCell>
              <TableCell className="text-right">
                <button onClick={() => setSelected(node)}><MoreVertical/></button>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
      
    </Table>
  );
}
