-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Vært: mysql
-- Genereringstid: 27. 05 2025 kl. 12:56:37
-- Serverversion: 9.3.0
-- PHP-version: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `shelter`
--

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `images`
--

CREATE TABLE `images` (
  `image_pk` varchar(36) NOT NULL,
  `item_pk` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `image_name` varchar(255) DEFAULT NULL,
  `created_at` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Data dump for tabellen `images`
--

INSERT INTO `images` (`image_pk`, `item_pk`, `image_name`, `created_at`) VALUES
('07f2bca7e3be47fdb388d8640e888b0e', '0d86277c-a9b7-4d22-a3a4-39b7255cd6fb', '525c5450749e4fde8808960cd3ecabf6.jpg', 1747939057),
('0f595a98892b4a818b249f7b49690c24', '7251a6bc-102d-4ecf-8cce-6d7849151fa6', '70cb6706431b4606ab9503c319896256.webp', 1747937942),
('1796a7b783d04d12847c16be8ed3c14c', 'b282e548-168c-418c-8a12-53facafe8638', 'bcf7cf67dfbc4b5caa51d66649c92d61.jpeg', 1748078517),
('18f45c5007e4476c9e7c0c20cc822953', '6c184a18-9ffd-4e05-950a-b550ceae2f34', 'd3d083a84695499599033236899d9001.jpg', 1748079355),
('194825d662724a4bac3855ee5f99b679', 'f9a05084-a4df-40ce-96c3-142684a6b300', 'cc1036ab453f44e89eaca1493221170c.jpg', 1747938320),
('1f7cecf0bcf44cafa4adbe3e3d72fbe4', '6e5db8a1-d429-408b-9775-38afb2f52960', 'a03b084fa8e44143a1ba79041dd078c9.jpg', 1747938478),
('249ff945b3cb4eed80b281ffa466ab63', '034f7982-ad7d-4dfc-bcc2-5c87a24a52cd', 'e49ae5951e614704ae349dcf3d65e411.jpg', 1748080248),
('2b876f8ec44041d7993e63d006b02ac2', '6e5db8a1-d429-408b-9775-38afb2f52960', '1a63fcb8772a4a13a2ba286dcb3937ed.jpg', 1747938478),
('3075e5c910d44d8b80bf4cf96d92595f', '6c184a18-9ffd-4e05-950a-b550ceae2f34', 'a98ba23767884de98d5cb27bce1d027c.webp', 1748079355),
('32df39f021db4a98b1f86ffd4e15d9e8', '6e5db8a1-d429-408b-9775-38afb2f52960', 'a3355c9ce799450f8f9c5751b02d922f.jpg', 1747938478),
('3b138314d2d14eefb0581cd854129bd8', '998c4e4b-994d-4fa6-9e9c-1367865b7df5', 'd27151b38666489dbe0d99b90dcc2369.jpg', 1748078955),
('421399c20f8c4476a3a7ec0f0f94732c', '80d9217a-7fe5-4473-bbe4-20494579db16', '819604078ca24f649dbbedce80fb3bc4.jpg', 1748078235),
('42daa70826c74013a553649c64fb8530', '7251a6bc-102d-4ecf-8cce-6d7849151fa6', '251eb1c55a9a4a35b08590bf4eac0906.webp', 1747937942),
('49612f34eced497690f87a21c8ef5d60', 'f9a05084-a4df-40ce-96c3-142684a6b300', '546ead8cd19d46eb9bc516689428251b.webp', 1747938320),
('4a162e37cf1140bba8dd5c525d083ebf', '28007129-11eb-434e-8a21-8f247cb62ab3', 'd7695c518a3c4e61bfe3c1a1076ff6be.jpg', 1747938645),
('4f990da6ad4c4646b8b1367579f5390f', '28007129-11eb-434e-8a21-8f247cb62ab3', '8f8b8c8853a74d339a5d0cf230ad79c7.jpg', 1747938645),
('55b676f496e84b52a6e2b677005fe619', '28007129-11eb-434e-8a21-8f247cb62ab3', '512f859fcc374025a98fba873523802c.jpg', 1747938645),
('6e1fcce2124b43948cabca2e45dce804', 'f9a05084-a4df-40ce-96c3-142684a6b300', '26c0b6b06a104663bbbe1bd8e994ea3e.jpg', 1747938320),
('70985a240a53478ebf44a1e0f8ae0421', '6e5db8a1-d429-408b-9775-38afb2f52960', 'b0a1157e5d734d8eb02d178dcda5d33c.jpg', 1747938478),
('7bbeb641e9fb42e08cdf369b30f0089c', '0d86277c-a9b7-4d22-a3a4-39b7255cd6fb', '3f9626dbbf8c45229d89923e2dcfcc4f.jpg', 1747939057),
('7ca36e3f4aad4d9c92f0add9a8af91aa', '2041fbb0-b57b-4cea-8be6-5f00b9589add', 'e1fc4c160bd440d0b8deee55be18c80a.jpg', 1748077632),
('94b753952965444cb8299b4d5244e59a', '80d9217a-7fe5-4473-bbe4-20494579db16', 'f6ff6638a61546728b9aab345125b900.jpg', 1748078235),
('94e84c3a72654aa49d630deee0ed2883', '034f7982-ad7d-4dfc-bcc2-5c87a24a52cd', 'c52d5548a2984ea6903a991b116adb01.jpg', 1748080248),
('97244b38caa94c89b05f64f3a3b88b28', '2041fbb0-b57b-4cea-8be6-5f00b9589add', '765a1365c9604efbb18feb0e0a5b6942.jpg', 1748077632),
('986bb2c3dae24d4a9ee027086130d629', '6c184a18-9ffd-4e05-950a-b550ceae2f34', 'a1ad5428e9ea45158568cfe0e333f548.jpg', 1748079355),
('9dbf5b0bae21441099ed8e60177211c5', '998c4e4b-994d-4fa6-9e9c-1367865b7df5', '74f3bf6bca1c4dbe8a6187a9f7e7713d.jpg', 1748078955),
('a54cd267b73742afa096aa8a9313eeec', '0d86277c-a9b7-4d22-a3a4-39b7255cd6fb', '422b6ff299044e3184ec1faede531dc7.jpg', 1747939057),
('ca95566efb2841189dc61661a77dc3ea', '998c4e4b-994d-4fa6-9e9c-1367865b7df5', '0b5d0a3c46b443c087fbc7df6cd392a3.jpg', 1748078955),
('caa7ddc850024ebf8b065f1bc998a6a1', 'b282e548-168c-418c-8a12-53facafe8638', 'f0259c383e434305b55077b3ff1085b1.jpg', 1748078517),
('cbbc826762f74846b467c1ff13025076', '2041fbb0-b57b-4cea-8be6-5f00b9589add', 'cf7fe97d1e704c91841bde44734a9589.jpg', 1748077632),
('cecbe9eb37ec41a9b75d4b81747f529a', '80d9217a-7fe5-4473-bbe4-20494579db16', 'aff8eef9b4f94ced8fb0778ab5047319.jpg', 1748078235),
('d9610f77152f470ab3a563445b1bd7e0', '6e5db8a1-d429-408b-9775-38afb2f52960', '8a2ddf6fed4b41fca5fe7c814502a79a.jpg', 1747938478),
('e79483af5bdf49ffbf3b334059d50265', 'b282e548-168c-418c-8a12-53facafe8638', 'f3732d10e89c42de95987a5ad68cedd8.jpg', 1748078517),
('ef88559f3fe24f0a88d3c2b8d28c4910', '28007129-11eb-434e-8a21-8f247cb62ab3', 'f8d0d15274ec48b4955306733d5cef57.jpg', 1747938645),
('f3e5060a53a7481a8c6d6fc29c3434ba', '034f7982-ad7d-4dfc-bcc2-5c87a24a52cd', 'a10875a64913473b9fb3d52e7c177ad3.webp', 1748080248),
('fa4e77ba6d074dd2a1a52e4d5cebed15', '7251a6bc-102d-4ecf-8cce-6d7849151fa6', '460118f6261b478ead6f8fa1ecedffca.webp', 1747937942);

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `items`
--

CREATE TABLE `items` (
  `item_pk` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `item_name` varchar(50) NOT NULL,
  `item_image` varchar(255) DEFAULT NULL,
  `item_address` varchar(255) NOT NULL,
  `item_icon` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'shelter.svg',
  `item_price` int UNSIGNED NOT NULL,
  `item_lon` varchar(50) NOT NULL,
  `item_lat` varchar(50) NOT NULL,
  `item_created_at` bigint UNSIGNED NOT NULL,
  `item_blocked_at` bigint NOT NULL DEFAULT '0',
  `item_updated_at` bigint UNSIGNED DEFAULT NULL,
  `item_deleted_at` bigint NOT NULL DEFAULT '0',
  `user_fk` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Data dump for tabellen `items`
--

INSERT INTO `items` (`item_pk`, `item_name`, `item_image`, `item_address`, `item_icon`, `item_price`, `item_lon`, `item_lat`, `item_created_at`, `item_blocked_at`, `item_updated_at`, `item_deleted_at`, `user_fk`) VALUES
('034f7982-ad7d-4dfc-bcc2-5c87a24a52cd', 'Shelter ved Gribskov', 'c52d5548a2984ea6903a991b116adb01.jpg', 'Gribskov, 3200 Helsinge', 'shelter.svg', 19, '12.3', '56.0', 1748080248, 0, NULL, 0, 'f8efb1d6-5813-4a5a-8fdd-94b998eb4ffb'),
('0d86277c-a9b7-4d22-a3a4-39b7255cd6fb', 'Stigsnæs Skov Shelters', '525c5450749e4fde8808960cd3ecabf6.jpg', 'Skovvej 5, 4400 Kalundborg', 'shelter.svg', 21, '11.25', '55.25', 1747939057, 0, 1748344405, 0, 'a9acaf19-91d1-4de1-bf94-e379b013a71e'),
('2041fbb0-b57b-4cea-8be6-5f00b9589add', 'Rørhøgen Shelter', 'cf7fe97d1e704c91841bde44734a9589.jpg', 'Sonnerup Skov, ved Arresø, 3300 Frederiksværk', 'shelter.svg', 13, '12.06151', '55.951954', 1748077632, 0, NULL, 0, '7213a8cd-079e-4fc2-ae1e-b37d5ca5bf94'),
('28007129-11eb-434e-8a21-8f247cb62ab3', 'Avnø Naturcenter Shelters', 'f8d0d15274ec48b4955306733d5cef57.jpg', 'Avnøvej 12, 4700 Næstved', 'shelter.svg', 17, '12.0804', '55.6415', 1747938645, 0, NULL, 0, 'a9acaf19-91d1-4de1-bf94-e379b013a71e'),
('6c184a18-9ffd-4e05-950a-b550ceae2f34', 'Shelter ved Bidstrup Skovene', 'a1ad5428e9ea45158568cfe0e333f548.jpg', 'Bidstrup Skovene, 4330 Hvalsø', 'shelter.svg', 16, '11.85', '55.587', 1748079355, 0, NULL, 0, 'f8efb1d6-5813-4a5a-8fdd-94b998eb4ffb'),
('6e5db8a1-d429-408b-9775-38afb2f52960', 'Boserup Skov Shelter', 'a3355c9ce799450f8f9c5751b02d922f.jpg', 'Boserupvej 3, 4000 Roskilde', 'shelter.svg', 13, '11.7609', '55.2299', 1747938478, 0, NULL, 0, 'a9acaf19-91d1-4de1-bf94-e379b013a71e'),
('7251a6bc-102d-4ecf-8cce-6d7849151fa6', 'Flagbakken Shelter', '460118f6261b478ead6f8fa1ecedffca.webp', 'Flagbakken 7, 4100 Ringsted', 'shelter.svg', 19, '12.4', '55.28', 1747937942, 0, NULL, 0, 'a9acaf19-91d1-4de1-bf94-e379b013a71e'),
('80d9217a-7fe5-4473-bbe4-20494579db16', 'Egernet og Flagermusen Sheltere', 'f6ff6638a61546728b9aab345125b900.jpg', 'Kelleris Hegn, Hørsholm Kongevej, 3490 Kvistgård', 'shelter.svg', 18, '12.510541', '55.988192', 1748078234, 0, 1748078824, 0, '7213a8cd-079e-4fc2-ae1e-b37d5ca5bf94'),
('998c4e4b-994d-4fa6-9e9c-1367865b7df5', 'Shelter ved Teglværkshavnen', '0b5d0a3c46b443c087fbc7df6cd392a3.jpg', 'Frederikskaj 8, 2450 København SV', 'shelter.svg', 14, '12.564', '55.656', 1748078955, 0, NULL, 0, '7213a8cd-079e-4fc2-ae1e-b37d5ca5bf94'),
('b282e548-168c-418c-8a12-53facafe8638', 'Perlemorsommerfuglen Sheltere', 'bcf7cf67dfbc4b5caa51d66649c92d61.jpeg', 'Kelleris Hegn, Hørsholm Kongevej, 3490 Kvistgård', 'shelter.svg', 23, '12.558441', '55.999791', 1748078517, 0, NULL, 0, '7213a8cd-079e-4fc2-ae1e-b37d5ca5bf94'),
('f9a05084-a4df-40ce-96c3-142684a6b300', 'Skovhyttens Shelters', '26c0b6b06a104663bbbe1bd8e994ea3e.jpg', 'Skovvej 12, 4400 Kalundborg', 'shelter.svg', 15, '11.1386', '55.3299', 1747938320, 0, NULL, 0, 'a9acaf19-91d1-4de1-bf94-e379b013a71e');

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `users`
--

CREATE TABLE `users` (
  `user_pk` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_last_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `user_role` enum('user','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'user',
  `user_verification_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_created_at` bigint UNSIGNED NOT NULL,
  `user_updated_at` bigint UNSIGNED NOT NULL DEFAULT '0',
  `user_deleted_at` bigint UNSIGNED NOT NULL DEFAULT '0',
  `user_verified_at` bigint NOT NULL DEFAULT '0',
  `user_blocked_at` bigint NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users`
--

INSERT INTO `users` (`user_pk`, `user_username`, `user_name`, `user_last_name`, `user_email`, `user_password`, `user_role`, `user_verification_key`, `user_created_at`, `user_updated_at`, `user_deleted_at`, `user_verified_at`, `user_blocked_at`) VALUES
('7213a8cd-079e-4fc2-ae1e-b37d5ca5bf94', 'usertwo', 'User', 'Two', 'user_two@user.com', 'scrypt:32768:8:1$YqB546SGswcE78oh$9296c986ed2c9da4b2718ade0a24a442e71e8acdca565902d67944db935691233d000b9941af3ed562c40ed80393a36af5001ed5a001178ddf18e8ce433c633d', 'user', NULL, 1748076703, 20250527111223, 0, 1747935458, 0),
('87c02902-373d-11f0-9eda-0242ac120002', 'admin', 'admin', 'admin', 'admin@admin.com', 'scrypt:32768:8:1$e6YUcjgqZ3iCb5mz$f3a3ab84a6482b8d58e2b95a17fb21ca5616b6062398388db07a04eb6758349034b3a8c4751ff2103a01a0c3f679ba278c3964ac0bab438f9cece3f13d1f3c6f', 'admin', NULL, 1747935418, 20250522191120, 0, 1747935459, 0),
('a9acaf19-91d1-4de1-bf94-e379b013a71e', 'andreahauberg', 'Andrea', 'Hauberg', 'andrea.hauberg1@gmail.com', 'scrypt:32768:8:1$rLmw7qRiTWIs5RWj$2185916458a46eb51c632d11f167534452bc467364f533729076a9c064181d08d66f03f4736936ed643ee16176470a8ca92b3ab6715dff115a8a2d5efe76730c', 'user', NULL, 1747935417, 20250527125440, 0, 1747935452, 0),
('f8efb1d6-5813-4a5a-8fdd-94b998eb4ffb', 'userone', 'User', 'One', 'user_one@user.com', 'scrypt:32768:8:1$7yDZHYJl1U3NFyvS$ab73f9f4b1bf90ed95d30ff2725b05129297a03c6ca049cb239d3a1c3630ee9617db6a194977827f07b02b64b025651928c915b1d17d444a391c76e7196d2b6c', 'user', NULL, 1748076502, 20250524084948, 0, 1747935455, 0);

--
-- Triggers/udløsere `users`
--
DELIMITER $$
CREATE TRIGGER `update_user` BEFORE UPDATE ON `users` FOR EACH ROW SET NEW.user_updated_at = NOW()
$$
DELIMITER ;

--
-- Begrænsninger for dumpede tabeller
--

--
-- Indeks for tabel `images`
--
ALTER TABLE `images`
  ADD PRIMARY KEY (`image_pk`),
  ADD KEY `fk_images_items` (`item_pk`);

--
-- Indeks for tabel `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`item_pk`),
  ADD KEY `fk_items_users` (`user_fk`);

--
-- Indeks for tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_pk` (`user_pk`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD UNIQUE KEY `user_username` (`user_username`);

--
-- Begrænsninger for dumpede tabeller
--

--
-- Begrænsninger for tabel `images`
--
ALTER TABLE `images`
  ADD CONSTRAINT `fk_images_items` FOREIGN KEY (`item_pk`) REFERENCES `items` (`item_pk`) ON DELETE CASCADE,
  ADD CONSTRAINT `images_ibfk_1` FOREIGN KEY (`item_pk`) REFERENCES `items` (`item_pk`);

--
-- Begrænsninger for tabel `items`
--
ALTER TABLE `items`
  ADD CONSTRAINT `fk_items_users` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
