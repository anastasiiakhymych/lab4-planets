
import re

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DSN = "postgresql://postgres:postgres@localhost:5432/planets"

app = FastAPI(
    title="Планети",
    description="REST API для роботи з каталогом планет",
    version="1.0.0",
)


class PlanetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    planet_type: str = Field(min_length=1, max_length=50)
    radius_km: float = Field(gt=0)
    mass_earth: float = Field(gt=0)
    star_system_id: int = Field(gt=0)


def validate_name(name: str) -> bool:
    return re.fullmatch(r"[A-Za-zА-Яа-яІіЇїЄєҐґ0-9 -]+", name) is not None


@app.get("/")
def home():
    return {"message": "API каталогу планет працює"}


@app.get("/planets")
def get_planets():
    with psycopg.connect(DSN, row_factory=psycopg.rows.dict_row) as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.name, p.planet_type, p.radius_km,
                   p.mass_earth, s.name AS star_system
            FROM planets p
            JOIN star_systems s ON p.star_system_id = s.id
            ORDER BY p.id
            """
        ).fetchall()
    return rows


@app.get("/planets/{planet_id}")
def get_planet(planet_id: int):
    with psycopg.connect(DSN, row_factory=psycopg.rows.dict_row) as conn:
        row = conn.execute(
            """
            SELECT id, name, planet_type, radius_km,
                   mass_earth, star_system_id
            FROM planets WHERE id = %s
            """,
            (planet_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Планету не знайдено")
    return row


@app.post("/planets", status_code=201)
def create_planet(planet: PlanetCreate):
    if not validate_name(planet.name):
        raise HTTPException(
            status_code=422,
            detail="Назва містить недопустимі символи",
        )

    with psycopg.connect(DSN, row_factory=psycopg.rows.dict_row) as conn:
        system = conn.execute(
            "SELECT id FROM star_systems WHERE id = %s",
            (planet.star_system_id,),
        ).fetchone()

        if system is None:
            raise HTTPException(
                status_code=400,
                detail="Зоряну систему не знайдено",
            )

        row = conn.execute(
            """
            INSERT INTO planets
                (name, planet_type, radius_km, mass_earth, star_system_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, planet_type, radius_km,
                      mass_earth, star_system_id
            """,
            (
                planet.name,
                planet.planet_type,
                planet.radius_km,
                planet.mass_earth,
                planet.star_system_id,
            ),
        ).fetchone()

    return row


@app.put("/planets/{planet_id}")
def update_planet(planet_id: int, planet: PlanetCreate):
    if not validate_name(planet.name):
        raise HTTPException(
            status_code=422,
            detail="Назва містить недопустимі символи",
        )

    with psycopg.connect(DSN, row_factory=psycopg.rows.dict_row) as conn:
        row = conn.execute(
            """
            UPDATE planets
            SET name = %s, planet_type = %s, radius_km = %s,
                mass_earth = %s, star_system_id = %s
            WHERE id = %s
            RETURNING id, name, planet_type, radius_km,
                      mass_earth, star_system_id
            """,
            (
                planet.name,
                planet.planet_type,
                planet.radius_km,
                planet.mass_earth,
                planet.star_system_id,
                planet_id,
            ),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Планету не знайдено")
    return row


@app.delete("/planets/{planet_id}")
def delete_planet(planet_id: int):
    with psycopg.connect(DSN) as conn:
        cursor = conn.execute(
            "DELETE FROM planets WHERE id = %s",
            (planet_id,),
        )

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Планету не знайдено")

    return {"message": "Планету видалено", "id": planet_id}
