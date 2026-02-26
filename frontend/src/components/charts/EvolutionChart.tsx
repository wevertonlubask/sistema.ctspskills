import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface CompetitorEvolution {
  competitorId: string;
  competitorName: string;
  data: Array<{
    simuladoName: string;
    date: string;
    score: number;
  }>;
}

interface EvolutionChartProps {
  data: CompetitorEvolution[];
  height?: number;
}

const COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // yellow
  '#EF4444', // red
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#F97316', // orange
];

export const EvolutionChart: React.FC<EvolutionChartProps> = ({
  data,
  height = 400,
}) => {
  // Transform data for recharts
  // We need to create a unified dataset where each point has all competitor scores
  const allSimulados = data.length > 0
    ? data[0].data.map(d => d.simuladoName)
    : [];

  const chartData = allSimulados.map((simuladoName, index) => {
    const point: Record<string, any> = {
      name: simuladoName,
      index: index + 1,
    };

    data.forEach(competitor => {
      const competitorData = competitor.data.find(d => d.simuladoName === simuladoName);
      point[competitor.competitorName] = competitorData?.score || null;
    });

    return point;
  });

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        Selecione competidores para visualizar a evolução
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={chartData}
        margin={{ top: 10, right: 30, left: 20, bottom: 80 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
        <XAxis
          dataKey="name"
          tick={{ fill: '#6B7280', fontSize: 11 }}
          axisLine={{ stroke: '#374151' }}
          angle={-35}
          textAnchor="end"
          height={80}
          interval={0}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fill: '#6B7280', fontSize: 12 }}
          axisLine={{ stroke: '#374151' }}
          label={{
            value: 'Nota',
            angle: -90,
            position: 'insideLeft',
            fill: '#6B7280',
          }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1F2937',
            border: 'none',
            borderRadius: '8px',
            color: '#F3F4F6',
          }}
          formatter={(value: number) => [value?.toFixed(1), 'Nota']}
        />
        <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 16 }} />
        {data.map((competitor, index) => (
          <Line
            key={competitor.competitorId}
            type="monotone"
            dataKey={competitor.competitorName}
            stroke={COLORS[index % COLORS.length]}
            strokeWidth={2}
            dot={{ fill: COLORS[index % COLORS.length], strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};
