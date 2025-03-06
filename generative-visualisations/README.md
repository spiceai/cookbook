

## Installation
python
```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Example results
```html
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="salesTrendChart" width="600" height="400"></canvas>
    <script>
        var ctx = document.getElementById('salesTrendChart').getContext('2d');
        var salesTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], // This will be populated with month-year labels from the query result
                datasets: [{
                    label: 'Total Sales',
                    data: [], // This will be populated with total_sales from the query result
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Month-Year'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Total Sales'
                        }
                    }
                }
            }
        });

        // This function should be called with the actual SQL query results
document.addEventListener('DOMContentLoaded', (event) => {
    const data = [ /* Example data: {month: 1, year: 2021, total_sales: 2000} */ ];
    data.forEach((point) => {
        salesTrendChart.data.labels.push(point.year + '-' + ('0' + point.month).slice(-2));
        salesTrendChart.data.datasets[0].data.push(point.total_sales);
    });
    salesTrendChart.update();
});
    </script>
</body>
</html>
```
```sql
SELECT "year", "month", SUM("sales") as total_sales
FROM spice.public.sales
GROUP BY "year", "month"
ORDER BY "year", "month";
```
```json
[{'year': 2003, 'month': 1, 'total_sales': 129753.6}, {'year': 2003, 'month': 2, 'total_sales': 140836.19000000003}, {'year': 2003, 'month': 3, 'total_sales': 174504.9}, {'year': 2003, 'month': 4, 'total_sales': 201609.55000000002}, {'year': 2003, 'month': 5, 'total_sales': 192673.11}, {'year': 2003, 'month': 6, 'total_sales': 168082.55999999997}, {'year': 2003, 'month': 7, 'total_sales': 187731.87999999998}, {'year': 2003, 'month': 8, 'total_sales': 197809.3}, {'year': 2003, 'month': 9, 'total_sales': 263973.36}, {'year': 2003, 'month': 10, 'total_sales': 568290.97}, {'year': 2003, 'month': 11, 'total_sales': 1029837.6600000001}, {'year': 2003, 'month': 12, 'total_sales': 261876.46000000005}, {'year': 2004, 'month': 1, 'total_sales': 316577.4200000001}, {'year': 2004, 'month': 2, 'total_sales': 311419.5299999999}, {'year': 2004, 'month': 3, 'total_sales': 205733.72999999992}, {'year': 2004, 'month': 4, 'total_sales': 206148.12000000008}, {'year': 2004, 'month': 5, 'total_sales': 273438.3900000001}, {'year': 2004, 'month': 6, 'total_sales': 286674.22}, {'year': 2004, 'month': 7, 'total_sales': 327144.0899999998}, {'year': 2004, 'month': 8, 'total_sales': 461501.2700000001}, {'year': 2004, 'month': 9, 'total_sales': 320750.91000000003}, {'year': 2004, 'month': 10, 'total_sales': 552924.25}, {'year': 2004, 'month': 11, 'total_sales': 1089048.0100000005}, {'year': 2004, 'month': 12, 'total_sales': 372802.6599999999}, {'year': 2005, 'month': 1, 'total_sales': 339543.42}, {'year': 2005, 'month': 2, 'total_sales': 358186.18000000005}, {'year': 2005, 'month': 3, 'total_sales': 374262.7599999999}, {'year': 2005, 'month': 4, 'total_sales': 261633.29000000007}, {'year': 2005, 'month': 5, 'total_sales': 457861.05999999965}]
```
```markdown
Here’s what the data reveals about monthly sales trends over the period:

• In 2003, sales started modestly early in the year, then gradually increased until a dramatic spike in October and especially November – November sales were nearly a million, more than four times the sum seen in the earlier months. However, December saw a steep drop relative to November.

• The 2004 figures show a similar pattern of seasonal fluctuation. While the first half of the year had moderate sales with some fluctuations (for instance, March and April were lower compared to January/February), the numbers picked up later. Summer months like July and August were higher, building up to another strong peak in November where sales exceeded one million. December again was lower compared to the November peak.

• The partial data for 2005 (covering January through May) indicates some growth in the first three months, with January starting lower and rising in February and March. However, April dipped noticeably before rebounding in May.

• Across the years, there appears to be an overall seasonal pattern: sales are generally lower at the start of the year, tend to increase as the summer progresses, and reach their highest point in late fall (notably in November). The repeated high peaks in November for both 2003 and 2004 suggest a strong seasonal driver during that period.

• In addition, although the data for 2005 is incomplete, there’s some indication of a potential growth trend over the years, with the early months of 2005 showing higher absolute numbers compared to 2003 in some cases.

Overall, the data highlights both strong seasonal effects—with a notable spike around November—and hints of an upward trend in sales magnitude over the years.
```
