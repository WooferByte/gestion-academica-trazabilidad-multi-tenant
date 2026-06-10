import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { useAuth } from "@/features/auth/hooks/useAuth";

const codeSchema = z.object({
  code: z
    .string()
    .min(6, "El código debe tener 6 dígitos")
    .max(6, "El código debe tener 6 dígitos")
    .regex(/^\d{6}$/, "Solo números"),
});

type CodeFormData = z.infer<typeof codeSchema>;

export function TwoFactorPage() {
  const { verify2fa } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const tempToken = (location.state as { temp_token?: string })?.temp_token;
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CodeFormData>({
    resolver: zodResolver(codeSchema),
  });

  const onSubmit = async (data: CodeFormData) => {
    if (!tempToken) {
      navigate("/login", { replace: true });
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await verify2fa({ code: data.code, temp_token: tempToken });
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } };
      setError(apiError?.response?.data?.detail ?? "Código inválido");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-sm p-xl">
        <div className="mb-lg text-center">
          <h1 className="font-headline-md text-headline-md text-on-surface">
            Verificación en dos pasos
          </h1>
          <p className="mt-sm font-body-md text-body-md text-secondary">
            Ingresá el código de 6 dígitos de tu aplicación autenticadora
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-md">
          <Input
            label="Código"
            placeholder="000000"
            maxLength={6}
            inputMode="numeric"
            autoComplete="one-time-code"
            error={errors.code?.message}
            {...register("code")}
          />

          {error && (
            <p className="font-body-sm text-body-sm text-error" role="alert">
              {error}
            </p>
          )}

          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? "Verificando..." : "Verificar"}
          </Button>
        </form>

        <div className="mt-md text-center">
          <Link
            to="/login"
            className="font-body-sm text-body-sm text-secondary hover:text-on-surface underline"
          >
            Volver al inicio de sesión
          </Link>
        </div>
      </Card>
    </div>
  );
}

export default TwoFactorPage;
