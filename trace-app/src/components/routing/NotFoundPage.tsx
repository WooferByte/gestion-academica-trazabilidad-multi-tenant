import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-md bg-background">
      <h1 className="font-headline-lg text-headline-lg text-on-surface">404</h1>
      <p className="font-body-lg text-body-lg text-secondary">
        Página no encontrada
      </p>
      <p className="font-body-md text-body-md text-on-surface-variant">
        La página que buscás no existe o fue movida
      </p>
      <Link to="/dashboard">
        <Button variant="primary">Ir al Dashboard</Button>
      </Link>
    </div>
  );
}

export default NotFoundPage;
