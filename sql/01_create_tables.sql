-- =====================================================================
--  ИС «Автотранспортная компания» (вариант 15)
--  Скрипт 1: создание таблиц, ограничений и триггера
--  СУБД: PostgreSQL
-- =====================================================================

DROP TABLE IF EXISTS waybill_item  CASCADE;
DROP TABLE IF EXISTS waybill       CASCADE;
DROP TABLE IF EXISTS cargo         CASCADE;
DROP TABLE IF EXISTS staff         CASCADE;
DROP TABLE IF EXISTS vehicle       CASCADE;
DROP TABLE IF EXISTS client        CASCADE;
DROP TABLE IF EXISTS internal_user CASCADE;

-- Клиенты фирмы
CREATE TABLE client (
    contract_num     INTEGER       PRIMARY KEY,               -- уникальный номер договора
    client_name      VARCHAR(100)  NOT NULL,                  -- название
    address          VARCHAR(200)  NOT NULL,                  -- адрес
    inside_mkad      BOOLEAN       NOT NULL DEFAULT TRUE,     -- признак района: TRUE - в пределах МКАД
    contact_surname  VARCHAR(50)   NOT NULL,                  -- фамилия контактного лица
    contact_phone    VARCHAR(20)   NOT NULL,                  -- телефон контактного лица
    year_weight      NUMERIC(12,2) NOT NULL DEFAULT 0         -- вес грузов с начала года, кг (нарастающий итог)
                     CHECK (year_weight >= 0)
);

-- Автотранспорт фирмы
CREATE TABLE vehicle (
    vehicle_id    SERIAL        PRIMARY KEY,
    reg_number    VARCHAR(12)   NOT NULL UNIQUE,              -- регистрационный номер
    brand         VARCHAR(50)   NOT NULL,                     -- марка
    release_year  INTEGER       NOT NULL CHECK (release_year BETWEEN 1980 AND 2100), -- год выпуска
    capacity      NUMERIC(6,2)  NOT NULL CHECK (capacity > 0) -- грузоподъёмность, т
);

-- Персонал фирмы (в основном водители и экспедиторы)
CREATE TABLE staff (
    staff_id    SERIAL        PRIMARY KEY,
    surname     VARCHAR(50)   NOT NULL,                       -- фамилия
    address     VARCHAR(200)  NOT NULL,                       -- адрес
    birth_date  DATE          NOT NULL,                       -- дата рождения
    position    VARCHAR(50)   NOT NULL,                       -- должность
    hire_date   DATE          NOT NULL,                       -- дата зачисления на должность
    CHECK (hire_date > birth_date)
);

-- Справочник возможных грузов
CREATE TABLE cargo (
    cargo_id    SERIAL        PRIMARY KEY,
    cargo_name  VARCHAR(100)  NOT NULL UNIQUE,                -- название груза
    avg_weight  NUMERIC(8,2)  NOT NULL CHECK (avg_weight > 0) -- средний вес единицы, кг
);

-- Товарно-транспортная накладная
CREATE TABLE waybill (
    waybill_id     SERIAL        PRIMARY KEY,
    waybill_date   DATE          NOT NULL,                    -- дата перевозки
    vehicle_id     INTEGER       NOT NULL REFERENCES vehicle(vehicle_id),   -- транспорт
    forwarder_id   INTEGER       NOT NULL REFERENCES staff(staff_id),       -- экспедитор
    contract_num   INTEGER       NOT NULL REFERENCES client(contract_num),  -- клиент-отправитель
    total_weight   NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (total_weight >= 0) -- общий вес, кг
);

-- Список перевезённых грузов, прикладываемый к накладной
CREATE TABLE waybill_item (
    waybill_id  INTEGER  NOT NULL REFERENCES waybill(waybill_id) ON DELETE CASCADE,
    cargo_id    INTEGER  NOT NULL REFERENCES cargo(cargo_id),
    quantity    INTEGER  NOT NULL CHECK (quantity > 0),       -- количество
    PRIMARY KEY (waybill_id, cargo_id)
);

-- Внутренние пользователи информационной системы (ЛР2)
CREATE TABLE internal_user (
    user_id     SERIAL       PRIMARY KEY,
    login       VARCHAR(30)  NOT NULL UNIQUE,
    password    VARCHAR(64)  NOT NULL,
    user_group  VARCHAR(30)  NOT NULL,                         -- группа (роль) пользователя
    full_name   VARCHAR(100) NOT NULL
);

-- ---------------------------------------------------------------------
-- Триггер: общий вес грузов клиента с начала года хранится
-- нарастающим итогом. При добавлении / изменении / удалении накладной
-- текущего года вес автоматически пересчитывается.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_client_year_weight() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP IN ('UPDATE', 'DELETE')
       AND EXTRACT(YEAR FROM OLD.waybill_date) = EXTRACT(YEAR FROM CURRENT_DATE) THEN
        UPDATE client SET year_weight = year_weight - OLD.total_weight
         WHERE contract_num = OLD.contract_num;
    END IF;
    IF TG_OP IN ('INSERT', 'UPDATE')
       AND EXTRACT(YEAR FROM NEW.waybill_date) = EXTRACT(YEAR FROM CURRENT_DATE) THEN
        UPDATE client SET year_weight = year_weight + NEW.total_weight
         WHERE contract_num = NEW.contract_num;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_waybill_year_weight
AFTER INSERT OR UPDATE OR DELETE ON waybill
FOR EACH ROW EXECUTE FUNCTION update_client_year_weight();
