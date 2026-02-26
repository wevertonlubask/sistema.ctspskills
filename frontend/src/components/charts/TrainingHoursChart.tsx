import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';

export interface TrainingHoursData {
  date: string;
  hours: number;
  label?: string;
}

interface TrainingHoursChartProps {
  data: TrainingHoursData[];
  height?: number;
  targetHoursPerDay?: number;
  showTarget?: boolean;
  targetLabel?: string;
}

export const TrainingHoursChart: React.FC<TrainingHoursChartProps> = ({
  data,
  height = 250,
  targetHoursPerDay,
  showTarget = true,
  targetLabel,
}) => {
  // Format date for display
  const chartData = data.map(item => ({
    ...item,
    displayDate: item.label || formatDate(item.date),
  }));

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  }

  // Ensure Y axis domain always includes the target line value
  const target = showTarget && targetHoursPerDay ? targetHoursPerDay : 0;
  const yDomain: [number, (dataMax: number) => number] = [
    0,
    (dataMax: number) => Math.max(dataMax, target * 1.2) || 1,
  ];

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
        <XAxis
          dataKey="displayDate"
          tick={{ fill: '#6B7280', fontSize: 11 }}
          axisLine={{ stroke: '#374151' }}
          interval={0}
          angle={-45}
          textAnchor="end"
          height={60}
        />
        <YAxis
          tick={{ fill: '#6B7280', fontSize: 11 }}
          axisLine={{ stroke: '#374151' }}
          domain={yDomain}
          label={{ value: 'Horas', angle: -90, position: 'insideLeft', fill: '#6B7280', fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1F2937',
            border: 'none',
            borderRadius: '8px',
            color: '#F3F4F6',
          }}
          formatter={(value: number) => [`${value}h`, 'Horas']}
          labelFormatter={(label) => `Data: ${label}`}
        />
        <Legend />
        <Bar
          dataKey="hours"
          name="Horas de Treino"
          fill="#F59E0B"
          radius={[4, 4, 0, 0]}
        />
        {showTarget && targetHoursPerDay != null && targetHoursPerDay > 0 && (
          <ReferenceLine
            y={targetHoursPerDay}
            stroke="#10B981"
            strokeDasharray="5 5"
            ifOverflow="extendDomain"
            label={{
              value: targetLabel || `Meta: ${targetHoursPerDay}h`,
              fill: '#10B981',
              fontSize: 11,
              position: 'right',
            }}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
};
