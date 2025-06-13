-- PostgreSQL Script
-- Wed Jun  5 13:15:51 2024

-- Schema
CREATE SCHEMA IF NOT EXISTS database_mapper_postgresql;

-- Set search path
SET search_path TO database_mapper_postgresql;

-- Variations Table
CREATE TABLE IF NOT EXISTS variations_table (
    id_variations_table BIGSERIAL PRIMARY KEY,
    not_null_col VARCHAR(10) NOT NULL,
    unique_col VARCHAR(20) UNIQUE,
    binary_col BYTEA,
    unsigned_col INTEGER,
    generated_col VARCHAR(40) GENERATED ALWAYS AS (not_null_col || '-' || unique_col) STORED,
    default_expression_bool_column BOOLEAN DEFAULT TRUE,
    not_null_unique_col VARCHAR(50) NOT NULL UNIQUE,
    not_null_binary_col BYTEA NOT NULL,
    not_null_unsigned_col INTEGER NOT NULL,
    not_null_auto_generated_col INTEGER GENERATED ALWAYS AS (not_null_unsigned_col + 1) STORED,
    not_null_unique_binary_col BYTEA NOT NULL UNIQUE,
    not_null_unique_unsigned_col INTEGER NOT NULL UNIQUE,
    not_null_unique_generated_col VARCHAR(80) GENERATED ALWAYS AS (UPPER(not_null_unique_col)) STORED,
    not_null_unique_binary_generated_col VARCHAR(90) GENERATED ALWAYS AS (LOWER(not_null_unique_binary_col::TEXT)) STORED,
    not_null_unique_binary_generated_default_value_col VARCHAR(100) DEFAULT 'DEFAULT',
    unique_binary_col BYTEA UNIQUE,
    unique_unsigned_col INTEGER UNIQUE,
    unique_generated_col VARCHAR(400) GENERATED ALWAYS AS (REVERSE(unique_col)) STORED,
    binary_generated_col VARCHAR(500) GENERATED ALWAYS AS (unique_binary_col::TEXT) STORED,
    datetime_default_value TIMESTAMP DEFAULT '1970-01-01 00:00:00'
);

-- String Table
CREATE TABLE IF NOT EXISTS string_table (
    id_string_table UUID PRIMARY KEY,
    char_col CHAR(36) UNIQUE,
    varchar_col VARCHAR(100) UNIQUE,
    binary_col BYTEA UNIQUE,
    varbinary_col BYTEA UNIQUE,
    blob_col BYTEA UNIQUE,
    text_col TEXT UNIQUE,
    enum_col TEXT CHECK (enum_col IN ('enum1', 'enum2')) UNIQUE,
    set_col TEXT UNIQUE,
    variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table)
);

-- Numeric Table
CREATE TABLE IF NOT EXISTS numeric_table (
    id_numeric_table BIGINT PRIMARY KEY,
    int_col INTEGER,
    mediumint_col INTEGER,
    smallint_col SMALLINT,
    tinyint_col SMALLINT,
    bool_col BOOLEAN,
    decimal_col DECIMAL,
    decimal_variable_col DECIMAL(13,2),
    float_col REAL,
    float_variable_col REAL,
    real_col REAL,
    double_col REAL,
    numeric_col NUMERIC,
    bit_col BIT,
    variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table)
);

-- Date and Time Table
CREATE TABLE IF NOT EXISTS date_and_time_table (
    id_date_and_time_table UUID PRIMARY KEY,
    date_col DATE,
    time_col TIME,
    datetime_col TIMESTAMP,
    timestamp_col TIMESTAMP,
    year_col INTEGER,
    variations_table_id BIGINT REFERENCES variations_table(id_variations_table),
    numeric_table_id BIGINT NOT NULL REFERENCES numeric_table(id_numeric_table)
);

-- Spatial Table
CREATE TABLE IF NOT EXISTS spatial_table (
    id_spatial_table UUID PRIMARY KEY,
    linestring GEOMETRY(LINESTRING) NOT NULL,
    geometry GEOMETRY NOT NULL,
    geometrycollection GEOMETRY(GEOMETRYCOLLECTION) NOT NULL,
    point GEOMETRY(POINT) NOT NULL,
    polygon GEOMETRY(POLYGON) NOT NULL,
    multipoint GEOMETRY(MULTIPOINT) NOT NULL,
    multipolygon GEOMETRY(MULTIPOLYGON) NOT NULL,
    multilinestring GEOMETRY(MULTILINESTRING) NOT NULL,
    variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table)
);

-- JSON Table
CREATE TABLE IF NOT EXISTS json_table (
    id_json_table UUID PRIMARY KEY,
    json_not_nullable_col JSONB NOT NULL,
    json_unique_col JSONB UNIQUE,
    json_not_nullable_unique_col JSONB NOT NULL UNIQUE,
    json_generated_column JSONB GENERATED ALWAYS AS (jsonb_build_object('key', json_not_nullable_col->'key')) STORED,
    json_not_nullable_generated_col JSONB GENERATED ALWAYS AS (jsonb_set(json_not_nullable_unique_col, '{new_value}', '"new_value"')) STORED,
    json_unique_generated_col JSONB GENERATED ALWAYS AS (jsonb_set(json_unique_col, '{new_key}', '"new_value"')) STORED,
    json_not_nullable_unique_col_index TEXT GENERATED ALWAYS AS ((json_not_nullable_unique_col->'address'->>'city')) STORED,
    json_unique_generated_col_index TEXT GENERATED ALWAYS AS ((json_unique_generated_col->>'specific_path')) STORED,
    variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table),
    string_table_id UUID REFERENCES string_table(id_string_table),
    spatial_table_id UUID NOT NULL REFERENCES spatial_table(id_spatial_table)
);

-- No ID Table
CREATE TABLE IF NOT EXISTS no_id_table (
    name VARCHAR(100),
    gender VARCHAR(20)
);