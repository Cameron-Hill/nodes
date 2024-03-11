import { Save } from "lucide-react";
import Loader from "./Loader";

export default function SaveButton({
  saving,
  onSaveRequest,
}: {
  saving: boolean;
  onSaveRequest: () => void;
}) {
  return (
    <div className="h-7 w-7">
      {saving && <Loader />}
      {!saving && (
        <Save
          className="transition-colors hover:text-slate-500"
          onClick={onSaveRequest}
        />
      )}
    </div>
  );
}
