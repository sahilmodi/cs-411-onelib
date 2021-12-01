ALTER TABLE `onelib`.`User` ADD COLUMN `email` VARCHAR(256) NULL DEFAULT NULL AFTER `Password`;
UPDATE User 
SET email = LOWER(CONCAT(SUBSTRING_INDEX(Name, " ", 1), "_", SUBSTRING_INDEX(Name, " ", -1), "@gmail.com"))
