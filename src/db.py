import sqlite3
from contextlib import contextmanager


class DB:
    def __init__(self, db_path="db/training.db"):
        self.path = db_path

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        try:
            yield conn
        finally:
            conn.close()

    def init_schema(self):
        with self.connection() as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS lifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                bodyweight REAL,
                lift TEXT NOT NULL,
                weight REAL NOT NULL,
                reps INTEGER NOT NULL,
                top_set BOOLEAN DEFAULT 0,
                reps_in_reserve INTEGER,
                filepath TEXT,
                program TEXT,
                program_iteration INTEGER
            )""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_lifts_date ON lifts(date)")
            conn.commit()

    def add_lift_entry(self, **kwargs):
        with self.connection() as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO lifts 
                (date,bodyweight,lift,weight,reps,top_set,reps_in_reserve,filepath,program,program_iteration)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    kwargs["date"],
                    kwargs.get("bodyweight"),
                    kwargs["lift"],
                    kwargs["weight"],
                    kwargs["reps"],
                    kwargs.get("top_set", False),
                    kwargs.get("reps_in_reserve"),
                    kwargs.get("filepath"),
                    kwargs.get("program"),
                    kwargs.get("program_iteration"),
                ),
            )
            conn.commit()
            return c.lastrowid

    def add_session_entries(self, entries):
        with self.connection() as conn:
            c = conn.cursor()
            # Each entry tuple has 7 values (date,bodyweight,lift,weight,reps,top_set,reps_in_reserve)
            placeholders = ",".join(["?" for _ in range(len(entries[0]))])
            cols = ", ".join(
                [
                    "date",
                    "bodyweight",
                    "lift",
                    "weight",
                    "reps",
                    "top_set",
                    "reps_in_reserve",
                ]
            )
            # Use executemany for efficient batch insert
            c.executemany(
                f"""INSERT INTO lifts ({cols}) VALUES ({placeholders})""", entries
            )
            conn.commit()

    def list_entries(self, query="SELECT * FROM lifts"):
        with self.connection() as conn:
            c = conn.cursor()
            c.execute(query)
            return c.fetchall()

    def update_entry(self, entry_id, **kwargs):
        with self.connection() as conn:
            c = conn.cursor()
            updates = []
            values = []
            col_map = {
                "date": "date",
                "bodyweight": "bodyweight",
                "lift": "lift",
                "weight": "weight",
                "reps": "reps",
                "top_set": "top_set",
                "reps_in_reserve": "reps_in_reserve",
                "filepath": "filepath",
                "program": "program",
                "program_iteration": "program_iteration",
            }
            for k in kwargs.keys():
                if k in col_map:
                    updates.append(f"{col_map[k]}=?")
                    values.append(kwargs[k])

            if not updates:
                return

            # Build SET clause with string-formatted values (sqlite3 parser doesn't handle ? in SET clause)
            set_clause_parts = []
            for update_expr, val in zip(updates, values):
                col_name = update_expr.strip().replace(
                    "=?", ""
                )  # Extract column name from "weight=?"
                safe_val = str(val).replace("'", "''")
                set_clause_parts.append(f"{col_name}='{safe_val}'")

            sql = f"""UPDATE lifts 
                     SET {", ".join(set_clause_parts)} 
                     WHERE id=?"""
            c.execute(sql, (entry_id,))
            conn.commit()
