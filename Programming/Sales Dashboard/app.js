(async function(){
    const $ = id => document.getElementById(id);

    const params = () => ({
        start: $('startDate').value,
        end: $('endDate').value,
        region: $('regionFilter').value
    });

    const charts = {};
    function createChart(id, config) {
        const ctx = document.getElementById(id).getContext('2d');
        if (charts[id]) charts[id].destroy();
        charts[id] = new Chart(ctx, config);
    }

    async function fetchData() {
        const qs = new URLSearchParams(params());
        const res = await fetch('/api/sales?' + qs.toString());
        if (!res.ok) throw new Error('Backend unavailable');
        return await res.json();
    }

    function render(data) {
        $('totalSales').textContent = `$${data.summary.total_sales.toFixed(2)}`;
        $('ordersCount').textContent = data.summary.orders;
        $('avgOrder').textContent = `$${data.summary.avg_order.toFixed(2)}`;
    
        createChart('salesTrend', {
            type: 'line',
            data: {
                labels: data.monthly.map(m => m.month),
                datasets: [{label : 'Sales', data: data.monthly.map(m => m.total), fill: true, backgroundColor: 'rgba(255, 111, 161, 0.2)', borderColor: '#ff6fa1'}]
            }
        });

        createChart('salesByCategory', {
            type: 'doughnut',
            data: {
                labels: data.by_category.map(c => c.category),
                datasets: [{ 
                    data: data.by_category.map(c => c.total),
                    backgroundColor: ['#ff6fa1','#4a90e2','#a0a0a0','#ffb6c1','#6fa8ff']
                }]
            }
        });

        createChart('topProducts', {
            type: 'bar',
            data: {
                labels: data.top_products.map(p => p.product),
                datasets: [{ 
                    label: 'Revenue', 
                    data: data.top_products.map(p => p.total),
                    backgroundColor: '#4a90e2'}] 
            },
            options: { indexAxis: 'y' }
        });

        createChart('salesByRegion', {
            type: 'pie',
            data: {
                labels: data.by_region.map(r => r.region),
                datasets: [{ 
                    data: data.by_region.map(r => r.total),
                    backgroundColor: ['#ff6fa1','#4a90e2','#a0a0a0']
                }]
            }
        });

        const tbody = document.querySelector('#ordersTable tbody');
        tbody.innerHTML = '';
        data.recent_orders.forEach(order => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${order.id}</td>
                            <td>${order.date}</td>
                            <td>${order.product}</td>
                            <td>${order.qty}</td>
                            <td>$${order.total.toFixed(2)}</td>
                            <td>${order.region}</td>`;
            tbody.appendChild(tr);
        });
    }

    async function refresh() {
        const data = await fetchData();
        render(data);
    }

    $('refreshBtn').addEventListener('click', refresh);
    $('regionFilter').addEventListener('change', refresh);

    //default dates
    const today = new Date();
    const past = new Date();
    past.setDate(today.getDate() - 90);
    $('endDate').value = today.toISOString().slice(0,10);
    $('startDate').value = past.toISOString().slice(0,10);

    refresh();
})();