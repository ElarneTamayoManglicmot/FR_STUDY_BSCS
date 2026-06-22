-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 12, 2026 at 02:19 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.5.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `thesis`
--

-- --------------------------------------------------------

--
-- Table structure for table `recognized_faces`
--

CREATE TABLE `recognized_faces` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `accuracy` decimal(5,2) DEFAULT NULL,
  `processing_speed` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `detected_by_face_recognition` tinyint(1) DEFAULT 0,
  `detected_by_dlib` tinyint(1) DEFAULT 0,
  `isRegister` tinyint(1) DEFAULT 0,
  `detected_resolution` varchar(10) DEFAULT NULL,
  `accuracy_1440p` decimal(5,2) DEFAULT NULL,
  `accuracy_1080p` decimal(5,2) DEFAULT NULL,
  `speed_1440p` decimal(10,2) DEFAULT NULL,
  `speed_1080p` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `recognized_faces`
--

INSERT INTO `recognized_faces` (`id`, `user_id`, `accuracy`, `processing_speed`, `created_at`, `detected_by_face_recognition`, `detected_by_dlib`, `isRegister`, `detected_resolution`, `accuracy_1440p`, `accuracy_1080p`, `speed_1440p`, `speed_1080p`) VALUES
(3, 1, 78.53, 3.01, '2026-01-30 16:28:11', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(4, 1, 82.00, 1.56, '2026-01-30 16:30:54', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(5, 1, 82.00, 1.55, '2026-01-30 16:30:54', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(6, 1, 71.00, 1.54, '2026-01-30 16:30:58', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(7, 1, 71.00, 1.54, '2026-01-30 16:30:58', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(8, 1, 81.00, 1.57, '2026-01-30 16:31:05', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(9, 1, 81.00, 1.58, '2026-01-30 16:31:05', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(13, 1, 60.00, 2.99, '2026-02-02 13:26:08', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(14, 1, 70.00, 3.08, '2026-02-06 00:57:24', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(15, 1, 67.00, 3.16, '2026-02-06 00:57:59', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(17, 3, NULL, NULL, '2026-02-06 01:00:59', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(18, 1, 69.04, 3.12, '2026-02-06 01:01:07', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(19, 3, 59.00, 3.07, '2026-02-06 01:01:08', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(20, 3, 69.00, 3.20, '2026-02-06 01:01:12', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(21, 1, 67.00, 3.05, '2026-02-07 13:09:30', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(22, NULL, 0.00, 3.21, '2026-02-07 13:09:36', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(23, 1, 71.00, 3.17, '2026-02-07 13:09:40', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(24, 1, 69.00, 3.03, '2026-02-07 13:16:35', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(25, 1, 79.00, 3.19, '2026-02-07 13:17:14', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(26, 1, 67.00, 3.21, '2026-02-07 13:17:20', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(27, NULL, 0.00, 3.22, '2026-02-07 13:17:42', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(28, 1, 71.00, 3.12, '2026-02-07 13:19:39', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(29, 1, 73.00, 3.11, '2026-02-07 13:22:21', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(30, 1, 74.00, 3.09, '2026-02-07 13:23:29', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(31, 1, 74.00, 3.14, '2026-02-07 13:23:32', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(32, 1, 64.00, 2.83, '2026-02-07 13:26:14', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(33, 1, 70.00, 2.97, '2026-02-07 13:29:25', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(34, NULL, 0.00, 3.00, '2026-02-07 13:30:02', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(39, 1, 61.00, 2.62, '2026-02-09 12:46:10', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(41, 7, NULL, NULL, '2026-02-09 12:46:15', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(43, 7, NULL, NULL, '2026-02-09 12:46:15', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(44, 7, 71.00, 3.10, '2026-02-09 12:46:18', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(45, 1, 61.00, 3.20, '2026-02-09 12:46:28', 1, 1, 0, NULL, NULL, NULL, NULL, NULL),
(46, 1, 70.00, 0.79, '2026-02-09 12:57:59', 1, 1, 0, 'both', NULL, NULL, NULL, NULL),
(47, 1, 77.00, 3.03, '2026-02-09 13:40:55', 1, 1, 0, '1440p', 77.00, NULL, 3.03, NULL),
(48, 1, 72.00, 1.15, '2026-02-09 13:42:33', 1, 1, 0, 'both', 72.00, 67.00, 3.10, 1.82),
(49, 1, 72.00, 1.20, '2026-02-09 13:47:19', 1, 1, 0, 'both', 72.00, 66.00, 3.19, 1.91),
(50, 8, NULL, NULL, '2026-02-12 13:22:34', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(51, 8, NULL, NULL, '2026-02-12 13:22:34', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(52, 1, 73.00, 1.10, '2026-02-12 13:22:46', 1, 1, 0, 'both', 73.00, 62.00, 2.73, 1.83),
(53, 8, 70.00, 1.70, '2026-02-12 13:22:50', 1, 1, 0, '1440p', 70.00, NULL, 2.98, 3.93),
(54, 9, NULL, NULL, '2026-02-12 13:26:58', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(55, 1, 74.00, 1.11, '2026-02-12 13:27:04', 1, 1, 0, 'both', 74.00, 67.00, 2.86, 1.81),
(56, 1, 74.00, 1.12, '2026-02-12 13:27:07', 1, 1, 0, 'both', 74.00, 67.00, 3.07, 1.76),
(57, 1, 73.00, 1.12, '2026-02-12 13:27:09', 1, 1, 0, 'both', 73.00, 68.00, 2.98, 1.79),
(58, 1, 65.00, 1.13, '2026-02-12 13:27:11', 1, 1, 0, 'both', 65.00, 61.00, 3.06, 1.79),
(59, 1, 62.46, 3.08, '2026-02-12 13:27:15', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(60, 1, 62.00, 1.09, '2026-02-12 13:27:15', 1, 1, 0, '1440p', 62.00, NULL, 3.08, 1.68),
(61, 8, 61.58, 3.05, '2026-02-12 13:27:18', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(62, 8, 61.00, 1.13, '2026-02-12 13:27:19', 1, 1, 0, '1440p', 61.00, NULL, 3.05, 1.79),
(63, 1, 70.00, 1.08, '2026-02-12 13:27:37', 1, 1, 0, 'both', 70.00, 67.00, 2.95, 1.69),
(64, 1, 67.00, 1.14, '2026-02-12 13:27:39', 1, 1, 0, 'both', 67.00, 64.00, 3.04, 1.81),
(65, 1, 67.00, 1.72, '2026-02-12 13:27:44', 1, 1, 0, '1440p', 67.00, NULL, 3.03, 3.97),
(66, 1, 74.00, 1.14, '2026-02-12 13:27:49', 1, 1, 0, 'both', 74.00, 69.00, 3.02, 1.83),
(67, 8, 70.15, 3.05, '2026-02-12 13:27:50', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(68, 8, 70.00, 1.11, '2026-02-12 13:27:51', 1, 1, 0, '1440p', 70.00, NULL, 3.05, 1.75),
(69, 1, 64.27, 3.03, '2026-02-12 13:27:54', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(70, 1, 64.00, 1.13, '2026-02-12 13:27:54', 1, 1, 0, '1440p', 64.00, NULL, 3.03, 1.81),
(71, 1, 69.00, 1.15, '2026-02-12 13:27:57', 1, 1, 0, 'both', 69.00, 62.00, 3.04, 1.85),
(72, 1, 62.00, 1.14, '2026-02-12 13:27:59', 1, 1, 0, 'both', 62.00, 59.00, 3.02, 1.83),
(73, 1, 69.00, 1.14, '2026-02-12 13:28:01', 1, 1, 0, 'both', 69.00, 59.00, 3.04, 1.83),
(74, 7, 55.91, 3.03, '2026-02-12 13:28:02', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(75, 7, 55.00, 1.12, '2026-02-12 13:28:03', 1, 1, 0, '1440p', 55.00, NULL, 3.03, 1.77),
(76, 1, 60.49, 3.04, '2026-02-12 13:28:04', 0, 0, 0, NULL, NULL, NULL, NULL, NULL),
(77, 1, 60.00, 1.12, '2026-02-12 13:28:05', 1, 1, 0, '1440p', 60.00, NULL, 3.04, 1.78),
(78, 10, NULL, NULL, '2026-02-12 13:40:57', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(79, 11, NULL, NULL, '2026-02-12 13:50:44', 1, 1, 1, NULL, NULL, NULL, NULL, NULL),
(80, 10, 72.00, 1.12, '2026-02-12 13:50:50', 1, 1, 0, 'both', 72.00, 67.00, 2.94, 1.82),
(81, 11, 72.00, 1.14, '2026-02-12 13:50:53', 1, 1, 0, 'both', 72.00, 65.00, 3.04, 1.83),
(82, 11, 65.00, 1.13, '2026-02-12 13:50:59', 1, 1, 0, 'both', 65.00, 60.00, 3.00, 1.82),
(83, 11, 66.00, 1.14, '2026-02-12 13:51:01', 1, 1, 0, 'both', 66.00, 57.00, 3.04, 1.81),
(84, 11, 65.00, 1.13, '2026-02-12 13:51:03', 1, 1, 0, 'both', 65.00, 64.00, 3.00, 1.82),
(85, 1, 74.00, 1.13, '2026-02-12 13:51:05', 1, 1, 0, 'both', 74.00, 67.00, 2.96, 1.82),
(86, 11, 68.00, 1.14, '2026-02-12 13:51:07', 1, 1, 0, '1440p', 68.00, NULL, 3.01, 1.83),
(87, 11, 66.00, 1.06, '2026-02-12 13:53:51', 1, 1, 0, 'both', 66.00, 61.00, 2.89, 1.67),
(88, 11, 59.00, 1.14, '2026-02-12 13:53:55', 1, 1, 0, 'both', 59.00, 57.00, 3.01, 1.82),
(89, 10, 65.00, 1.12, '2026-02-12 13:53:57', 1, 1, 0, '1080p', NULL, 65.00, 2.94, 1.82);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `recognized_faces`
--
ALTER TABLE `recognized_faces`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `recognized_faces`
--
ALTER TABLE `recognized_faces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=90;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `recognized_faces`
--
ALTER TABLE `recognized_faces`
  ADD CONSTRAINT `recognized_faces_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
