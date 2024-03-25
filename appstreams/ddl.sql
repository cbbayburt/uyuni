-- List of modules in a channel
CREATE TABLE IF NOT EXISTS suseAppstream(
	id	NUMERIC NOT NULL
			CONSTRAINT suse_as_module_id_pk PRIMARY KEY,
	channel_id NUMERIC NOT NULL
			REFERENCES rhnChannel(id)
			ON DELETE CASCADE,
	name	VARCHAR(128) NOT NULL,
	stream	VARCHAR(128) NOT NULL,
	version VARCHAR(128) NOT NULL,
	context	VARCHAR(16) NOT NULL,
	arch	VARCHAR(16) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_uq_as_module_nsvca
ON suseAppstream(name, stream, version, context, arch);

CREATE SEQUENCE IF NOT EXISTS suse_as_module_seq;

-- Which packages are included in a module
CREATE TABLE IF NOT EXISTS suseAppstreamPackage(
	package_id	NUMERIC NOT NULL
				REFERENCES rhnPackage(id)
				ON DELETE CASCADE,
	module_id	NUMERIC NOT NULL
				REFERENCES suseAppstream(id)
				ON DELETE CASCADE,
        CONSTRAINT uq_as_pkg_module UNIQUE (package_id, module_id)
);

-- Which APIs does the module provide
CREATE TABLE IF NOT EXISTS suseAppstreamApi(
	module_id	NUMERIC NOT NULL
				REFERENCES suseAppstream(id)
				ON DELETE CASCADE,
        rpm             VARCHAR(128) NOT NULL
);

-- Which modules are enabled on a server
CREATE TABLE IF NOT EXISTS suseServerAppstream(
	id	NUMERIC NOT NULL
			CONSTRAINT suse_as_servermodule_id_pk PRIMARY KEY,
	server_id NUMERIC NOT NULL
			REFERENCES rhnServer(id)
			ON DELETE CASCADE,
	name	VARCHAR(128) NOT NULL,
	stream	VARCHAR(128) NOT NULL,
	version VARCHAR(128) NOT NULL,
	context	VARCHAR(16) NOT NULL,
	arch	VARCHAR(16) NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS suse_as_servermodule_seq;

CREATE OR REPLACE VIEW modulePackage AS
SELECT
    m.name,
    m.stream,
    m.version,
    pn.name as pkg_name,
    pe.evr
FROM
    suseAppstream m
    JOIN suseAppstreamPackage mp ON m.id = mp.module_id
    JOIN rhnPackage p on mp.package_id = p.id
    JOIN rhnPackageName pn ON p.name_id = pn.id
    JOIN rhnPackageEvr pe ON p.evr_id = pe.id
ORDER BY m.name, m.stream, m.version;

CREATE OR REPLACE VIEW serverModularPackages AS
SELECT
    c.id AS channel_id,
    c.label AS channel_label,
    m.id AS module_id,
    m.name,
    m.stream,
    m.version,
    m.context,
    m.arch,
    CONCAT(rpn.name, '-', COALESCE(rpe.epoch || ':', rpe.epoch), rpe.version, '-', rpe.release) AS package,
    s.server_id
FROM suseAppstream m
JOIN suseAppstreamPackage p ON p.module_id = m.id
JOIN rhnchannel c ON m.channel_id = c.id
JOIN rhnpackage rp ON rp.id = p.package_id
JOIN rhnpackageevr rpe ON rpe.id = rp.evr_id
JOIN rhnpackagename rpn ON rpn.id = rp.name_id
LEFT JOIN suseServerAppstream s
    ON  m.name = s.name
    AND m.stream = s.stream
    AND m.version = s.version
    AND m.context = s.context
    AND m.arch = s.arch
ORDER BY c.label, m.name, m.stream, m.version, m.context, m.arch, rpn.name;

CREATE OR REPLACE VIEW serverModularPackageIds AS
SELECT
    p.package_id,
    c.id AS channel_id,
    c.label AS channel_label,
    s.server_id
FROM suseAppstream m
JOIN suseAppstreamPackage p ON p.module_id = m.id
JOIN rhnchannel c ON m.channel_id = c.id
LEFT JOIN suseServerAppstream s
    ON  m.name = s.name
    AND m.stream = s.stream
    AND m.version = s.version
    AND m.context = s.context
    AND m.arch = s.arch;



-- MORE:
-- suseModuleApi
