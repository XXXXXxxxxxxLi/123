#双表
CREATE TABLE DrugImages (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP,
    company_id INTEGER,
    staff VARCHAR(255),
    img TEXT,
    drug_name VARCHAR(255),
    is_activated BOOLEAN
);
CREATE TABLE DrugDetails (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP,
    company_id INTEGER,
    staff VARCHAR(255),
    drug_name VARCHAR(255),
    effect TEXT,
    indications TEXT,
    syndrome TEXT,
    is_verified BOOLEAN,
    verifier VARCHAR(255),
    is_activated BOOLEAN
);
CREATE VIEW CompanyDrugInfo AS
SELECT di.company_id, di.drug_name, dd.syndrome, di.img
FROM DrugImages di
JOIN DrugDetails dd ON di.drug_name = dd.drug_name AND di.company_id = dd.company_id;
#合并表
CREATE TABLE DrugInfo (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP,
    company_id INTEGER,
    staff VARCHAR(255),
    img TEXT,
    drug_name VARCHAR(255),
    is_activated BOOLEAN,
    effect TEXT,
    indications TEXT,
    syndrome TEXT[],
    is_verified BOOLEAN,
    verifier VARCHAR(255)
);
CREATE VIEW CompanyDrugInfo AS
SELECT company_id, drug_name, unnest(syndrome) AS syndrome, img
FROM DrugInfo;
