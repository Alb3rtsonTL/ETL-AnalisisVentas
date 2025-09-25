-- Total ventas por producto
SELECT p.ProductID, p.ProductName, SUM(od.TotalPrice) AS TotalSales
FROM order_details od
JOIN products p ON p.ProductID = od.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY TotalSales DESC;

-- Total ventas por cliente
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName, SUM(od.TotalPrice) AS TotalSpent
FROM orders o
JOIN order_details od ON o.OrderID = od.OrderID
JOIN customers c ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, CustomerName
ORDER BY TotalSpent DESC;

-- Ventas por mes
SELECT DATE_FORMAT(o.OrderDate, '%Y-%m') AS YearMonth, SUM(od.TotalPrice) AS TotalSales
FROM orders o
JOIN order_details od ON o.OrderID = od.OrderID
GROUP BY YearMonth
ORDER BY YearMonth;
