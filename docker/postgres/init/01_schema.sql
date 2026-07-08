-- ============================================================
-- Base de datos: parking
-- Motor: PostgreSQL
-- Inicializacion idempotente para parking-back.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS uce;

CREATE OR REPLACE FUNCTION set_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified_date = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS public.users (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username           VARCHAR(50)  NOT NULL UNIQUE,
    password_hash      VARCHAR(255) NOT NULL,
    full_name          VARCHAR(150),
    email              VARCHAR(150) UNIQUE,
    role               VARCHAR(30)  NOT NULL DEFAULT 'operador',
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    must_change_password BOOLEAN    NOT NULL DEFAULT TRUE,
    created_date       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    last_modified_date TIMESTAMPTZ  NOT NULL DEFAULT now()
);

ALTER TABLE public.users ADD COLUMN IF NOT EXISTS full_name VARCHAR(150);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS email VARCHAR(150) UNIQUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS role VARCHAR(30) NOT NULL DEFAULT 'operador';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS created_date TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_modified_date TIMESTAMPTZ NOT NULL DEFAULT now();

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_users_modified') THEN
        CREATE TRIGGER trg_users_modified
            BEFORE UPDATE ON public.users
            FOR EACH ROW EXECUTE FUNCTION set_last_modified();
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS uce.core_persons (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dni                    VARCHAR(20) NOT NULL UNIQUE,
    dni_type               VARCHAR(20) NOT NULL DEFAULT 'CEDULA',
    name                   VARCHAR(150),
    first_names            VARCHAR(150),
    last_names             VARCHAR(150),
    phone                  VARCHAR(20),
    secondary_phone        VARCHAR(20),
    email                  VARCHAR(150) UNIQUE,
    fingerprint_code       VARCHAR(20),
    embedding_face         DOUBLE PRECISION[],
    password_hash          VARCHAR(255),
    must_change_password   BOOLEAN NOT NULL DEFAULT TRUE,
    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
    person_type            VARCHAR(30),
    registration_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_date           TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_modified_date     TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS dni_type VARCHAR(20) NOT NULL DEFAULT 'CEDULA';
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS name VARCHAR(150);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS first_names VARCHAR(150);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS last_names VARCHAR(150);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS secondary_phone VARCHAR(20);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS email VARCHAR(150) UNIQUE;
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS fingerprint_code VARCHAR(20);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS embedding_face DOUBLE PRECISION[];
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS person_type VARCHAR(30);
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS registration_completed BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS created_date TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE uce.core_persons ADD COLUMN IF NOT EXISTS last_modified_date TIMESTAMPTZ NOT NULL DEFAULT now();

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'core_persons_dni_type_check') THEN
        ALTER TABLE uce.core_persons
        ADD CONSTRAINT core_persons_dni_type_check
        CHECK (dni_type IN ('CEDULA', 'PASAPORTE', 'RUC'));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_persons_modified') THEN
        CREATE TRIGGER trg_persons_modified
            BEFORE UPDATE ON uce.core_persons
            FOR EACH ROW EXECUTE FUNCTION set_last_modified();
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS uce.core_vehicles (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plate              VARCHAR(10) NOT NULL UNIQUE,
    last_plate         VARCHAR(10),
    brand              VARCHAR(50),
    vehicle_class      VARCHAR(50),
    type               VARCHAR(50),
    manufacture_year   SMALLINT,
    model              VARCHAR(50),
    engine             VARCHAR(50),
    primary_color      VARCHAR(30),
    secondary_color    VARCHAR(30),
    chassis            VARCHAR(50),
    created_date       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_modified_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by         UUID REFERENCES public.users(id),
    last_modified_by   UUID REFERENCES public.users(id)
);

ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS last_plate VARCHAR(10);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS brand VARCHAR(50);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS vehicle_class VARCHAR(50);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS type VARCHAR(50);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS manufacture_year SMALLINT;
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS model VARCHAR(50);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS engine VARCHAR(50);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS primary_color VARCHAR(30);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(30);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS chassis VARCHAR(50);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS created_date TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS last_modified_date TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES public.users(id);
ALTER TABLE uce.core_vehicles ADD COLUMN IF NOT EXISTS last_modified_by UUID REFERENCES public.users(id);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_vehicles_modified') THEN
        CREATE TRIGGER trg_vehicles_modified
            BEFORE UPDATE ON uce.core_vehicles
            FOR EACH ROW EXECUTE FUNCTION set_last_modified();
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS uce.vehicle_persons (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id   UUID NOT NULL REFERENCES uce.core_vehicles(id) ON DELETE CASCADE,
    person_id    UUID NOT NULL REFERENCES uce.core_persons(id),
    relation     VARCHAR(20) NOT NULL DEFAULT 'AUTORIZADO',
    created_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (vehicle_id, person_id)
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vehicle_persons_relation_check') THEN
        ALTER TABLE uce.vehicle_persons
        ADD CONSTRAINT vehicle_persons_relation_check
        CHECK (relation IN ('DUENO', 'AUTORIZADO'));
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS uce.gates (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(50),
    address          VARCHAR(200),
    number           INTEGER,
    main_street      VARCHAR(150),
    secondary_street VARCHAR(150),
    reference        VARCHAR(200),
    mqtt_topic       VARCHAR(200)
);

ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS name VARCHAR(50);
ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS address VARCHAR(200);
ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS number INTEGER;
ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS main_street VARCHAR(150);
ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS secondary_street VARCHAR(150);
ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS reference VARCHAR(200);
ALTER TABLE uce.gates ADD COLUMN IF NOT EXISTS mqtt_topic VARCHAR(200);

CREATE TABLE IF NOT EXISTS uce.access_logs (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id      UUID NOT NULL REFERENCES uce.core_persons(id),
    vehicle_id     UUID NOT NULL REFERENCES uce.core_vehicles(id),
    entry_gate_id  UUID REFERENCES uce.gates(id),
    exit_gate_id   UUID REFERENCES uce.gates(id),
    entry_datetime TIMESTAMPTZ,
    exit_datetime  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS uce.payments (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id     UUID NOT NULL REFERENCES uce.core_persons(id),
    amount        NUMERIC(10,2) NOT NULL,
    payment_date  DATE NOT NULL DEFAULT current_date,
    valid_from    DATE NOT NULL,
    valid_until   DATE NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'VALIDADO',
    receipt_path  VARCHAR(255),
    validated_by  UUID REFERENCES public.users(id),
    created_date  TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS payment_date DATE NOT NULL DEFAULT current_date;
ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS valid_from DATE;
ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS valid_until DATE;
ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'VALIDADO';
ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS receipt_path VARCHAR(255);
ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS validated_by UUID REFERENCES public.users(id);
ALTER TABLE uce.payments ADD COLUMN IF NOT EXISTS created_date TIMESTAMPTZ NOT NULL DEFAULT now();

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'payments_status_check') THEN
        ALTER TABLE uce.payments
        ADD CONSTRAINT payments_status_check
        CHECK (status IN ('PENDIENTE', 'VALIDADO', 'ANULADO'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_payments_person ON uce.payments(person_id);
CREATE INDEX IF NOT EXISTS idx_payments_valid  ON uce.payments(valid_until);
CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON uce.core_vehicles(plate);
CREATE INDEX IF NOT EXISTS idx_vp_vehicle     ON uce.vehicle_persons(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vp_person      ON uce.vehicle_persons(person_id);
CREATE INDEX IF NOT EXISTS idx_logs_person    ON uce.access_logs(person_id);
CREATE INDEX IF NOT EXISTS idx_logs_vehicle   ON uce.access_logs(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_logs_entry     ON uce.access_logs(entry_datetime);
