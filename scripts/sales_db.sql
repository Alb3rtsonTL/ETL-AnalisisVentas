-- Crear base de datos
CREATE DATABASE IF NOT EXISTS sales_db;
USE sales_db;

-- Customers
CREATE TABLE customers (
  CustomerID INT PRIMARY KEY,
  FirstName VARCHAR(100),
  LastName VARCHAR(100),
  Email VARCHAR(150),
  Phone VARCHAR(50),
  City VARCHAR(100),
  Country VARCHAR(100)
);

-- Products
CREATE TABLE products (
  ProductID INT PRIMARY KEY,
  ProductName VARCHAR(200),
  Category VARCHAR(100),
  Price DECIMAL(10,2),
  Stock INT
);

-- Orders
CREATE TABLE orders (
  OrderID INT PRIMARY KEY,
  CustomerID INT,
  OrderDate DATETIME,
  Status VARCHAR(50),
  FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
);

-- Order Details
CREATE TABLE order_details (
  OrderID INT,
  ProductID INT,
  Quantity INT,
  TotalPrice DECIMAL(12,2),
  PRIMARY KEY (OrderID, ProductID),
  FOREIGN KEY (OrderID) REFERENCES orders(OrderID),
  FOREIGN KEY (ProductID) REFERENCES products(ProductID)
);
