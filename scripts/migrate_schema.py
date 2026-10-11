"""Database migration script for new taxonomic, ecological, claim, and audit fields."""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrate")

def run_migration():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    columns_to_add = [
        ("families", "order_name", "VARCHAR(100) DEFAULT 'Cichliformes'"),
        ("families", "class_name", "VARCHAR(100) DEFAULT 'Actinopterygii'"),
        ("families", "general_biology", "TEXT"),
        ("families", "distribution_overview", "TEXT"),
        ("families", "feeding_ecology", "TEXT"),
        ("families", "reproduction_overview", "TEXT"),
        ("families", "aquarium_care_overview", "TEXT"),
        ("genera", "author", "VARCHAR(255)"),
        ("genera", "year_described", "INTEGER"),
        ("genera", "subfamily", "VARCHAR(100)"),
        ("genera", "type_species", "VARCHAR(255)"),
        ("genera", "diagnostic_traits", "TEXT"),
        ("genera", "distribution", "TEXT"),
        ("genera", "taxonomic_notes", "TEXT"),
        ("species", "subspecies", "VARCHAR(255)"),
        ("species", "taxonomic_status", "VARCHAR(100) DEFAULT 'valid'"),
        ("species", "conservation_status", "VARCHAR(100)"),
        ("species", "depth_range", "VARCHAR(100)"),
        ("species", "dietary_category", "VARCHAR(100)"),
        ("species", "temperament", "VARCHAR(255)"),
        ("species", "conspecific_aggression", "TEXT"),
        ("species", "interspecific_aggression", "TEXT"),
        ("species", "tank_setup_notes", "TEXT"),
        ("species", "filtration_notes", "TEXT"),
        ("species", "water_changes_notes", "TEXT"),
        ("species", "taxonomic_notes", "TEXT"),
        ("species", "evidence_quality_note", "TEXT"),
        ("species", "last_verified_date", "VARCHAR(50)"),
    ]

    for table, col, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            logger.info(f"Added column {col} to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info(f"Column {col} already exists in {table}")
            else:
                logger.warning(f"Notice on {table}.{col}: {e}")

    # Create tables if not present
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scientific_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_id INTEGER NOT NULL REFERENCES species(id) ON DELETE CASCADE,
        claim_type VARCHAR(100) NOT NULL,
        claim_text TEXT NOT NULL,
        source_id INTEGER REFERENCES sources(id) ON DELETE SET NULL,
        exact_source_url VARCHAR(1000),
        source_section VARCHAR(500),
        evidence_label VARCHAR(50) DEFAULT 'scientific',
        verified_date VARCHAR(50),
        reviewer_notes TEXT
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_scientific_claims_species ON scientific_claims(species_id)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species_id INTEGER NOT NULL REFERENCES species(id) ON DELETE CASCADE,
        field_name VARCHAR(100) NOT NULL,
        old_value TEXT,
        new_value TEXT,
        changed_by VARCHAR(100) DEFAULT 'system',
        source_citation VARCHAR(500),
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_verification_history_species ON verification_history(species_id)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_name VARCHAR(255) NOT NULL,
        total_records INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        error_count INTEGER DEFAULT 0,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Dedicated L-number & LDA-number tables (Section 4)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS l_number_designations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        designation VARCHAR(50) NOT NULL UNIQUE,
        number_type VARCHAR(10) DEFAULT 'L',
        code_number INTEGER,
        scientific_name_current VARCHAR(255),
        identification_status VARCHAR(50) DEFAULT 'verified',
        genus_name VARCHAR(100),
        family_name VARCHAR(100) DEFAULT 'Loricariidae',
        subfamily_name VARCHAR(100) DEFAULT 'Ancistrinae',
        common_name_uz VARCHAR(255),
        common_name_en VARCHAR(255),
        common_name_ru VARCHAR(255),
        trade_names VARCHAR(500),
        alternative_numbers VARCHAR(255),
        river_basin VARCHAR(255),
        country VARCHAR(100),
        locality_detail TEXT,
        max_size_cm FLOAT,
        temp_min FLOAT,
        temp_max FLOAT,
        ph_min FLOAT,
        ph_max FLOAT,
        dietary_category VARCHAR(100),
        description TEXT,
        aquarium_care TEXT,
        source_reference VARCHAR(500),
        last_verified_date VARCHAR(20),
        is_ancistrus BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_lnum_desig ON l_number_designations(designation)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_lnum_sci ON l_number_designations(scientific_name_current)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_lnum_genus ON l_number_designations(genus_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_lnum_basin ON l_number_designations(river_basin)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_lnum_ancistrus ON l_number_designations(is_ancistrus)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lnumber_species (
        lnumber_id INTEGER NOT NULL REFERENCES l_number_designations(id) ON DELETE CASCADE,
        species_id INTEGER NOT NULL REFERENCES species(id) ON DELETE CASCADE,
        is_primary BOOLEAN DEFAULT 1,
        notes VARCHAR(255),
        PRIMARY KEY (lnumber_id, species_id)
    )
    """)

    conn.commit()
    conn.close()
    logger.info("Schema migration successfully completed!")

if __name__ == "__main__":
    run_migration()
