CREATE DATABASE smart_water;
USE smart_water;

-- 1) User configuration (only one row for now)
CREATE TABLE system_config (
  id INT PRIMARY KEY,
  users_count INT NOT NULL,
  green_limit_per_user FLOAT NOT NULL,
  orange_limit_per_user FLOAT NOT NULL
);

INSERT INTO system_config VALUES (1, 3, 70, 100);

-- 2) Tap master table
CREATE TABLE taps (
  tap_id INT AUTO_INCREMENT PRIMARY KEY,
  tap_name VARCHAR(50) NOT NULL
);

-- 3) Running usage table (reset daily)
CREATE TABLE tap_usage (
  tap_id INT,
  current_usage FLOAT DEFAULT 0,
  last_update DATETIME,
  PRIMARY KEY (tap_id),
  FOREIGN KEY (tap_id) REFERENCES taps(tap_id)
);

-- 4) Aggregate daily totals (per day, per tap)
CREATE TABLE tap_daily_archive (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tap_id INT,
  usage_liters FLOAT,
  archive_date DATE,
  FOREIGN KEY (tap_id) REFERENCES taps(tap_id)
);

-- 5) System-level daily aggregated totals
CREATE TABLE system_daily_totals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  total_usage FLOAT,
  color_status VARCHAR(10),
  usage_date DATE
);

use smart_water;
CREATE TABLE tap_usage_timeseries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tap_id INT,
  usage_liters DECIMAL(8,2),
  recorded_at DATETIME,
  FOREIGN KEY (tap_id) REFERENCES taps(tap_id)
);

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE tap_usage;
TRUNCATE TABLE tap_daily_archive;
TRUNCATE TABLE system_daily_totals;
TRUNCATE TABLE taps;

SET FOREIGN_KEY_CHECKS = 1;
