import argparse
import json
from pathlib import Path
import sys
from typing import List, Sequence

from reservas.errores import ErrorReserva
from reservas.servicio import ServicioReservas

def obtener_ruta_db_defecto() -> str:
    raiz = Path(__file__).parent.parent
    return str(raiz / "data" / "reservas.db")

def obtener_inventario_defecto() -> List[dict]:
    ruta_inv = Path(__file__).parent.parent / "data" / "inventario.json"
    with open(ruta_inv, "r", encoding="utf-8") as f:
        return json.load(f)

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sistema de reservas de laboratorio")
    parser.add_argument("--db", default=obtener_ruta_db_defecto(), help="Ruta a la base de datos SQLite")

    subparsers = parser.add_subparsers(dest="comando", required=True)

    # init
    subparsers.add_parser("init", help="Inicializa el sistema")

    # inventario
    subparsers.add_parser("inventario", help="Lista las unidades del inventario")

    # disponibilidad UNIDAD INICIO FIN
    parser_disp = subparsers.add_parser("disponibilidad", help="Consulta disponibilidad de una unidad")
    parser_disp.add_argument("unidad", help="ID de la unidad")
    parser_disp.add_argument("inicio", help="Fecha/hora inicio ISO (YYYY-MM-DDTHH:MM)")
    parser_disp.add_argument("fin", help="Fecha/hora fin ISO (YYYY-MM-DDTHH:MM)")

    # reservar UNIDAD SOLICITANTE INICIO FIN
    parser_res = subparsers.add_parser("reservar", help="Crea una reserva")
    parser_res.add_argument("unidad", help="ID de la unidad")
    parser_res.add_argument("solicitante", help="Nombre del solicitante")
    parser_res.add_argument("inicio", help="Fecha/hora inicio ISO (YYYY-MM-DDTHH:MM)")
    parser_res.add_argument("fin", help="Fecha/hora fin ISO (YYYY-MM-DDTHH:MM)")

    # cancelar ID
    parser_canc = subparsers.add_parser("cancelar", help="Cancela una reserva")
    parser_canc.add_argument("id", type=int, help="ID de la reserva")

    # listar [--estado activa|cancelada]
    parser_list = subparsers.add_parser("listar", help="Lista las reservas")
    parser_list.add_argument("--estado", choices=["activa", "cancelada"], help="Filtrar por estado")

    # reiniciar-datos --confirmar
    parser_reset = subparsers.add_parser("reiniciar-datos", help="Borra todas las reservas")
    parser_reset.add_argument("--confirmar", action="store_true", help="Confirmar el borrado de datos")

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    inventario = obtener_inventario_defecto()
    servicio = ServicioReservas(ruta_db=args.db, inventario=inventario)

    try:
        if args.comando == "init":
            # Inicialización implícita al instanciar el servicio
            return 0

        elif args.comando == "inventario":
            for unit in servicio.listar_inventario():
                print(f"{unit['id']}: {unit['nombre']}")
            return 0

        elif args.comando == "disponibilidad":
            disp = servicio.disponible(args.unidad, args.inicio, args.fin)
            if disp:
                print(f"DISPONIBLE: la unidad {args.unidad} se puede reservar en el intervalo {args.inicio} - {args.fin}.")
            else:
                print(f"NO DISPONIBLE: la unidad {args.unidad} tiene una reserva activa en el intervalo {args.inicio} - {args.fin}.")
            return 0

        elif args.comando == "reservar":
            reserva = servicio.reservar(args.unidad, args.solicitante, args.inicio, args.fin)
            print(f"Reserva creada exitosamente con ID {reserva.id}.")
            return 0

        elif args.comando == "cancelar":
            reserva = servicio.cancelar(args.id)
            print(f"Reserva {reserva.id} cancelada exitosamente.")
            return 0

        elif args.comando == "listar":
            reservas = servicio.listar(estado=args.estado)
            for r in reservas:
                ini_str = r.inicio.strftime("%Y-%m-%dT%H:%M")
                fin_str = r.fin.strftime("%Y-%m-%dT%H:%M")
                print(f"ID {r.id} | {r.unidad} | {r.solicitante} | {ini_str} | {fin_str} | {r.estado}")
            return 0

        elif args.comando == "reiniciar-datos":
            if not args.confirmar:
                print("Error: debe incluir la opción --confirmar para reiniciar todos los datos.", file=sys.stderr)
                return 1
            servicio.reiniciar_datos()
            print("Todos los datos de reservas han sido reiniciados.")
            return 0

    except ErrorReserva as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        servicio.cerrar()

    return 0

if __name__ == "__main__":
    sys.exit(main())
