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

export interface ProgressData {
  name: string;
  atual: number;
  meta?: number;
}

interface ProgressChartProps {
  data?: ProgressData[];
  height?: number;
  showMeta?: boolean;
  metaGlobal?: number;
  atualLabel?: string;
  metaLabel?: string;
}

// Default data for backwards compatibility
const defaultData: ProgressData[] = [
  { name: 'Soldagem', atual: 85, meta: 90 },
  { name: 'Usinagem', atual: 72, meta: 80 },
  { name: 'CAD', atual: 90, meta: 85 },
  { name: 'Elétrica', atual: 68, meta: 75 },
  { name: 'Mecânica', atual: 78, meta: 80 },
];

export const ProgressChart: React.FC<ProgressChartProps> = ({
  data = defaultData,
  height = 300,
  showMeta = true,
  metaGlobal,
  atualLabel = 'Média Atual',
  metaLabel = 'Meta',
}) => {
  // Apply global meta to data if provided
  const chartData = metaGlobal
    ? data.map(item => ({ ...item, meta: item.meta ?? metaGlobal }))
    : data;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
        <XAxis
          dataKey="name"
          tick={{ fill: '#6B7280', fontSize: 12 }}
          axisLine={{ stroke: '#374151' }}
        />
        <YAxis
          tick={{ fill: '#6B7280', fontSize: 12 }}
          axisLine={{ stroke: '#374151' }}
          domain={[0, 100]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1F2937',
            border: 'none',
            borderRadius: '8px',
            color: '#F3F4F6',
          }}
        />
        <Legend />
        <Bar dataKey="atual" name={atualLabel} fill="#3B82F6" radius={[4, 4, 0, 0]} />
        {showMeta && <Bar dataKey="meta" name={metaLabel} fill="#10B981" radius={[4, 4, 0, 0]} />}
        {metaGlobal && (
          <ReferenceLine
            y={metaGlobal}
            stroke="#F59E0B"
            strokeDasharray="5 5"
            label={{
              value: `${metaLabel}: ${metaGlobal}`,
              fill: '#F59E0B',
              fontSize: 12,
              position: 'right',
            }}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
};
