// server.js
const express = require('express');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

const app = express();
const PORT = 3000;

// Serve frontend files
app.use(express.static(path.join(__dirname)));

app.get('/api/sales', (req, res) => {
  const { start, end, region } = req.query;

  const results = [];
  fs.createReadStream(path.join(__dirname, 'supermarket_sales_new.csv'))
    .pipe(csv())
    .on('data', (row) => {
      // Calculate total from unit price, quantity, and tax
      const unitPrice = parseFloat(row['Unit price']);
      const quantity = parseInt(row.Quantity);
      const tax = parseFloat(row['Tax 5%']);
      const total = (unitPrice * quantity) + tax;
      
      // Add calculated total and formatted date to row
      row.Total = total;
      row.Date = '2023-01-01'; // Placeholder - you'll need to add real dates to your CSV
      
      results.push(row);
    })
    .on('end', () => {
      // Filter by date + region
      let filtered = results;
      if (start && end) {
        const s = new Date(start), e = new Date(end);
        filtered = filtered.filter(r => {
          const d = new Date(r.Date);
          return d >= s && d <= e;
        });
      }
      if (region && region !== 'all') {
        // Map branches to regions
        const regionMap = {
          'A': 'North',
          'B': 'South', 
          'C': 'East'
        };
        filtered = filtered.filter(r => regionMap[r.Branch] === region);
      }

      // Aggregate
      const summary = {
        total_sales: filtered.reduce((a, r) => a + parseFloat(r.Total), 0),
        orders: filtered.length,
        avg_order: filtered.length ? filtered.reduce((a, r) => a + parseFloat(r.Total), 0) / filtered.length : 0
      };

      // Monthly totals
      const monthlyMap = {};
      filtered.forEach(r => {
        const m = r.Date.slice(0,7); // YYYY-MM
        monthlyMap[m] = (monthlyMap[m] || 0) + parseFloat(r.Total);
      });
      const monthly = Object.keys(monthlyMap).map(m => ({ month: m, total: monthlyMap[m] }));

      // By category (using Product line)
      const catMap = {};
      filtered.forEach(r => { 
        catMap[r['Product line']] = (catMap[r['Product line']] || 0) + parseFloat(r.Total); 
      });
      const by_category = Object.keys(catMap).map(c => ({ category: c, total: catMap[c] }));

      // Top products
      const prodMap = {};
      filtered.forEach(r => { 
        prodMap[r['Product line']] = (prodMap[r['Product line']] || 0) + parseFloat(r.Total); 
      });
      const top_products = Object.entries(prodMap).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([product,total])=>({product,total}));

      // By region
      const regMap = {};
      const branchToRegion = {
        'A': 'North',
        'B': 'South', 
        'C': 'East'
      };
      filtered.forEach(r => { 
        const region = branchToRegion[r.Branch];
        regMap[region] = (regMap[region] || 0) + parseFloat(r.Total); 
      });
      const by_region = Object.keys(regMap).map(r => ({ region: r, total: regMap[r] }));

      // Recent orders
      const recent_orders = filtered.slice(-10).map(r => ({
        id: r['Invoice ID'],
        date: r.Date,
        product: r['Product line'],
        qty: +r.Quantity,
        total: +r.Total,
        region: branchToRegion[r.Branch]
      }));

      res.json({ summary, monthly, by_category, top_products, by_region, recent_orders });
    });
});

app.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));