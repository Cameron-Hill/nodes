import { useEffect, useState } from "react";

export function useSchedule(
  callback: () => void,
  interval: number,
  dependencies: unknown[],
) {
  const [saveFlag, setSaveFlag] = useState(false);
  const [lastSave, setLastSave] = useState(0);
  const [lastChange, setLastChange] = useState(0);

  useEffect(() => {
    setTimeout(() => setSaveFlag(!saveFlag), interval);
    if (lastChange > lastSave + interval) {
      setLastSave(lastChange);
      callback();
    }
  }, [saveFlag]);

  useEffect(() => {
    setLastChange(new Date().getTime());
  }, dependencies);
}
