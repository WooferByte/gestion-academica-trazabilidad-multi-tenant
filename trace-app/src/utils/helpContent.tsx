import type { ReactNode } from "react";

type HelpContentMap = Record<string, ReactNode>;

export const helpContent: HelpContentMap = {
  equipos: (
    <div className="space-y-4 text-zinc-300">
      <p className="text-lg font-medium text-[var(--text-inverse)]">
        Equipos Docentes
      </p>
      <p>
        Gestiona las asignaciones de docentes a materias, carreras y cohortes.
        Podes ver tus asignaciones, crear asignaciones masivas, clonar equipos
        entre periodos y modificar la vigencia en lote.
      </p>
      <ul className="list-disc list-inside space-y-2 ml-4">
        <li>
          <strong>Mis Equipos:</strong> Vista de tus asignaciones activas con
          filtros por materia, rol y cohorte.
        </li>
        <li>
          <strong>Asignacion Masiva:</strong> Asigna multiples docentes en
          bloque a una materia x carrera x cohorte.
        </li>
        <li>
          <strong>Clonar Equipo:</strong> Duplica asignaciones de un periodo
          origen a un periodo destino.
        </li>
        <li>
          <strong>Vigencia:</strong> Actualiza las fechas desde/hasta de todo
          un equipo en una sola operacion.
        </li>
      </ul>
      <div className="bg-zinc-800 p-4 rounded-lg mt-4">
        <p className="text-orange-400 font-medium">Consejo:</p>
        <p className="text-sm mt-1">
          Usa la asignacion masiva al inicio del cuatrimestre para configurar
          todos los docentes de una vez. Luego clona el equipo para el
          siguiente periodo.
        </p>
      </div>
    </div>
  ),
  avisos: (
    <div className="space-y-4 text-zinc-300">
      <p className="text-lg font-medium text-[var(--text-inverse)]">
        Avisos
      </p>
      <p>
        Publica avisos institucionales con alcance configurable (Global, por
        Materia, por Cohorte, o por Rol). Los destinatarios pueden confirmar
        la lectura.
      </p>
      <ul className="list-disc list-inside space-y-2 ml-4">
        <li>
          <strong>Nuevo Aviso:</strong> Crea un aviso con titulo, cuerpo,
          severidad y vigencia.
        </li>
        <li>
          <strong>Alcance:</strong> Segun el alcance elegido, podes
          seleccionar materia, cohorte o rol destino.
        </li>
        <li>
          <strong>Confirmacion de Lectura:</strong> Si activas esta opcion,
          los destinatarios deberan confirmar que leyeron el aviso.
        </li>
      </ul>
      <div className="bg-zinc-800 p-4 rounded-lg mt-4">
        <p className="text-orange-400 font-medium">Importante:</p>
        <p className="text-sm mt-1">
          Los avisos vencidos se ocultan automaticamente. Programa la vigencia
          correctamente al crear el aviso.
        </p>
      </div>
    </div>
  ),
  avisosActivos: (
    <div className="space-y-4 text-zinc-300">
      <p className="text-lg font-medium text-[var(--text-inverse)]">
        Avisos Activos
      </p>
      <p>
        Aca se muestran los avisos activos que estan dirigidos a vos segun tu
        rol, tus materias y tus cohortes.
      </p>
      <ul className="list-disc list-inside space-y-2 ml-4">
        <li>
          <strong>Confirmar Lectura:</strong> Si un aviso lo requiere, hace
          clic en "Confirmar lectura" para registrarlo.
        </li>
        <li>
          <strong>Avisos Leidos:</strong> Los avisos ya confirmados muestran
          un indicador verde.
        </li>
      </ul>
      <div className="bg-zinc-800 p-4 rounded-lg mt-4">
        <p className="text-orange-400 font-medium">Nota:</p>
        <p className="text-sm mt-1">
          Los avisos se actualizan automaticamente cada 30 segundos.
        </p>
      </div>
    </div>
  ),
  encuentros: (
    <div className="space-y-4 text-zinc-300">
      <p className="text-lg font-medium text-[var(--text-inverse)]">
        Encuentros
      </p>
      <p>
        Gestioná los encuentros sincrónicos de tus materias. Crea slots recurrentes
        o únicos, editá instancias individuales y generá bloques HTML para el aula virtual.
      </p>
      <ul className="list-disc list-inside space-y-2 ml-4">
        <li>
          <strong>Slots:</strong> Crea slots recurrentes semanales o encuentros únicos.
          Cada slot genera instancias automáticas.
        </li>
        <li>
          <strong>Instancias:</strong> Editá el estado, enlace Meet, URL de grabación
          y comentarios de cada encuentro individual.
        </li>
        <li>
          <strong>HTML Export:</strong> Generá un bloque HTML con el calendario de
          encuentros y grabaciones para copiar al LMS.
        </li>
      </ul>
      <div className="bg-zinc-800 p-4 rounded-lg mt-4">
        <p className="text-orange-400 font-medium">Consejo:</p>
        <p className="text-sm mt-1">
          Usá slots recurrentes al inicio del cuatrimestre para generar todos los
          encuentros de una vez. Luego editá cada instancia con los enlaces
          específicos.
        </p>
      </div>
    </div>
  ),
  guardias: (
    <div className="space-y-4 text-zinc-300">
      <p className="text-lg font-medium text-[var(--text-inverse)]">
        Guardias
      </p>
      <p>
        Registrá y consultá las guardias docentes. Los TUTORES pueden registrar
        sus guardias y los COORDINADORES pueden consultar el listado global con filtros.
      </p>
      <ul className="list-disc list-inside space-y-2 ml-4">
        <li>
          <strong>Registrar Guardia:</strong> Los TUTORES registran día, horario
          y comentarios de la guardia.
        </li>
        <li>
          <strong>Consulta Global:</strong> Los COORDINADORES ven todas las guardias
          con filtros por materia, carrera, cohorte y estado.
        </li>
        <li>
          <strong>Exportar CSV:</strong> Descargá el listado filtrado en formato CSV.
        </li>
      </ul>
    </div>
  ),
  coloquios: (
    <div className="space-y-4 text-zinc-300">
      <p className="text-lg font-medium text-[var(--text-inverse)]">
        Coloquios
      </p>
      <p>
        Gestioná las convocatorias de coloquio con turnos, cupos, reservas y
        resultados. Visualizá métricas globales y la agenda consolidada.
      </p>
      <ul className="list-disc list-inside space-y-2 ml-4">
        <li>
          <strong>Métricas:</strong> Panel con KPIs de convocatorias activas,
          alumnos convocados, reservas y resultados.
        </li>
        <li>
          <strong>Convocatorias:</strong> Creá convocatorias con múltiples turnos
          y cupos configurables por turno.
        </li>
        <li>
          <strong>Reservas:</strong> Los alumnos pueden reservar turnos con cupo
          disponible y cancelar sus reservas.
        </li>
        <li>
          <strong>Resultados:</strong> Registrá notas finales por alumno en cada
          convocatoria.
        </li>
        <li>
          <strong>Agenda:</strong> Visualizá los turnos con ocupación y alumnos
          reservados.
        </li>
      </ul>
    </div>
  ),
};
