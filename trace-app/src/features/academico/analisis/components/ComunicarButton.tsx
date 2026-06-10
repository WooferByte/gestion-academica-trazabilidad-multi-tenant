import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";

type ComunicarButtonProps = {
  selectedIds: string[];
};

export function ComunicarButton({ selectedIds }: ComunicarButtonProps) {
  const navigate = useNavigate();
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();

  return (
    <Button
      disabled={selectedIds.length === 0}
      onClick={() =>
        navigate(`/academico/${materiaId}/${cohorteId}/comunicar`, {
          state: { selectedAlumnos: selectedIds },
        })
      }
    >
      Comunicar ({selectedIds.length})
    </Button>
  );
}
