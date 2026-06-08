import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { useAuth } from "@/features/auth/hooks/useAuth";

const emailSchema = z.object({
  email: z.string().min(1, "El email es requerido").email("Email inválido"),
});

const confirmSchema = z
  .object({
    new_password: z
      .string()
      .min(8, "La contraseña debe tener al menos 8 caracteres"),
    confirm_password: z.string().min(1, "Confirmá la contraseña"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Las contraseñas no coinciden",
    path: ["confirm_password"],
  });

type EmailFormData = z.infer<typeof emailSchema>;
type ConfirmFormData = z.infer<typeof confirmSchema>;

export function RecoveryPage() {
  const { requestRecovery, confirmRecovery } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [recoveryToken, setRecoveryToken] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const emailForm = useForm<EmailFormData>({
    resolver: zodResolver(emailSchema),
  });

  const confirmForm = useForm<ConfirmFormData>({
    resolver: zodResolver(confirmSchema),
  });

  const onEmailSubmit = async (data: EmailFormData) => {
    setError(null);
    setMessage(null);
    setIsSubmitting(true);
    try {
      const result = await requestRecovery(data);
      if (result.token) {
        setRecoveryToken(result.token);
        setMessage(`Token de recuperación: ${result.token}`);
      } else {
        setMessage("Si el email existe, recibirás instrucciones");
      }
      setStep(2);
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } };
      setError(
        apiError?.response?.data?.detail ??
          "Error al solicitar recuperación",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const onConfirmSubmit = async (data: ConfirmFormData) => {
    if (!recoveryToken) return;
    setError(null);
    setIsSubmitting(true);
    try {
      await confirmRecovery({
        token: recoveryToken,
        new_password: data.new_password,
      });
      setStep(3);
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } };
      setError(
        apiError?.response?.data?.detail ?? "Error al recuperar contraseña",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-sm p-xl">
        <div className="mb-lg text-center">
          <h1 className="font-headline-md text-headline-md text-on-surface">
            Recuperar Contraseña
          </h1>
        </div>

        {step === 1 && (
          <form
            onSubmit={emailForm.handleSubmit(onEmailSubmit)}
            className="flex flex-col gap-md"
          >
            <Input
              label="Email"
              type="email"
              placeholder="tu@email.com"
              error={emailForm.formState.errors.email?.message}
              {...emailForm.register("email")}
            />

            {error && (
              <p className="font-body-sm text-body-sm text-error" role="alert">
                {error}
              </p>
            )}

            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Enviando..." : "Enviar código"}
            </Button>
          </form>
        )}

        {step === 2 && (
          <div className="flex flex-col gap-md">
            {message && (
              <p className="font-body-sm text-body-sm text-green-700" role="status">
                {message}
              </p>
            )}

            <form
              onSubmit={confirmForm.handleSubmit(onConfirmSubmit)}
              className="flex flex-col gap-md"
            >
              <Input
                label="Nueva contraseña"
                type="password"
                placeholder="••••••••"
                error={confirmForm.formState.errors.new_password?.message}
                {...confirmForm.register("new_password")}
              />

              <Input
                label="Confirmar contraseña"
                type="password"
                placeholder="••••••••"
                error={confirmForm.formState.errors.confirm_password?.message}
                {...confirmForm.register("confirm_password")}
              />

              {error && (
                <p
                  className="font-body-sm text-body-sm text-error"
                  role="alert"
                >
                  {error}
                </p>
              )}

              <Button type="submit" disabled={isSubmitting} className="w-full">
                {isSubmitting ? "Guardando..." : "Cambiar contraseña"}
              </Button>
            </form>
          </div>
        )}

        {step === 3 && (
          <div className="flex flex-col gap-md text-center">
            <p className="font-body-md text-body-md text-green-700" role="status">
              Contraseña actualizada correctamente
            </p>
            <Button onClick={() => navigate("/login")} className="w-full">
              Volver al inicio de sesión
            </Button>
          </div>
        )}

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

export default RecoveryPage;
