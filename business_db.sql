-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 07, 2026 at 11:31 PM
-- Server version: 11.7.2-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `business_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `company`
--

CREATE TABLE `company` (
  `company_id` int(11) NOT NULL,
  `company_name` varchar(100) NOT NULL,
  `industry` varchar(80) NOT NULL,
  `country` varchar(60) NOT NULL,
  `city` varchar(60) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `established_year` year(4) NOT NULL,
  `website` varchar(150) DEFAULT NULL,
  `annual_revenue` decimal(15,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `company`
--

INSERT INTO `company` (`company_id`, `company_name`, `industry`, `country`, `city`, `phone`, `email`, `established_year`, `website`, `annual_revenue`) VALUES
(1, 'TechNova Solutions', 'Information Technology', 'USA', 'San Francisco', '+1-415-555-0101', 'info@technova.com', '2005', 'www.technova.com', 45000000.00),
(2, 'GreenLeaf Foods', 'Food & Beverage', 'Canada', 'Toronto', '+1-416-555-0202', 'contact@greenleaf.ca', '2010', 'www.greenleaf.ca', 12000000.00),
(3, 'SteelForge Industries', 'Manufacturing', 'Germany', 'Munich', '+49-89-5550303', 'hello@steelforge.de', '1998', 'www.steelforge.de', 78000000.00),
(4, 'SunRise Apparel', 'Fashion & Retail', 'India', 'Mumbai', '+91-22-55500404', 'support@sunriseapp.in', '2015', 'www.sunriseapp.in', 8500000.00),
(5, 'OceanBlue Pharma', 'Pharmaceuticals', 'UK', 'London', '+44-20-55500505', 'info@oceanblue.co.uk', '2001', 'www.oceanblue.co.uk', 55000000.00),
(6, 'NovaBuild Constructs', 'Construction', 'UAE', 'Dubai', '+971-4-5550606', 'biz@novabuild.ae', '2008', 'www.novabuild.ae', 32000000.00),
(7, 'BrightMind Edu', 'Education', 'Australia', 'Sydney', '+61-2-55500707', 'hello@brightmind.edu.au', '2012', 'www.brightmind.edu.au', 6000000.00),
(8, 'SwiftLogix', 'Logistics', 'Singapore', 'Singapore', '+65-6555-0808', 'ops@swiftlogix.sg', '2007', 'www.swiftlogix.sg', 19000000.00),
(9, 'ClearWater Energy', 'Renewable Energy', 'Norway', 'Oslo', '+47-21-550909', 'info@clearwater.no', '2003', 'www.clearwater.no', 41000000.00),
(10, 'PixelCraft Studios', 'Media & Entertainment', 'Japan', 'Tokyo', '+81-3-55501010', 'studio@pixelcraft.jp', '2016', 'www.pixelcraft.jp', 9200000.00);

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `customer_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `first_name` varchar(60) NOT NULL,
  `last_name` varchar(60) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `city` varchar(60) DEFAULT NULL,
  `country` varchar(60) NOT NULL,
  `signup_date` date NOT NULL,
  `loyalty_points` int(11) NOT NULL DEFAULT 0,
  `total_spent` decimal(12,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`customer_id`, `company_id`, `first_name`, `last_name`, `email`, `phone`, `city`, `country`, `signup_date`, `loyalty_points`, `total_spent`) VALUES
(1, 1, 'Liam', 'Anderson', 'liam.anderson@email.com', '+1-415-100-0001', 'San Francisco', 'USA', '2021-03-15', 1200, 3200.50),
(2, 1, 'Sophia', 'Martinez', 'sophia.martinez@email.com', '+1-415-100-0002', 'Los Angeles', 'USA', '2020-07-22', 2500, 8750.00),
(3, 1, 'Noah', 'Williams', 'noah.williams@email.com', '+1-206-100-0003', 'Seattle', 'USA', '2022-01-10', 800, 1500.00),
(4, 1, 'Emma', 'Johnson', 'emma.johnson@email.com', '+1-312-100-0004', 'Chicago', 'USA', '2019-11-05', 5000, 15200.75),
(5, 1, 'Oliver', 'Brown', 'oliver.brown@email.com', '+1-646-100-0005', 'New York', 'USA', '2023-02-28', 300, 450.00),
(6, 2, 'Charlotte', 'Taylor', 'charlotte.taylor@email.com', '+1-416-100-0006', 'Toronto', 'Canada', '2021-06-18', 1800, 5400.00),
(7, 2, 'James', 'Moore', 'james.moore@email.com', '+1-604-100-0007', 'Vancouver', 'Canada', '2020-09-30', 3200, 11000.00),
(8, 2, 'Amelia', 'Jackson', 'amelia.jackson@email.com', '+1-514-100-0008', 'Montreal', 'Canada', '2022-04-12', 950, 2800.50),
(9, 2, 'Benjamin', 'White', 'benjamin.white@email.com', '+1-403-100-0009', 'Calgary', 'Canada', '2023-07-01', 100, 320.00),
(10, 2, 'Isabella', 'Harris', 'isabella.harris@email.com', '+1-613-100-0010', 'Ottawa', 'Canada', '2021-12-20', 2100, 6900.00),
(11, 3, 'Lukas', 'Schneider', 'lukas.schneider@email.com', '+49-89-100-0011', 'Munich', 'Germany', '2020-03-08', 4100, 28000.00),
(12, 3, 'Mia', 'Fischer', 'mia.fischer@email.com', '+49-30-100-0012', 'Berlin', 'Germany', '2021-08-25', 2700, 18500.50),
(13, 3, 'Leon', 'Meyer', 'leon.meyer@email.com', '+49-40-100-0013', 'Hamburg', 'Germany', '2019-05-14', 6000, 45000.00),
(14, 3, 'Hannah', 'Wagner', 'hannah.wagner@email.com', '+49-69-100-0014', 'Frankfurt', 'Germany', '2022-11-11', 1300, 9200.00),
(15, 3, 'Felix', 'Becker', 'felix.becker@email.com', '+49-221-100-0015', 'Cologne', 'Germany', '2023-01-19', 600, 4100.00),
(16, 4, 'Arjun', 'Sharma', 'arjun.sharma@email.com', '+91-98-100-0016', 'Mumbai', 'India', '2020-10-02', 3500, 12000.00),
(17, 4, 'Priya', 'Patel', 'priya.patel@email.com', '+91-99-100-0017', 'Ahmedabad', 'India', '2021-04-17', 2200, 7500.00),
(18, 4, 'Rahul', 'Gupta', 'rahul.gupta@email.com', '+91-97-100-0018', 'Delhi', 'India', '2022-08-29', 1100, 3800.00),
(19, 4, 'Sneha', 'Singh', 'sneha.singh@email.com', '+91-96-100-0019', 'Bangalore', 'India', '2023-03-05', 400, 1200.00),
(20, 4, 'Vikram', 'Mehta', 'vikram.mehta@email.com', '+91-95-100-0020', 'Chennai', 'India', '2021-09-22', 2900, 9800.00),
(21, 5, 'Emily', 'Clarke', 'emily.clarke@email.com', '+44-20-100-0021', 'London', 'UK', '2020-01-15', 4800, 16500.00),
(22, 5, 'Harry', 'Evans', 'harry.evans@email.com', '+44-161-100-0022', 'Manchester', 'UK', '2021-05-27', 3100, 10900.00),
(23, 5, 'Grace', 'Wilson', 'grace.wilson@email.com', '+44-131-100-0023', 'Edinburgh', 'UK', '2022-09-09', 1500, 5200.00),
(24, 5, 'Jack', 'Thomas', 'jack.thomas@email.com', '+44-29-100-0024', 'Cardiff', 'UK', '2023-04-01', 200, 680.00),
(25, 5, 'Ella', 'Roberts', 'ella.roberts@email.com', '+44-121-100-0025', 'Birmingham', 'UK', '2020-07-11', 5500, 19000.00),
(26, 6, 'Khalid', 'Al-Rashid', 'khalid.alrashid@email.com', '+971-50-100-0026', 'Dubai', 'UAE', '2021-02-20', 6200, 42000.00),
(27, 6, 'Fatima', 'Al-Mansoori', 'fatima.almansoori@email.com', '+971-55-100-0027', 'Abu Dhabi', 'UAE', '2020-11-30', 4000, 27000.00),
(28, 6, 'Omar', 'Hassan', 'omar.hassan@email.com', '+971-52-100-0028', 'Sharjah', 'UAE', '2022-06-15', 1700, 8900.00),
(29, 6, 'Noor', 'Ibrahim', 'noor.ibrahim@email.com', '+971-56-100-0029', 'Dubai', 'UAE', '2023-08-10', 500, 2500.00),
(30, 6, 'Yusuf', 'Karimi', 'yusuf.karimi@email.com', '+971-54-100-0030', 'Dubai', 'UAE', '2021-10-05', 3300, 21000.00),
(31, 7, 'Chloe', 'Robinson', 'chloe.robinson@email.com', '+61-2-100-0031', 'Sydney', 'Australia', '2020-04-19', 2800, 9600.00),
(32, 7, 'Ethan', 'Walker', 'ethan.walker@email.com', '+61-3-100-0032', 'Melbourne', 'Australia', '2021-07-08', 1900, 6400.00),
(33, 7, 'Madison', 'Hall', 'madison.hall@email.com', '+61-7-100-0033', 'Brisbane', 'Australia', '2022-12-22', 700, 2300.00),
(34, 7, 'Mason', 'Young', 'mason.young@email.com', '+61-8-100-0034', 'Perth', 'Australia', '2023-05-16', 150, 480.00),
(35, 7, 'Aria', 'King', 'aria.king@email.com', '+61-8-100-0035', 'Adelaide', 'Australia', '2021-01-30', 3600, 12800.00),
(36, 8, 'Wei', 'Zhang', 'wei.zhang@email.com', '+65-9100-0036', 'Singapore', 'Singapore', '2020-06-14', 5100, 34000.00),
(37, 8, 'Mei', 'Lin', 'mei.lin@email.com', '+65-9100-0037', 'Singapore', 'Singapore', '2021-03-25', 3700, 24500.00),
(38, 8, 'Jun', 'Tan', 'jun.tan@email.com', '+65-9100-0038', 'Singapore', 'Singapore', '2022-10-07', 1400, 7200.00),
(39, 8, 'Hui', 'Lim', 'hui.lim@email.com', '+65-9100-0039', 'Singapore', 'Singapore', '2023-01-22', 350, 1800.00),
(40, 8, 'Xin', 'Ng', 'xin.ng@email.com', '+65-9100-0040', 'Singapore', 'Singapore', '2021-08-18', 4400, 29000.00),
(41, 9, 'Erik', 'Larsen', 'erik.larsen@email.com', '+47-21-100-0041', 'Oslo', 'Norway', '2020-02-28', 4700, 31000.00),
(42, 9, 'Astrid', 'Hansen', 'astrid.hansen@email.com', '+47-22-100-0042', 'Bergen', 'Norway', '2021-06-10', 3000, 19500.00),
(43, 9, 'Magnus', 'Olsen', 'magnus.olsen@email.com', '+47-23-100-0043', 'Trondheim', 'Norway', '2022-09-03', 1600, 8100.00),
(44, 9, 'Sigrid', 'Berg', 'sigrid.berg@email.com', '+47-24-100-0044', 'Stavanger', 'Norway', '2023-04-14', 250, 1050.00),
(45, 9, 'Bjorn', 'Dahl', 'bjorn.dahl@email.com', '+47-25-100-0045', 'Oslo', 'Norway', '2020-12-01', 5800, 38500.00),
(46, 10, 'Hana', 'Yamamoto', 'hana.yamamoto@email.com', '+81-3-100-0046', 'Tokyo', 'Japan', '2021-02-14', 2600, 8900.00),
(47, 10, 'Kenji', 'Suzuki', 'kenji.suzuki@email.com', '+81-6-100-0047', 'Osaka', 'Japan', '2020-08-20', 4200, 28000.00),
(48, 10, 'Yuki', 'Tanaka', 'yuki.tanaka@email.com', '+81-52-100-0048', 'Nagoya', 'Japan', '2022-03-30', 1000, 3400.00),
(49, 10, 'Rin', 'Watanabe', 'rin.watanabe@email.com', '+81-82-100-0049', 'Hiroshima', 'Japan', '2023-06-06', 450, 1550.00),
(50, 10, 'Sota', 'Ito', 'sota.ito@email.com', '+81-92-100-0050', 'Fukuoka', 'Japan', '2021-11-11', 3800, 25000.00);

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `product_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `product_name` varchar(120) NOT NULL,
  `category` varchar(80) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `stock_quantity` int(11) NOT NULL DEFAULT 0,
  `sku` varchar(40) NOT NULL,
  `description` text DEFAULT NULL,
  `weight_kg` decimal(6,2) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`product_id`, `company_id`, `product_name`, `category`, `unit_price`, `stock_quantity`, `sku`, `description`, `weight_kg`, `is_active`) VALUES
(1, 1, 'CloudSync Pro 1TB', 'Cloud Storage', 199.99, 500, 'TNS-CS-001', '1TB cloud storage subscription – annual.', 0.00, 1),
(2, 1, 'DataShield Antivirus', 'Security Software', 49.99, 1200, 'TNS-AV-002', 'Enterprise antivirus & threat detection.', 0.00, 1),
(3, 1, 'AI Analytics Suite', 'Analytics', 599.00, 150, 'TNS-AI-003', 'Business intelligence powered by machine learning.', 0.00, 1),
(4, 1, 'NetGuard Firewall', 'Networking', 299.00, 300, 'TNS-NW-004', 'Hardware firewall for SMBs.', 1.20, 1),
(5, 2, 'Organic Granola 500g', 'Breakfast', 6.99, 3000, 'GLF-GR-001', 'Whole-grain oats with honey & almonds.', 0.50, 1),
(6, 2, 'Cold Press Orange Juice', 'Beverages', 4.49, 2500, 'GLF-OJ-002', '100% cold-pressed, no preservatives.', 1.00, 1),
(7, 2, 'Vegan Protein Bar', 'Snacks', 2.99, 5000, 'GLF-PB-003', 'Plant-based protein, 20 g per bar.', 0.06, 1),
(8, 2, 'Quinoa Salad Kit', 'Ready Meals', 8.99, 1500, 'GLF-QS-004', 'Pre-washed quinoa with dressing sachet.', 0.70, 1),
(9, 3, 'Stainless Steel Beam 6m', 'Structural Steel', 340.00, 800, 'SFI-SB-001', '6-metre structural beam, 200×100mm section.', 48.00, 1),
(10, 3, 'Galvanised Pipe 3m DN50', 'Piping', 75.00, 2000, 'SFI-GP-002', 'DN50 hot-dip galvanised pipe.', 8.50, 1),
(11, 3, 'Hex Bolt Set M12 x 50', 'Fasteners', 12.50, 10000, 'SFI-HB-003', 'Pack of 100 M12×50 zinc-plated bolts.', 0.80, 1),
(12, 4, 'Men\'s Linen Shirt', 'Men\'s Wear', 24.99, 2000, 'SRA-LS-001', 'Breathable linen, S-XXL sizes.', 0.25, 1),
(13, 4, 'Women\'s Floral Kurta', 'Women\'s Wear', 19.99, 3000, 'SRA-FK-002', 'Traditional Indian print, machine washable.', 0.20, 1),
(14, 4, 'Kids Denim Jacket', 'Kids Wear', 14.99, 1800, 'SRA-DJ-003', 'Soft denim, ages 3-12.', 0.35, 1),
(15, 5, 'Vitamin C 1000mg Tabs', 'Supplements', 9.99, 8000, 'OBP-VC-001', 'Effervescent vitamin C, 30 tablets per tube.', 0.15, 1),
(16, 5, 'OmegaForce Fish Oil', 'Supplements', 14.99, 5000, 'OBP-FO-002', 'Omega-3 EPA/DHA 1000mg, 90 softgels.', 0.30, 1),
(17, 5, 'ColdRelief Syrup 200ml', 'OTC Medicine', 7.49, 4000, 'OBP-CR-003', 'Paracetamol + antihistamine formulation.', 0.22, 1),
(18, 6, 'Ceramic Floor Tile 60×60', 'Tiles', 18.00, 12000, 'NBC-CT-001', 'Polished ceramic, box of 4 tiles (1.44 m²).', 8.00, 1),
(19, 6, 'Ready-Mix Concrete 25kg', 'Cement & Concrete', 9.50, 6000, 'NBC-RC-002', 'General-purpose ready-mix, 25kg bag.', 25.00, 1),
(20, 6, 'PVC Door Frame Set', 'Doors & Windows', 85.00, 1000, 'NBC-DF-003', 'Includes frame, architrave & seals.', 4.50, 1),
(21, 7, 'STEM Robotics Kit Lvl 1', 'STEM Kits', 59.99, 600, 'BME-RK-001', 'Build & program your first robot, age 8+.', 0.90, 1),
(22, 7, 'Interactive Globe 12\"', 'Learning Aids', 39.99, 800, 'BME-IG-002', 'Augmented-reality globe with 3D country facts.', 0.45, 1),
(23, 8, 'GPS Fleet Tracker Pro', 'Telematics', 129.00, 400, 'SLX-GT-001', 'Real-time GPS with driver behaviour analytics.', 0.18, 1),
(24, 8, 'Heavy-Duty Pallet Wrap', 'Packaging', 3.99, 5000, 'SLX-PW-002', '500mm×300m stretch film roll, 23 micron.', 2.50, 1),
(25, 8, 'Label Printer QL-800', 'Warehouse Equipment', 249.00, 200, 'SLX-LP-003', 'High-speed thermal label printer, USB/LAN.', 2.10, 1),
(26, 9, 'Solar Panel 400W Mono', 'Solar Energy', 220.00, 1500, 'CWE-SP-001', 'Monocrystalline 400W, 25-year warranty.', 22.00, 1),
(27, 9, 'Home Battery 10kWh', 'Energy Storage', 3200.00, 100, 'CWE-HB-002', 'LiFePO4 home storage battery system.', 120.00, 1),
(28, 9, 'Smart Energy Monitor', 'Monitoring', 89.00, 700, 'CWE-SM-003', 'Wi-Fi energy monitor, real-time dashboard.', 0.35, 1),
(29, 10, '4K Animation Course', 'Online Course', 79.00, 99999, 'PCS-AC-001', '12-month access, 120+ HD lessons.', 0.00, 1),
(30, 10, 'Digital Art Bundle', 'Software Bundle', 49.00, 99999, 'PCS-DA-002', 'Brushes, textures & templates pack.', 0.00, 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `company`
--
ALTER TABLE `company`
  ADD PRIMARY KEY (`company_id`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`customer_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `fk_customer_company` (`company_id`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`product_id`),
  ADD UNIQUE KEY `sku` (`sku`),
  ADD KEY `fk_product_company` (`company_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `company`
--
ALTER TABLE `company`
  MODIFY `company_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `customer`
--
ALTER TABLE `customer`
  ADD CONSTRAINT `fk_customer_company` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`) ON UPDATE CASCADE;

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `fk_product_company` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
