import psycopg

DSN = "postgresql://postgres:postgres@localhost:5432/planets"

SYSTEMS = [
    ("Сонячна система", "G-type", 0.0),
    ("Kepler-90", "G-type", 2545.0),
    ("TRAPPIST-1", "M-type", 39.5),
    ("Kepler-11", "G-type", 2000.0),
    ("HD 10180", "G-type", 127.0),
    ("55 Cancri", "G-type", 41.0),
    ("Gliese 667", "M-type", 23.6),
    ("Kepler-62", "K-type", 1200.0),
    ("Upsilon Andromedae", "F-type", 44.0),
    ("WASP-12", "F-type", 1400.0),
]

PLANETS = [
    ("Меркурій", "Terrestrial", 2439.7, 0.055, "Сонячна система"),
    ("Венера", "Terrestrial", 6051.8, 0.815, "Сонячна система"),
    ("Земля", "Terrestrial", 6371.0, 1.0, "Сонячна система"),
    ("Марс", "Terrestrial", 3389.5, 0.107, "Сонячна система"),
    ("Юпітер", "Gas giant", 69911.0, 317.8, "Сонячна система"),
    ("Сатурн", "Gas giant", 58232.0, 95.2, "Сонячна система"),
    ("Уран", "Ice giant", 25362.0, 14.5, "Сонячна система"),
    ("Нептун", "Ice giant", 24622.0, 17.1, "Сонячна система"),
]

# Додаємо ще 50 тестових планет до десяти зоряних систем.
for system_name, star_type, distance in SYSTEMS[1:]:
    prefix = system_name.replace("-", "").replace(" ", "")
    for number in range(1, 6):
        PLANETS.append((
            f"{prefix}-Planet-{number}",
            "Exoplanet",
            5000.0 + number * 1200.0,
            0.5 + number * 1.25,
            system_name,
        ))


def seed_database():
    with psycopg.connect(DSN) as conn:
        for name, star_type, distance in SYSTEMS:
            conn.execute(
                """
                INSERT INTO star_systems (name, star_type, distance_ly)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                """,
                (name, star_type, distance),
            )

        for name, planet_type, radius, mass, system_name in PLANETS:
            conn.execute(
                """
                INSERT INTO planets
                    (name, planet_type, radius_km, mass_earth, star_system_id)
                VALUES (
                    %s, %s, %s, %s,
                    (SELECT id FROM star_systems WHERE name = %s)
                )
                ON CONFLICT (name, star_system_id) DO NOTHING
                """,
                (name, planet_type, radius, mass, system_name),
            )

        system_count = conn.execute(
            "SELECT COUNT(*) FROM star_systems"
        ).fetchone()[0]

        planet_count = conn.execute(
            "SELECT COUNT(*) FROM planets"
        ).fetchone()[0]

    print(f"Кількість зоряних систем: {system_count}")
    print(f"Кількість планет: {planet_count}")


if __name__ == "__main__":
    seed_database()
