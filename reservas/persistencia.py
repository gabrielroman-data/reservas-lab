from datetime import datetime
from pathlib import Path
import sqlite3

from reservas.dominio import Reserva

class AlmacenSQLite:
    def __init__(self, ruta_db: str | Path):
        self.ruta_db = str(ruta_db)
        self._conexion = sqlite3.connect(self.ruta_db)
        self._conexion.row_factory = sqlite3.Row
        self._crear_tablas()

    def _crear_tablas(self):
        with self._conexion:
            self._conexion.execute("""
                CREATE TABLE IF NOT EXISTS reservas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unidad TEXT NOT NULL,
                    solicitante TEXT NOT NULL,
                    inicio TEXT NOT NULL,
                    fin TEXT NOT NULL,
                    estado TEXT NOT NULL
                )
            """)

    def obtener_conexion(self):
        return self._conexion

    def obtener_por_id(self, reserva_id: int) -> Reserva | None:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT id, unidad, solicitante, inicio, fin, estado FROM reservas WHERE id = ?",
            (reserva_id,)
        )
        fila = cursor.fetchone()
        if not fila:
            return None
        return Reserva(
            id=fila["id"],
            unidad=fila["unidad"],
            solicitante=fila["solicitante"],
            inicio=datetime.strptime(fila["inicio"], "%Y-%m-%dT%H:%M"),
            fin=datetime.strptime(fila["fin"], "%Y-%m-%dT%H:%M"),
            estado=fila["estado"]
        )

    def obtener_activas_por_unidad(self, unidad: str) -> list[tuple[int, datetime, datetime]]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT id, inicio, fin FROM reservas WHERE unidad = ? AND estado = 'activa'",
            (unidad,)
        )
        filas = cursor.fetchall()
        resultado = []
        for f in filas:
            ini_dt = datetime.strptime(f["inicio"], "%Y-%m-%dT%H:%M")
            fin_dt = datetime.strptime(f["fin"], "%Y-%m-%dT%H:%M")
            resultado.append((f["id"], ini_dt, fin_dt))
        return resultado

    def insertar_reserva(self, unidad: str, solicitante: str, inicio: datetime, fin: datetime) -> Reserva:
        ini_str = inicio.strftime("%Y-%m-%dT%H:%M")
        fin_str = fin.strftime("%Y-%m-%dT%H:%M")
        cursor = self._conexion.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            INSERT INTO reservas (unidad, solicitante, inicio, fin, estado)
            VALUES (?, ?, ?, ?, 'activa')
            """,
            (unidad, solicitante, ini_str, fin_str)
        )
        reserva_id = cursor.lastrowid
        self._conexion.commit()
        return Reserva(
            id=reserva_id,
            unidad=unidad,
            solicitante=solicitante,
            inicio=inicio,
            fin=fin,
            estado="activa"
        )

    def actualizar_estado(self, reserva_id: int, nuevo_estado: str) -> Reserva | None:
        cursor = self._conexion.cursor()
        with self._conexion:
            cursor.execute(
                "UPDATE reservas SET estado = ? WHERE id = ?",
                (nuevo_estado, reserva_id)
            )
        return self.obtener_por_id(reserva_id)

    def reiniciar_datos(self):
        with self._conexion:
            self._conexion.execute("DELETE FROM reservas")

    def listar(self, estado: str | None = None) -> list[Reserva]:
        cursor = self._conexion.cursor()
        if estado:
            cursor.execute("SELECT id, unidad, solicitante, inicio, fin, estado FROM reservas WHERE estado = ? ORDER BY id", (estado,))
        else:
            cursor.execute("SELECT id, unidad, solicitante, inicio, fin, estado FROM reservas ORDER BY id")
        
        filas = cursor.fetchall()
        reservas = []
        for f in filas:
            ini_dt = datetime.strptime(f["inicio"], "%Y-%m-%dT%H:%M")
            fin_dt = datetime.strptime(f["fin"], "%Y-%m-%dT%H:%M")
            reservas.append(Reserva(
                id=f["id"],
                unidad=f["unidad"],
                solicitante=f["solicitante"],
                inicio=ini_dt,
                fin=fin_dt,
                estado=f["estado"]
            ))
        return reservas

    def cerrar(self):
        if self._conexion:
            try:
                self._conexion.close()
            except sqlite3.ProgrammingError:
                pass
            self._conexion = None
