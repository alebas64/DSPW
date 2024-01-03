-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Creato il: Gen 02, 2024 alle 20:16
-- Versione del server: 10.4.32-MariaDB
-- Versione PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dsds`
--
CREATE DATABASE IF NOT EXISTS `dsds` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `dsds`;

-- --------------------------------------------------------

--
-- Struttura della tabella `citta`
--

CREATE TABLE `citta` (
  `id` int(11) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `latitudine` double NOT NULL,
  `longitudine` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dump dei dati per la tabella `citta`
--

INSERT INTO `citta` (`id`, `nome`, `latitudine`, `longitudine`) VALUES
(1, 'Roma', 41.9028, 43.7696);

-- --------------------------------------------------------

--
-- Struttura della tabella `constraints`
--

CREATE TABLE `constraints` (
  `id` int(11) NOT NULL,
  `valore` double DEFAULT NULL,
  `cod_legenda` int(11) NOT NULL,
  `cod_utente` int(11) NOT NULL,
  `cod_citta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `legenda`
--

CREATE TABLE `legenda` (
  `id` int(11) NOT NULL,
  `nome` text NOT NULL,
  `descrizione` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dump dei dati per la tabella `legenda`
--

INSERT INTO `legenda` (`id`, `nome`, `descrizione`) VALUES
(1, 'Temperatura massima', 'Se la temperatura registrata (in gradi celsius) è maggiore di una soglia'),
(2, 'Temperatura minima', 'Se la temperatura registrata (in gradi celsius) è minore di una soglia'),
(3, 'Temperatura massima', 'Valore di temperatura massima prevista (in gradi celsius)'),
(4, 'Temperatura minima', 'Valore di temperatura minima prevista (in gradi celsius)'),
(5, 'Umidità', 'Se l umidità registrata è minore di una soglia'),
(6, 'Quantità di pioggia', 'Se piove più di un valore di soglia (in mm/h)'),
(7, 'Presenza di neve', 'Restituirà \"si\" o \"no\" se ci sarà o meno neve'),
(8, 'Velocità del vento', 'Se la velocità del vento è superiore a un valore indicato'),
(9, 'testing', 'valore inserito da python per testing'),
(10, 'Percentuale di nuvolosita', 'Se il cielo è coperto per più di un valore di soglia'),
(11, 'Indice di raggi ultravioletti', 'Restituisce il valore di raggi ultravioletti'),
(12, 'Alba solare', 'Quando accadrà l alba solare'),
(13, 'Tramonto solare', 'Quando accadrà il tramonto solare'),
(14, 'Alba lunare', 'Quando accadrà l alba lunare'),
(15, 'Tramonto lunare', 'Quando accadrà il tramonto lunare'),
(16, 'testing', 'valore inserito da python per testing'),
(17, 'testing', 'valore inserito da python per testing'),
(18, 'testing', 'valore inserito da python per testing'),
(19, 'testing', 'valore inserito da python per testing');

-- --------------------------------------------------------

--
-- Struttura della tabella `utente`
--

CREATE TABLE `utente` (
  `id` int(11) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `cognome` varchar(255) NOT NULL,
  `telegram` varchar(128) NOT NULL,
  `id_chat` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `citta`
--
ALTER TABLE `citta`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `constraints`
--
ALTER TABLE `constraints`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cod_legenda` (`cod_legenda`),
  ADD KEY `cod_citta` (`cod_citta`),
  ADD KEY `cod_utente` (`cod_utente`);

--
-- Indici per le tabelle `legenda`
--
ALTER TABLE `legenda`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `utente`
--
ALTER TABLE `utente`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `telegram` (`telegram`),
  ADD UNIQUE KEY `id_chat` (`id_chat`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `citta`
--
ALTER TABLE `citta`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT per la tabella `constraints`
--
ALTER TABLE `constraints`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `legenda`
--
ALTER TABLE `legenda`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT per la tabella `utente`
--
ALTER TABLE `utente`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `constraints`
--
ALTER TABLE `constraints`
  ADD CONSTRAINT `constraints_ibfk_1` FOREIGN KEY (`cod_legenda`) REFERENCES `legenda` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `constraints_ibfk_3` FOREIGN KEY (`cod_citta`) REFERENCES `citta` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `constraints_ibfk_4` FOREIGN KEY (`cod_utente`) REFERENCES `utente` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `constraints_ibfk_5` FOREIGN KEY (`cod_utente`) REFERENCES `utente` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;


--
-- Metadati
--
USE `phpmyadmin`;

--
-- Metadati per tabella citta
--

--
-- Metadati per tabella constraints
--

--
-- Metadati per tabella legenda
--

--
-- Metadati per tabella utente
--

--
-- Metadati per database dsds
--

--
-- Dump dei dati per la tabella `pma__pdf_pages`
--

INSERT INTO `pma__pdf_pages` (`db_name`, `page_descr`) VALUES
('dsds', 'visualizzazione');

SET @LAST_PAGE = LAST_INSERT_ID();

--
-- Dump dei dati per la tabella `pma__table_coords`
--

INSERT INTO `pma__table_coords` (`db_name`, `table_name`, `pdf_page_number`, `x`, `y`) VALUES
('dsds', 'citta', @LAST_PAGE, 641, 364),
('dsds', 'constraints', @LAST_PAGE, 392, 253),
('dsds', 'legenda', @LAST_PAGE, 646, 212),
('dsds', 'utente', @LAST_PAGE, 173, 250);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
