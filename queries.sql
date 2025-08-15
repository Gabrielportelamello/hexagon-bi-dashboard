/* AdventureWorks -> SalesDB
   Nível: linha do pedido (SalesOrderDetail) para permitir agregações no Pandas.
   Região: ShipToAddress -> Person.Address -> Person.StateProvince (conforme enunciado).
*/

-- parâmetros
DECLARE @start_date date              = :start_date;        -- inclusive
DECLARE @end_date   date              = :end_date;          -- exclusivo
DECLARE @min_amount decimal(18,2)     = :min_amount;
DECLARE @categories_csv nvarchar(max) = :categories_csv;    -- 'Bikes,Components'
DECLARE @regions_csv    nvarchar(max) = :regions_csv;       -- 'Washington,California'

SELECT
    CAST(h.OrderDate AS date)                        AS OrderDate,
    h.SalesOrderID,
    CAST(h.TotalDue AS decimal(18,2))                AS TotalDue,          -- total do pedido (header)
    d.ProductID,
    p.Name                                          AS ProductName,
    pc.Name                                         AS Category,
    sp.Name                                         AS Region,             -- região via Address -> StateProvince
    d.OrderQty                                      AS Quantity,
    CAST(d.LineTotal AS decimal(18,2))              AS LineAmount          -- total da linha (detalhe)
FROM Sales.SalesOrderHeader AS h
JOIN Sales.SalesOrderDetail AS d
  ON d.SalesOrderID = h.SalesOrderID
JOIN Production.Product AS p
  ON p.ProductID = d.ProductID
LEFT JOIN Production.ProductSubcategory AS psc
  ON psc.ProductSubcategoryID = p.ProductSubcategoryID
LEFT JOIN Production.ProductCategory AS pc
  ON pc.ProductCategoryID = psc.ProductCategoryID
LEFT JOIN Person.Address AS a
  ON a.AddressID = h.ShipToAddressID
LEFT JOIN Person.StateProvince AS sp
  ON sp.StateProvinceID = a.StateProvinceID
WHERE h.OrderDate >= @start_date
  AND h.OrderDate <  @end_date
  AND CAST(d.LineTotal AS decimal(18,2)) >= @min_amount
  AND (
        @categories_csv = '' OR COALESCE(pc.Name,'(Sem categoria)') IN (
            SELECT LTRIM(RTRIM(value)) FROM string_split(@categories_csv, ',')
        )
      )
  AND (
        @regions_csv = '' OR COALESCE(sp.Name,'(Sem região)') IN (
            SELECT LTRIM(RTRIM(value)) FROM string_split(@regions_csv, ',')
        )
      )
ORDER BY h.OrderDate;
