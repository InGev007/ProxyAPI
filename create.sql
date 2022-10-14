-- --------------------------------------------------------
-- Хост:                         ingibd-db00005966.mdb0002659.db.skysql.net
-- Версия сервера:               10.6.4-1-MariaDB-enterprise-log - MariaDB Enterprise Server
-- Операционная система:         Linux
-- HeidiSQL Версия:              11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Дамп структуры базы данных proxy
CREATE DATABASE IF NOT EXISTS `proxy` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `proxy`;

-- Дамп структуры для таблица proxy.proxy
CREATE TABLE IF NOT EXISTS `proxy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(255) NOT NULL DEFAULT '',
  `port` int(11) NOT NULL,
  `proverki` int(11) DEFAULT 0,
  `status` int(1) DEFAULT 0,
  `type` varchar(255) DEFAULT NULL,
  `time` float DEFAULT NULL,
  `anonymity` varchar(255) DEFAULT NULL,
  `country_code` varchar(255) DEFAULT NULL,
  `error` int(1) DEFAULT 0,
  `del` int(1) DEFAULT 0,
  `unique` varchar(50) DEFAULT NULL,
  UNIQUE KEY `ip` (`ip`,`port`),
  KEY `key` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=91882 DEFAULT CHARSET=utf8mb4;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица proxy.proxycheckers
CREATE TABLE IF NOT EXISTS `proxycheckers` (
  `ip` varchar(50) NOT NULL,
  `unique` varchar(50) NOT NULL,
  `pass` varchar(50) NOT NULL,
  `lastupdate` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  UNIQUE KEY `Key` (`unique`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Экспортируемые данные не выделены.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
