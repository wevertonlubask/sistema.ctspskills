import React from 'react';
import { clsx } from 'clsx';

interface Competitor {
  id: string;
  name: string;
}

interface CompetitorSelectProps {
  competitors: Competitor[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label?: string;
}

export const CompetitorSelect: React.FC<CompetitorSelectProps> = ({
  competitors,
  selected,
  onChange,
  label = 'Competidores',
}) => {
  const toggleCompetitor = (id: string) => {
    if (selected.includes(id)) {
      onChange(selected.filter(s => s !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  const selectAll = () => {
    onChange(competitors.map(c => c.id));
  };

  const deselectAll = () => {
    onChange([]);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={selectAll}
            className="text-xs text-blue-600 hover:text-blue-500"
          >
            Todos
          </button>
          <span className="text-gray-400">|</span>
          <button
            type="button"
            onClick={deselectAll}
            className="text-xs text-blue-600 hover:text-blue-500"
          >
            Nenhum
          </button>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {competitors.map(competitor => (
          <button
            key={competitor.id}
            type="button"
            onClick={() => toggleCompetitor(competitor.id)}
            className={clsx(
              'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
              selected.includes(competitor.id)
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            )}
          >
            {competitor.name}
          </button>
        ))}
      </div>
    </div>
  );
};
