-- Turn off foreign key and unique checks
SET session_replication_role = replica;

-- Schema database_mapper_postgresql
CREATE SCHEMA IF NOT EXISTS database_mapper_postgresql;
-- Enable PostGIS extension to use spatial types
CREATE extension IF NOT EXISTS postgis;

UPDATE pg_extension 
  SET extrelocatable = TRUE 
    WHERE extname = 'postgis';

ALTER EXTENSION postgis 
  SET SCHEMA database_mapper_postgresql;

SET search_path TO database_mapper_postgresql;

-- Table `database_mapper_postgresql`.`variations_table`
CREATE TABLE IF NOT EXISTS variations_table (
  id_variations_table BIGSERIAL PRIMARY KEY,

  -- Generated columns
  generated_binary_col BYTEA GENERATED ALWAYS AS (unique_binary_col) STORED,
  generated_col VARCHAR(60) GENERATED ALWAYS AS (notnull_varchar_col || '-' || notnull_unique_col) STORED,
  generated_notnull_auto_col INT GENERATED ALWAYS AS (notnull_unsigned_col + 1) STORED,
  generated_notnull_unique_binary_col VARCHAR(90) GENERATED ALWAYS AS (LOWER(ENCODE(notnull_unique_binary_col, 'hex'))) STORED UNIQUE,
  generated_notnull_unique_col VARCHAR(80) GENERATED ALWAYS AS (UPPER(notnull_unique_col)) STORED UNIQUE,
  generated_unique_col VARCHAR(400) GENERATED ALWAYS AS (REVERSE(unique_col)) STORED UNIQUE,
  
  -- Not Null columns
  notnull_binary_col BYTEA NOT NULL,
  notnull_unique_binary_col BYTEA NOT NULL UNIQUE,
  notnull_unique_col VARCHAR(50) NOT NULL UNIQUE,
  notnull_unsigned_col INT NOT NULL CHECK (notnull_unsigned_col >= 0),
  notnull_unique_unsigned_col INT NOT NULL UNIQUE CHECK (notnull_unique_unsigned_col >= 0),
  notnull_varchar_col VARCHAR(10) NOT NULL,

  -- Unique columns
  unique_binary_col BYTEA UNIQUE,
  unique_col VARCHAR(20) UNIQUE,
  unique_unsigned_col INT UNIQUE CHECK (unique_unsigned_col >= 0),

  -- Default columns
  default_value_varchar_column VARCHAR(100) DEFAULT 'DEFAULT',
  default_value_bool_column BOOLEAN DEFAULT TRUE,
  default_value_datetime_column TIMESTAMP DEFAULT '1970-01-01 00:00:00',

  -- Other columns in alphabetical order
  binary_col BYTEA,
  unsigned_col INT CHECK (unsigned_col >= 0)
);

CREATE TABLE IF NOT EXISTS xml_table (
    id SERIAL PRIMARY KEY,
    xml_data XML
);

INSERT INTO xml_table (xml_data)
VALUES ('<bookstore>
            <book category="cooking">
                <title lang="en">Everyday Italian</title>
                <author>Giada De Laurentiis</author>
                <year>2005</year>
                <price>30.00</price>
            </book>
            <book category="children">
                <title lang="en">Harry Potter</title>
                <author>J.K. Rowling</author>
                <year>2005</year>
                <price>29.99</price>
            </book>
        </bookstore>');

-- Table `database_mapper_postgresql`.`string_table`
CREATE TABLE IF NOT EXISTS string_table (
  id_string_table UUID PRIMARY KEY,
  char_col CHAR(36) UNIQUE,
  varchar_col VARCHAR(100) UNIQUE,
  binary_col BYTEA UNIQUE,
  varbinary_col BYTEA,
  blob_col BYTEA UNIQUE,
  text_col TEXT UNIQUE,
  default_value_bpchar_col BPCHAR(20) DEFAULT 'bpchar_default',
  enum_col VARCHAR(20) CHECK (enum_col IN ('enum1', 'enum2')) UNIQUE,
  set_col TEXT UNIQUE,
  variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table)
);

-- Table `database_mapper_postgresql`.`numeric_table`
CREATE TABLE IF NOT EXISTS numeric_table (
  id_numeric_table BIGINT PRIMARY KEY,
  int_col INT CHECK (int_col >= 0),
  mediumint_col INT CHECK (mediumint_col >= -8388608 AND mediumint_col <= 8388607),
  smallint_col SMALLINT,
  tinyint_col SMALLINT CHECK (tinyint_col >= 0),
  bool_col BOOLEAN,
  decimal_col DECIMAL,
  decimal_variable_col DECIMAL(13,2) CHECK (decimal_variable_col >= 0),
  float_col REAL CHECK (float_col >= 0),
  float_variable_col REAL,
  real_col REAL CHECK (real_col >= 0),
  double_col DOUBLE PRECISION CHECK (double_col >= 0),
  numeric_col NUMERIC,
  bit_col BIT,
  bit_bool_col BIT(1),
  amount MONEY NOT NULL,
  default_value_int_col INT DEFAULT 42,
  default_value_real_col REAL DEFAULT 3.14,
  default_value_double_col DOUBLE PRECISION DEFAULT 1.618,
  default_value_decimal_col DECIMAL(10, 2) DEFAULT 99.99,
  variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table)
);

CREATE TABLE IF NOT EXISTS return_of_numeric_table (
    id_smallserial SMALLSERIAL PRIMARY KEY,
    default_value_serial SERIAL,
    default_value_bigserial BIGSERIAL,
    default_value_oid_column OID DEFAULT 0::oid,
    default_value_int4range_column INT4RANGE DEFAULT int4range(1, 10),
    default_value_int8range_column INT8RANGE DEFAULT int8range(1, 100),
    default_value_numrange_column NUMRANGE DEFAULT numrange(1.0, 100.0)
);

-- Insert data into the table to show defaults
INSERT INTO return_of_numeric_table DEFAULT VALUES;

-- Insert data specifying some values and relying on defaults for others
INSERT INTO return_of_numeric_table (default_value_oid_column) VALUES (12345::oid);

CREATE TABLE IF NOT EXISTS network_address_table (
    id SERIAL PRIMARY KEY,
    inet_address INET NOT NULL,
    cidr_address CIDR NOT NULL,
    mac_address MACADDR NOT NULL,
    mac_address8 MACADDR8 NOT NULL
);

-- Insert example data into the table
INSERT INTO network_address_table (inet_address, cidr_address, mac_address, mac_address8)
VALUES
('192.168.1.1', '192.168.1.0/24', '08:00:2b:01:02:03', '08:00:2b:01:02:03:04:05');

-- Insert more example data
INSERT INTO network_address_table (inet_address, cidr_address, mac_address, mac_address8)
VALUES
('2001:db8::ff00:42:8329', '2001:db8::/48', '08:00:2b:04:05:06', '08:00:2b:04:05:06:07:08');

CREATE TABLE IF NOT EXISTS full_text_search_table (
    id SERIAL PRIMARY KEY,
    document_text TEXT,
    document_vector TSVECTOR,
    search_query TSQUERY
);

INSERT INTO full_text_search_table (document_text, document_vector, search_query)
VALUES (
    'This is a sample document for full-text search.',  -- Example document text
    to_tsvector('english', 'This is a sample document for full-text search.'),  -- Example document vector
    plainto_tsquery('english', 'search')  -- Example search query
);

-- Table `database_mapper_postgresql`.`date_and_time_table`
CREATE TABLE IF NOT EXISTS date_and_time_table (
  id_date_and_time_table UUID PRIMARY KEY,
  default_value_timestamp_no_tz TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  default_value_timestamp_with_tz TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  default_value_date_col DATE DEFAULT CURRENT_DATE,
  default_value_time_no_tz TIME DEFAULT CURRENT_TIME,
  default_value_time_with_tz TIMETZ DEFAULT CURRENT_TIME,
  default_value_interval_col INTERVAL DEFAULT INTERVAL '1 day',
  date_col DATE,
  time_col TIME,
  datetime_col TIMESTAMP,
  timestamp_col TIMESTAMP,
  year_col INT CHECK (year_col BETWEEN 1901 AND 2155),
  variations_table_id BIGINT REFERENCES variations_table(id_variations_table),
  numeric_table_id BIGINT NOT NULL REFERENCES numeric_table(id_numeric_table),
  tsrange_col TSRANGE,
  tstzrange_col TSTZRANGE,
  daterange_col DATERANGE
);

-- Insert example data with the additional range types
INSERT INTO date_and_time_table (
    id_date_and_time_table,
    default_value_timestamp_no_tz,
    default_value_timestamp_with_tz,
    default_value_date_col,
    default_value_time_no_tz,
    default_value_time_with_tz,
    default_value_interval_col,
    date_col,
    time_col,
    datetime_col,
    timestamp_col,
    year_col,
    variations_table_id,
    numeric_table_id,
    tsrange_col,
    tstzrange_col,
    daterange_col
) VALUES (
    gen_random_uuid(),  -- Generate a random UUID
    '2024-06-12 14:30:00',  -- Specific timestamp without time zone
    '2024-06-12 14:30:00+00',  -- Specific timestamp with time zone
    '2024-06-12',  -- Specific date
    '14:30:00',  -- Specific time without time zone
    '14:30:00+00',  -- Specific time with time zone
    '2 days',  -- Specific interval
    '2024-06-12',  -- Specific date
    '14:30:00',  -- Specific time
    '2024-06-12 14:30:00',  -- Specific datetime
    '2024-06-12 14:30:00',  -- Specific timestamp
    2024,  -- Specific year
    1,  -- Example variations_table_id
    1,   -- Example numeric_table_id
    '[2024-06-12, 2024-06-15)',  -- Example tsrange
    '[2024-06-12 12:00:00+00, 2024-06-15 12:00:00+00)',  -- Example tstzrange
    '[2024-06-12, 2024-06-15)'  -- Example daterange
);

-- Table `database_mapper_postgresql`.`spatial_table`
CREATE TABLE IF NOT EXISTS spatial_table (
  id_spatial_table UUID PRIMARY KEY,
  linestring GEOMETRY(LINESTRING, 4326) NOT NULL,
  geometry GEOMETRY NOT NULL,
  geometrycollection GEOMETRY(GEOMETRYCOLLECTION, 4326) NOT NULL,
  point GEOMETRY(POINT, 4326) NOT NULL,
  polygon GEOMETRY(POLYGON, 4326) NOT NULL,
  multipoint GEOMETRY(MULTIPOINT, 4326) NOT NULL,
  multipolygon GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
  multilinestring GEOMETRY(MULTILINESTRING, 4326) NOT NULL,
  variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table)
);

-- Insert data into spatial_table
INSERT INTO spatial_table (
    id_spatial_table,
    linestring,
    geometry,
    geometrycollection,
    point,
    polygon,
    multipoint,
    multipolygon,
    multilinestring,
    variations_table_id
) VALUES (
    'b1aeb8e1-9f1b-4c4c-b04a-809e1c81ff9d',  -- UUID
    ST_GeomFromText('LINESTRING(0 0, 1 1, 2 2)', 4326),  -- LINESTRING
    ST_GeomFromText('POINT(0 0)', 4326),  -- GEOMETRY
    ST_Collect(
        ST_GeomFromText('POINT(0 0)', 4326), 
        ST_GeomFromText('LINESTRING(1 1, 2 2)', 4326)
    ),  -- GEOMETRYCOLLECTION
    ST_GeomFromText('POINT(1 1)', 4326),  -- POINT
    ST_GeomFromText('POLYGON((0 0, 1 1, 1 0, 0 0))', 4326),  -- POLYGON
    ST_GeomFromText('MULTIPOINT((0 0), (1 1), (2 2))', 4326),  -- MULTIPOINT
    ST_GeomFromText('MULTIPOLYGON(((0 0, 1 1, 1 0, 0 0)))', 4326),  -- MULTIPOLYGON
    ST_GeomFromText('MULTILINESTRING((0 0, 1 1, 2 2))', 4326),  -- MULTILINESTRING
    0  -- variations_table_id
);

CREATE TABLE pg_types_table (
    id SERIAL PRIMARY KEY,
    lsn_col PG_LSN,
    snapshot_col PG_SNAPSHOT
);

-- Create a restore point
SELECT pg_create_restore_point('test_restore_point');

-- Insert into the main table using the restore point
INSERT INTO pg_types_table (lsn_col, snapshot_col)
VALUES (
    pg_current_wal_lsn(), 
    (SELECT pg_current_snapshot())
);

CREATE TABLE IF NOT EXISTS native_geometric_table (
    id SERIAL PRIMARY KEY,
    point_col POINT,
    line_col LINE,
    lseg_col LSEG,
    box_col BOX,
    path_col PATH,
    polygon_col POLYGON,
    circle_col CIRCLE
);

INSERT INTO native_geometric_table (
    point_col, line_col, lseg_col, box_col, path_col, polygon_col, circle_col
) VALUES (
    '(1,1)',          -- Example point
    '((0,0),(1,1))',  -- Example line
    '((0,0),(1,1))',  -- Example line segment
    '((0,0),(1,1))',  -- Example box
    '[(0,0),(1,1),(1,0)]', -- Example open path
    '((0,0),(1,1),(1,0))', -- Example polygon
    '<(0,0),1>'       -- Example circle
);

-- Enum type
CREATE TYPE mood AS ENUM ('happy', 'sad', 'neutral');

-- Composite type 
CREATE TYPE address_type AS (
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20)
);

-- Domain types
CREATE DOMAIN positive_integer AS INTEGER CHECK (VALUE >= 0);
CREATE DOMAIN email_address AS VARCHAR(255) CHECK (VALUE ~* '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');

CREATE TABLE IF NOT EXISTS user_defined_types_table (
    id SERIAL PRIMARY KEY,
    mood_col mood NOT NULL DEFAULT 'neutral', -- Column using enum type mood
    address_col address_type, -- Column using composite type address_type
    age positive_integer, -- Column using domain type positive_integer
    email email_address -- Column using domain type email_address
);

-- Insert example data with different enum values and addresses
INSERT INTO user_defined_types_table (mood_col, address_col, age, email) 
VALUES 
    ('happy', ROW('123 Main St', 'Anytown', 'CA', '12345')::address_type, 25, 'john@example.com'),
    ('sad', ROW('456 Elm St', 'Othertown', 'NY', '54321')::address_type, 30, 'jane@example.com'),
    ('neutral', ROW('789 Oak St', 'Anothertown', 'TX', '67890')::address_type, 28, 'bill@example.com');

-- Insert data using the default value
INSERT INTO user_defined_types_table DEFAULT VALUES;

-- Create the necessary objects for object_identifier_types table
CREATE TABLE IF NOT EXISTS one_column_table (id SERIAL PRIMARY KEY);
CREATE TEXT SEARCH CONFIGURATION english (COPY = pg_catalog.english);
CREATE TEXT SEARCH DICTIONARY my_dict (
    TEMPLATE = simple,
    STOPWORDS = english
);
CREATE FUNCTION my_function() RETURNS void LANGUAGE plpgsql AS $$ BEGIN RETURN; END $$;
CREATE FUNCTION my_stored_proc() RETURNS void LANGUAGE plpgsql AS $$ BEGIN RETURN; END $$;
CREATE TYPE my_custom_type AS (field1 INT, field2 TEXT);
CREATE ROLE admin;


CREATE TABLE IF NOT EXISTS object_identifier_types (
    oid OID,
    regclass REGCLASS,
    regcollation REGCOLLATION,
    regconfig REGCONFIG,
    regdictionary REGDICTIONARY,
    regnamespace REGNAMESPACE,
    regoper REGOPER,
    regoperator REGOPERATOR,
    regproc REGPROC,
    regprocedure REGPROCEDURE,
    regrole REGROLE,
    regtype REGTYPE
);

CREATE TABLE IF NOT EXISTS array_table (
    id SERIAL PRIMARY KEY,
    int_array INTEGER[],
    text_array TEXT[],
    varchar_array VARCHAR(255)[],
    double_precision_array DOUBLE PRECISION[],
    boolean_array BOOLEAN[],
    date_array DATE[],
    timestamp_array TIMESTAMP[],
    int4range_array INT4RANGE[],
    int8range_array INT8RANGE[],
    numrange_array NUMRANGE[],
    tsrange_array TSRANGE[],
    tstzrange_array TSTZRANGE[],
    daterange_array DATERANGE[],
    box_array BOX[],
    circle_array CIRCLE[],
    path_array PATH[],
    polygon_array POLYGON[],
    line_array LINE[],
    lseg_array LSEG[],
    macaddr_array MACADDR[],
    macaddr8_array MACADDR8[],
    inet_array INET[],
    cidr_array CIDR[],
    xml_array XML[],
    tsvector_array TSVECTOR[],
    tsquery_array TSQUERY[],
    json_array JSON[],
    jsonb_array JSONB[],
    point_array POINT[],
    varbit_array VARBIT[],
    bit_array BIT[]
);

-- Create the json_table with triggers for generated columns
CREATE TABLE IF NOT EXISTS json_table (
  id_json_table UUID PRIMARY KEY,
  jsonb_not_nullable_col JSONB NOT NULL,
  json_not_nullable_col JSON NOT NULL,
  json_not_nullable_unique_col JSONB NOT NULL,
  default_value_json_generated_column JSONB DEFAULT '{"default_key": "default_value", "status": "new"}'::jsonb,
  json_not_nullable_generated_col JSONB,
  json_unique_generated_col JSONB,
  json_not_nullable_unique_col_index VARCHAR(191) UNIQUE,
  json_unique_generated_col_index VARCHAR(191) UNIQUE,
  variations_table_id BIGINT NOT NULL REFERENCES variations_table(id_variations_table),
  string_table_id UUID REFERENCES string_table(id_string_table),
  spatial_table_id UUID NOT NULL REFERENCES spatial_table(id_spatial_table)
);

-- Table `database_mapper_postgresql`.`no_id_table`
CREATE TABLE IF NOT EXISTS no_id_table (
  name VARCHAR(100),
  gender VARCHAR(20)
);

-- Restore foreign key and unique checks
SET session_replication_role = DEFAULT;
