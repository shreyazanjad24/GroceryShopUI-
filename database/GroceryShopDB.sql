-- ====================================================================
-- MINI PROJECT: GROCERY SHOP MANAGEMENT SYSTEM
-- AIM: Demonstrating Creation, Modification, Manipulation,
--      Authorization & Views of Database with Front-End Connectivity.
-- Database: MySQL Workbench
-- Front-End: Flask (Python) + Bootstrap 5
-- ====================================================================

DROP DATABASE IF EXISTS GroceryShopDB;
CREATE DATABASE GroceryShopDB;
USE GroceryShopDB;

-- ====================================================================
-- 1. DATABASE CREATION (DDL)
-- ====================================================================

-- 1.1 PRODUCT TABLE
CREATE TABLE PRODUCT (
    Product_ID INT PRIMARY KEY,
    Product_Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    Brand VARCHAR(50),
    Purchase_Price DECIMAL(10,2),
    Selling_Price DECIMAL(10,2),
    Available_Quantity INT,
    Expiry_Date DATE
);

-- 1.2 SUPPLIER TABLE
CREATE TABLE SUPPLIER (
    Supplier_ID INT PRIMARY KEY,
    Supplier_Name VARCHAR(100) NOT NULL,
    Address VARCHAR(200),
    Phone_Number VARCHAR(15)
);

-- 1.3 BILL TABLE
CREATE TABLE BILL (
    Bill_ID INT PRIMARY KEY,
    Bill_Name VARCHAR(100),
    Payment_Method VARCHAR(30),
    Discount DECIMAL(10,2) DEFAULT 0,
    Total_Amount DECIMAL(10,2),
    Transaction_ID VARCHAR(30) UNIQUE
);

-- 1.4 INCLUDE RELATIONSHIP: BILL AND PRODUCT (COMPOSITE KEY & FOREIGN KEYS)
CREATE TABLE BILL_PRODUCT (
    Bill_ID INT,
    Product_ID INT,
    Quantity INT NOT NULL,
    Unit_Selling_Price DECIMAL(10,2),
    PRIMARY KEY (Bill_ID, Product_ID),
    FOREIGN KEY (Bill_ID) REFERENCES BILL(Bill_ID) ON DELETE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE CASCADE
);

-- 1.5 SUPPLIES RELATIONSHIP: PRODUCT AND SUPPLIER
CREATE TABLE PRODUCT_SUPPLIER (
    Product_ID INT,
    Supplier_ID INT,
    PRIMARY KEY (Product_ID, Supplier_ID),
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID) ON DELETE CASCADE,
    FOREIGN KEY (Supplier_ID) REFERENCES SUPPLIER(Supplier_ID) ON DELETE CASCADE
);

-- 1.6 SUPPLIER BILLINGS & PAYMENTS
CREATE TABLE IF NOT EXISTS SUPPLIER_PAYMENT (
    Payment_ID INT PRIMARY KEY,
    Supplier_ID INT,
    Invoice_Number VARCHAR(50),
    Bill_Amount DECIMAL(10,2) NOT NULL,
    Amount_Paid DECIMAL(10,2) NOT NULL,
    Payment_Date DATE,
    Payment_Method VARCHAR(30),
    Payment_Status VARCHAR(20) DEFAULT 'Paid',
    Notes VARCHAR(200),
    FOREIGN KEY (Supplier_ID) REFERENCES SUPPLIER(Supplier_ID) ON DELETE CASCADE
);

-- ====================================================================
-- 2. DATA MANIPULATION - INSERTION (DML)
-- ====================================================================

-- Insert into PRODUCT
INSERT INTO PRODUCT VALUES
(101,'Fortune Sunflower Oil','Oil','Fortune',125.00,145.00,80,'2027-06-30'),
(102,'Tata Salt','Grocery','Tata',20.00,25.00,150,'2028-12-31'),
(103,'Parle-G Biscuits','Biscuits','Parle',5.00,6.00,200,'2027-08-15'),
(104,'Good Day Cookies','Biscuits','Britannia',25.00,30.00,90,'2027-09-20'),
(105,'Amul Milk','Dairy','Amul',26.00,30.00,60,'2026-10-25'),
(106,'Amul Butter','Dairy','Amul',52.00,60.00,45,'2027-02-28'),
(107,'Maggi Noodles','Snacks','Nestle',12.00,15.00,120,'2027-07-31'),
(108,'Tata Tea Gold','Beverages','Tata',145.00,165.00,35,'2027-12-31'),
(109,'Nescafe Coffee','Beverages','Nestle',120.00,140.00,25,'2027-11-30'),
(110,'Aashirvaad Atta','Flour','ITC',210.00,240.00,40,'2027-05-31'),
(111,'India Gate Basmati Rice','Rice','India Gate',95.00,115.00,55,'2028-01-31'),
(112,'Surf Excel Detergent','Detergents','Surf Excel',105.00,125.00,30,'2028-06-30'),
(113,'Dove Soap','Personal Care','Dove',42.00,50.00,70,'2028-03-31'),
(114,'Colgate Toothpaste','Personal Care','Colgate',65.00,75.00,50,'2028-04-30'),
(115,'Kissan Tomato Ketchup','Sauces','Kissan',85.00,100.00,32,'2027-10-31');

-- Insert into SUPPLIER
INSERT INTO SUPPLIER VALUES
(201,'Shree Ganesh Distributors','Itwari, Nagpur','9876501001'),
(202,'Mahalaxmi Wholesale','Gandhibagh, Nagpur','9876501002'),
(203,'Vidarbha Foods Supply','Dharampeth, Nagpur','9876501003'),
(204,'Fresh Dairy Suppliers','Sadar, Nagpur','9876501004'),
(205,'National Grocery Traders','Kalamna, Nagpur','9876501005'),
(206,'Om Sai Consumer Goods','Sitabuldi, Nagpur','9876501006'),
(207,'Reliable FMCG Distributors','Hingna, Nagpur','9876501007'),
(208,'Shivam General Suppliers','Manish Nagar, Nagpur','9876501008');

-- Insert into BILL
INSERT INTO BILL VALUES
(301,'Customer 1','Cash',5.00,170.00,'TXN1001'),
(302,'Customer 2','UPI',10.00,230.00,'TXN1002'),
(303,'Customer 3','Card',0.00,150.00,'TXN1003'),
(304,'Customer 4','UPI',15.00,285.00,'TXN1004'),
(305,'Customer 5','Cash',0.00,120.00,'TXN1005'),
(306,'Customer 6','Card',20.00,310.00,'TXN1006'),
(307,'Customer 7','UPI',5.00,195.00,'TXN1007'),
(308,'Customer 8','Cash',10.00,250.00,'TXN1008'),
(309,'Customer 9','UPI',0.00,180.00,'TXN1009'),
(310,'Customer 10','Card',25.00,400.00,'TXN1010'),
(311,'Customer 11','Cash',5.00,135.00,'TXN1011'),
(312,'Customer 12','UPI',0.00,220.00,'TXN1012');

-- Insert into BILL_PRODUCT
INSERT INTO BILL_PRODUCT VALUES
(301,101,1,145.00),
(301,103,5,6.00),
(302,110,1,240.00),
(302,102,2,25.00),
(303,107,4,15.00),
(304,111,2,115.00),
(304,104,2,30.00),
(305,105,4,30.00),
(306,112,2,125.00),
(307,106,2,60.00),
(308,108,1,165.00),
(308,103,5,6.00),
(309,113,2,50.00),
(310,109,2,140.00),
(311,114,1,75.00);

-- Insert into PRODUCT_SUPPLIER
INSERT INTO PRODUCT_SUPPLIER VALUES
(101,201),
(102,202),
(103,203),
(104,203),
(105,204),
(106,204),
(107,205),
(108,206),
(110,207),
(113,208);

-- Insert into SUPPLIER_PAYMENT
INSERT INTO SUPPLIER_PAYMENT VALUES
(501, 201, 'INV-SG-8801', 12500.00, 12500.00, '2026-10-15', 'Bank Transfer', 'Paid', 'Fortnightly oil supply settlement'),
(502, 202, 'INV-MW-4202', 4500.00, 4500.00, '2026-10-18', 'UPI', 'Paid', 'Tata salt bulk purchase'),
(503, 203, 'INV-VF-1090', 8200.00, 5000.00, '2026-10-22', 'Cheque', 'Partial', 'Biscuits & confectionery delivery (bal 3200)'),
(504, 204, 'INV-FD-3312', 6400.00, 6400.00, '2026-10-25', 'UPI', 'Paid', 'Dairy butter & milk supply'),
(505, 207, 'INV-RF-7741', 15800.00, 0.00, '2026-10-28', 'Bank Transfer', 'Pending', 'Atta & detergent wholesale consignment');

-- ====================================================================
-- 3. DATABASE MODIFICATION (DDL - ALTER TABLE)
-- ====================================================================

-- 3.1 Adding Email column to SUPPLIER table
ALTER TABLE SUPPLIER
ADD Email VARCHAR(100);

-- Update some email values
UPDATE SUPPLIER SET Email = 'ganesh_dist@example.com' WHERE Supplier_ID = 201;
UPDATE SUPPLIER SET Email = 'mahalaxmi_wh@example.com' WHERE Supplier_ID = 202;
UPDATE SUPPLIER SET Email = 'vidarbha_foods@example.com' WHERE Supplier_ID = 203;

-- 3.2 Modifying Category column size in PRODUCT table
ALTER TABLE PRODUCT
MODIFY Category VARCHAR(100);

-- ====================================================================
-- 4. DATABASE VIEWS
-- ====================================================================

-- 4.1 Product_View: Hides Purchase_Price from end-users/cashiers
CREATE OR REPLACE VIEW Product_View AS
SELECT 
    Product_ID, 
    Product_Name, 
    Category,
    Brand,
    Selling_Price, 
    Available_Quantity
FROM PRODUCT;

-- 4.2 Bill_Summary_View: Joins Bill with Products & calculated items
CREATE OR REPLACE VIEW Bill_Summary_View AS
SELECT 
    B.Bill_ID,
    B.Bill_Name,
    B.Payment_Method,
    B.Total_Amount,
    COUNT(BP.Product_ID) AS Total_Items
FROM BILL B
LEFT JOIN BILL_PRODUCT BP ON B.Bill_ID = BP.Bill_ID
GROUP BY B.Bill_ID, B.Bill_Name, B.Payment_Method, B.Total_Amount;

-- ====================================================================
-- 5. DATABASE AUTHORIZATION (DCL: CREATE USER, GRANT, REVOKE)
-- ====================================================================

-- 5.1 Create Restricted Viewer User (e.g. Cashier / Catalog Viewer)
CREATE USER IF NOT EXISTS 'grocery_viewer'@'localhost' IDENTIFIED BY 'Grocery@123';

-- 5.2 Grant SELECT privilege only on views and specific tables
GRANT SELECT ON GroceryShopDB.Product_View TO 'grocery_viewer'@'localhost';
GRANT SELECT ON GroceryShopDB.PRODUCT TO 'grocery_viewer'@'localhost';
GRANT SELECT ON GroceryShopDB.BILL TO 'grocery_viewer'@'localhost';
GRANT SELECT ON GroceryShopDB.Bill_Summary_View TO 'grocery_viewer'@'localhost';

FLUSH PRIVILEGES;

-- 5.3 Show grants for verification
SHOW GRANTS FOR 'grocery_viewer'@'localhost';

-- ====================================================================
-- 6. STORED PROCEDURES, FUNCTIONS & TRIGGERS (BONUS PRACTICAL DEMO)
-- ====================================================================

-- Stored Procedure to filter products by category
DROP PROCEDURE IF EXISTS GetProductsByCategory;
DELIMITER //
CREATE PROCEDURE GetProductsByCategory(
    IN category_name VARCHAR(50)
)
BEGIN
    SELECT Product_ID, Product_Name, Category, Brand, Selling_Price, Available_Quantity
    FROM PRODUCT
    WHERE Category = category_name;
END //
DELIMITER ;

-- Stored Function to calculate total stock value of a specific product
DROP FUNCTION IF EXISTS CalculateStockValue;
DELIMITER //
CREATE FUNCTION CalculateStockValue(
    product_id_input INT
)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE stock_value DECIMAL(12,2);
    SELECT Selling_Price * Available_Quantity
    INTO stock_value
    FROM PRODUCT
    WHERE Product_ID = product_id_input;
    RETURN IFNULL(stock_value, 0);
END //
DELIMITER ;

-- Trigger: Prevent negative stock quantity during updates
DROP TRIGGER IF EXISTS CheckProductQuantity;
DELIMITER //
CREATE TRIGGER CheckProductQuantity
BEFORE UPDATE ON PRODUCT
FOR EACH ROW
BEGIN
    IF NEW.Available_Quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Available quantity cannot be negative';
    END IF;
END //
DELIMITER ;

