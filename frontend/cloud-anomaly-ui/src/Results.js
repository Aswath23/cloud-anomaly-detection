import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const COLORS = ["#0088FE", "#00C49F"];

const Results = ({ results }) => {
  const data = [
    { name: "SVM Accuracy", value: results["SVM Accuracy"] * 100 },
    { name: "RF Accuracy", value: results["RF Accuracy"] * 100 },
  ];

  return (
    <PieChart width={400} height={300}>
      <Pie data={data} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value">
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index]} />
        ))}
      </Pie>
      <Tooltip />
      <Legend />
    </PieChart>
  );
};

export default Results;

