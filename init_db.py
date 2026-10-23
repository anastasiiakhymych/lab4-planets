
import psycopg

DSN = "postgresql://postgres:postgres@localhost:5432/planets"


def create_tables():
    with psycopg.connect(DSN) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS star_systems (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                star_type VARCHAR(50) NOT NULL,
                distance_ly DOUBLE PRECISION
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS planets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                planet_type VARCHAR(50) NOT NULL,
                radius_km DOUBLE PRECISION NOT NULL,
                mass_earth DOUBLE PRECISION NOT NULL,
                star_system_id INTEGER NOT NULL
                    REFERENCES star_systems(id)
                    ON DELETE CASCADE,
                UNIQUE (name, star_system_id)
            );
        """)

    print("Таблиці успішно створено.")


if __name__ == "__main__":
    create_tables()
