# Recharts Library Explanation

## What is Recharts?

**Recharts** is a composable charting library built on React and D3.js. It provides a declarative way to create charts using React components, making it easy to build responsive, interactive data visualizations.

**Key Features:**
- ✅ Built on React (component-based)
- ✅ Responsive by default
- ✅ Declarative API (compose components)
- ✅ Built on D3.js (powerful, battle-tested)
- ✅ TypeScript support
- ✅ Customizable styling

---

## Core Architecture

### Component Composition Model

Recharts uses a **composition pattern** where you compose smaller components to build complex charts:

```
Chart Container (LineChart, BarChart, PieChart, etc.)
  ├── Data Layer (data prop)
  ├── Grid (CartesianGrid)
  ├── Axes (XAxis, YAxis)
  ├── Data Visualization (Line, Bar, Area, Pie)
  ├── Interactive Elements (Tooltip, Legend)
  └── Responsive Wrapper (ResponsiveContainer)
```

---

## How Recharts Works

### 1. **Chart Container Components**

These are the main chart types that define the coordinate system:

#### **LineChart** - For line/trend visualizations
```tsx
<LineChart data={data}>
  {/* Chart elements */}
</LineChart>
```

#### **BarChart** - For bar/comparison visualizations
```tsx
<BarChart data={data}>
  {/* Chart elements */}
</BarChart>
```

#### **AreaChart** - For filled area/stacked visualizations
```tsx
<AreaChart data={data}>
  {/* Chart elements */}
</AreaChart>
```

#### **PieChart** - For pie/donut visualizations
```tsx
<PieChart>
  <Pie data={data} />
</PieChart>
```

### 2. **Data Format**

Recharts expects data as an **array of objects** where each object represents a data point:

```typescript
// Example: Time series data
const data = [
  { date: "2025-01-01", cost: 10.50, executions: 100 },
  { date: "2025-01-02", cost: 15.75, executions: 150 },
  { date: "2025-01-03", cost: 12.25, executions: 120 },
]

// Example: Categorical data
const data = [
  { name: "OpenAI", value: 45 },
  { name: "Anthropic", value: 30 },
  { name: "Other", value: 25 },
]
```

### 3. **Core Components**

#### **ResponsiveContainer**
Wraps the chart to make it responsive:

```tsx
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    {/* Chart content */}
  </LineChart>
</ResponsiveContainer>
```

**Why it's needed:** Charts need a fixed height, but ResponsiveContainer makes them scale with container width.

#### **CartesianGrid**
Adds grid lines for readability:

```tsx
<CartesianGrid strokeDasharray="3 3" />
```

#### **XAxis / YAxis**
Define the axes:

```tsx
<XAxis
  dataKey="date"           // Which field from data to use
  tick={{ fontSize: 12 }} // Styling
  angle={-45}             // Rotate labels
  textAnchor="end"         // Anchor point
/>
<YAxis
  tick={{ fontSize: 12 }}
  domain={[0, 100]}        // Min/max range
/>
```

#### **Data Visualization Components**

**Line** - Draws lines:
```tsx
<Line
  type="monotone"          // Line smoothing
  dataKey="cost"           // Data field
  stroke="#8884d8"        // Color
  strokeWidth={2}         // Thickness
  dot={{ r: 4 }}          // Dot size
  name="Cost ($)"         // Legend label
/>
```

**Bar** - Draws bars:
```tsx
<Bar
  dataKey="cost"
  fill="#8884d8"
  name="Cost ($)"
/>
```

**Area** - Draws filled areas:
```tsx
<Area
  type="monotone"
  dataKey="completed"
  stackId="1"              // Stack multiple areas
  stroke="#82ca9d"
  fill="#82ca9d"
  name="Completed"
/>
```

**Pie** - Draws pie slices:
```tsx
<Pie
  data={data}
  cx="50%"                 // Center X
  cy="50%"                 // Center Y
  labelLine={false}        // Show label lines
  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
  outerRadius={80}         // Size
  fill="#8884d8"
  dataKey="value"
>
  {/* Individual cells for colors */}
  {data.map((_, index) => (
    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
  ))}
</Pie>
```

#### **Tooltip**
Shows data on hover:

```tsx
<Tooltip
  formatter={(value: number) => `$${value.toFixed(2)}`}  // Format value
  labelStyle={{ color: "#000" }}                         // Style
  contentStyle={{ backgroundColor: "#fff" }}            // Background
/>
```

#### **Legend**
Shows what each series represents:

```tsx
<Legend />
```

---

## Real Examples from Our Codebase

### Example 1: Cost Trend Line Chart

```tsx
// From CostAnalytics.tsx
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={metrics.cost_trend}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis
      dataKey="date"
      tick={{ fontSize: 12 }}
      angle={-45}
      textAnchor="end"
      height={80}
    />
    <YAxis tick={{ fontSize: 12 }} />
    <Tooltip
      formatter={(value: number) => `$${value.toFixed(2)}`}
      labelStyle={{ color: "#000" }}
    />
    <Legend />
    <Line
      type="monotone"
      dataKey="cost"
      stroke="#8884d8"
      strokeWidth={2}
      name="Cost ($)"
      dot={{ r: 4 }}
    />
    <Line
      type="monotone"
      dataKey="executions"
      stroke="#82ca9d"
      strokeWidth={2}
      name="Executions"
      dot={{ r: 4 }}
    />
  </LineChart>
</ResponsiveContainer>
```

**How it works:**
1. `ResponsiveContainer` makes it responsive
2. `LineChart` creates a line chart coordinate system
3. `data={metrics.cost_trend}` provides the data array
4. `XAxis` uses `date` field from each data point
5. `YAxis` auto-scales based on data values
6. Two `Line` components draw two lines (cost and executions)
7. `Tooltip` shows formatted values on hover
8. `Legend` shows what each line represents

### Example 2: Stacked Area Chart

```tsx
// From AnalyticsPanel.tsx
<AreaChart data={trends.trends}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Area
    type="monotone"
    dataKey="total_executions"
    stackId="1"
    stroke="#8884d8"
    fill="#8884d8"
    name="Total Executions"
  />
  <Area
    type="monotone"
    dataKey="completed"
    stackId="1"
    stroke="#82ca9d"
    fill="#82ca9d"
    name="Completed"
  />
  <Area
    type="monotone"
    dataKey="failed"
    stackId="1"
    stroke="#ff7300"
    fill="#ff7300"
    name="Failed"
  />
</AreaChart>
```

**Key concept:** `stackId="1"` makes all areas stack on top of each other, creating a cumulative visualization.

### Example 3: Pie Chart

```tsx
// From ConnectorStats.tsx
<PieChart>
  <Pie
    data={Object.entries(stats.by_status).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
    }))}
    cx="50%"
    cy="50%"
    labelLine={false}
    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
    outerRadius={80}
    fill="#8884d8"
    dataKey="value"
  >
    {Object.entries(stats.by_status).map((_, index) => (
      <Cell
        key={`cell-${index}`}
        fill={COLORS[index % COLORS.length]}
      />
    ))}
  </Pie>
  <Tooltip />
  <Legend />
</PieChart>
```

**How it works:**
1. `PieChart` creates a circular coordinate system
2. `Pie` component draws the pie slices
3. Each `Cell` inside `Pie` gets a different color
4. `label` prop formats the slice labels
5. `dataKey="value"` tells it which field to use for slice size

### Example 4: Bar Chart

```tsx
// From SystemMetrics.tsx
<BarChart data={resourceData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="name" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Bar dataKey="value" fill="#8884d8" name="Count" />
</BarChart>
```

**Simple and straightforward:** One `Bar` component draws bars for each data point.

---

## Data Flow

```
1. Data Array
   ↓
2. Chart Container (LineChart/BarChart/etc.)
   ↓
3. Axes extract data for labels (XAxis uses dataKey)
   ↓
4. Visualization components (Line/Bar/Area) extract values
   ↓
5. D3.js renders SVG elements
   ↓
6. Tooltip/Legend provide interactivity
```

---

## Key Concepts

### 1. **dataKey**
Tells components which field from your data object to use:

```tsx
// If data is: [{ date: "2025-01-01", cost: 10 }]
<XAxis dataKey="date" />  // Uses "date" field
<Line dataKey="cost" />   // Uses "cost" field
```

### 2. **stackId**
Groups multiple areas/bars to stack them:

```tsx
<Area stackId="1" dataKey="completed" />
<Area stackId="1" dataKey="failed" />  // Stacks on top of completed
```

### 3. **Responsive Design**
Always wrap charts in `ResponsiveContainer`:

```tsx
<ResponsiveContainer width="100%" height={300}>
  {/* Chart */}
</ResponsiveContainer>
```

### 4. **Styling**
- Colors: Use `stroke` (line color) and `fill` (fill color)
- Sizes: Use `strokeWidth`, `dot={{ r: 4 }}`, `outerRadius={80}`
- Typography: Use `tick={{ fontSize: 12 }}` on axes

---

## Best Practices

### ✅ DO:

1. **Always use ResponsiveContainer:**
   ```tsx
   <ResponsiveContainer width="100%" height={300}>
     <LineChart data={data}>...</LineChart>
   </ResponsiveContainer>
   ```

2. **Format tooltips:**
   ```tsx
   <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
   ```

3. **Handle empty data:**
   ```tsx
   {data.length > 0 ? (
     <LineChart data={data}>...</LineChart>
   ) : (
     <div>No data available</div>
   )}
   ```

4. **Use meaningful names:**
   ```tsx
   <Line name="Cost ($)" />  // Shows in legend
   ```

5. **Customize axes:**
   ```tsx
   <XAxis
     angle={-45}      // Rotate for readability
     tick={{ fontSize: 12 }}  // Adjust size
   />
   ```

### ❌ DON'T:

1. **Don't forget ResponsiveContainer** - Charts won't be responsive
2. **Don't use nested charts** - One chart container per visualization
3. **Don't forget dataKey** - Components won't know which field to use
4. **Don't use inconsistent colors** - Use a color palette

---

## Common Patterns in Our Codebase

### Pattern 1: Time Series Chart
```tsx
<LineChart data={timeSeriesData}>
  <XAxis dataKey="date" />
  <YAxis />
  <Line dataKey="value" />
</LineChart>
```

### Pattern 2: Comparison Chart
```tsx
<BarChart data={comparisonData}>
  <XAxis dataKey="name" />
  <YAxis />
  <Bar dataKey="value" />
</BarChart>
```

### Pattern 3: Distribution Chart
```tsx
<PieChart>
  <Pie data={distributionData} dataKey="value">
    {data.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
  </Pie>
</PieChart>
```

### Pattern 4: Stacked Chart
```tsx
<AreaChart data={stackedData}>
  <Area stackId="1" dataKey="series1" />
  <Area stackId="1" dataKey="series2" />
</AreaChart>
```

---

## Summary

**Recharts = React Components + D3.js Power**

- **Declarative:** Compose components to build charts
- **Responsive:** Use ResponsiveContainer for mobile-friendly charts
- **Flexible:** Customize colors, labels, tooltips, axes
- **Interactive:** Built-in tooltips and legends
- **Type-safe:** Full TypeScript support

The library handles all the complex D3.js math and SVG rendering, giving you a simple React component API to create beautiful, interactive charts!
