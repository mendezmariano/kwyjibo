CREATE DATABASE `kwyjibo`;
CREATE USER `kwyjibo`@`localhost` IDENTIFIED BY 'kwyjibo321';

GRANT ALL PRIVILEGES ON `kwyjibo`.* TO `kwyjibo`@`localhost`;
GRANT ALL PRIVILEGES ON `%_kwyjibo`.* TO `kwyjibo`@`localhost`;

