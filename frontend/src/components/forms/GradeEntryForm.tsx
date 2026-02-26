import React, { useState } from 'react';
import { Button, Badge } from '../ui';

interface Competitor {
  id: string;
  name: string;
  currentScore?: number;
}

interface Competence {
  id: string;
  name: string;
  maxScore: number;
  weight: number;
}

interface GradeEntry {
  competitorId: string;
  competenceId: string;
  score: number;
}

interface GradeEntryFormProps {
  simuladoId: string;
  simuladoName: string;
  onSubmit: (data: { simuladoId: string; grades: GradeEntry[] }) => void;
  onCancel: () => void;
}

// Mock data - would come from API
const mockCompetitors: Competitor[] = [
  { id: '1', name: 'João Santos', currentScore: 78 },
  { id: '2', name: 'Maria Souza', currentScore: 85 },
  { id: '3', name: 'Pedro Lima', currentScore: 72 },
  { id: '4', name: 'Ana Clara Ferreira', currentScore: undefined },
  { id: '5', name: 'Lucas Mendes', currentScore: undefined },
];

const mockCompetences: Competence[] = [
  { id: 'c1', name: 'Soldagem TIG', maxScore: 100, weight: 1.5 },
  { id: 'c2', name: 'Soldagem MIG/MAG', maxScore: 100, weight: 1.5 },
  { id: 'c3', name: 'Leitura de Desenho', maxScore: 100, weight: 1.0 },
  { id: 'c4', name: 'Segurança do Trabalho', maxScore: 100, weight: 0.5 },
  { id: 'c5', name: 'Qualidade de Acabamento', maxScore: 100, weight: 1.5 },
];

export const GradeEntryForm: React.FC<GradeEntryFormProps> = ({
  simuladoId,
  simuladoName: _simuladoName,
  onSubmit,
  onCancel,
}) => {
  const [grades, setGrades] = useState<Record<string, Record<string, number>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleScoreChange = (competitorId: string, competenceId: string, value: string) => {
    const score = parseFloat(value);
    if (isNaN(score) && value !== '') return;

    setGrades(prev => ({
      ...prev,
      [competitorId]: {
        ...prev[competitorId],
        [competenceId]: value === '' ? 0 : score,
      },
    }));
  };

  const getScore = (competitorId: string, competenceId: string): string => {
    const score = grades[competitorId]?.[competenceId];
    return score !== undefined ? score.toString() : '';
  };

  const calculateAverage = (competitorId: string): number => {
    const competitorGrades = grades[competitorId];
    if (!competitorGrades) return 0;

    let totalWeight = 0;
    let weightedSum = 0;

    mockCompetences.forEach(comp => {
      const score = competitorGrades[comp.id];
      if (score !== undefined) {
        weightedSum += score * comp.weight;
        totalWeight += comp.weight;
      }
    });

    return totalWeight > 0 ? weightedSum / totalWeight : 0;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    const gradeEntries: GradeEntry[] = [];
    Object.entries(grades).forEach(([competitorId, competences]) => {
      Object.entries(competences).forEach(([competenceId, score]) => {
        if (score > 0) {
          gradeEntries.push({ competitorId, competenceId, score });
        }
      });
    });

    await onSubmit({ simuladoId, grades: gradeEntries });
    setIsSubmitting(false);
  };

  const getScoreVariant = (score: number): 'success' | 'warning' | 'danger' => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  return (
    <div className="space-y-6">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider sticky left-0 bg-gray-50 dark:bg-gray-800 z-10">
                Competidor
              </th>
              {mockCompetences.map(comp => (
                <th
                  key={comp.id}
                  className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                >
                  <div>{comp.name}</div>
                  <div className="text-gray-400 font-normal">Peso: {comp.weight}</div>
                </th>
              ))}
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Média
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            {mockCompetitors.map(competitor => {
              const average = calculateAverage(competitor.id);
              return (
                <tr key={competitor.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-4 py-3 whitespace-nowrap sticky left-0 bg-white dark:bg-gray-900 z-10">
                    <div className="flex items-center">
                      <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium mr-3">
                        {competitor.name.charAt(0)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {competitor.name}
                        </div>
                        {competitor.currentScore !== undefined && (
                          <div className="text-xs text-gray-500">
                            Anterior: {competitor.currentScore}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  {mockCompetences.map(comp => (
                    <td key={comp.id} className="px-4 py-3">
                      <input
                        type="number"
                        min="0"
                        max={comp.maxScore}
                        step="0.1"
                        value={getScore(competitor.id, comp.id)}
                        onChange={(e) => handleScoreChange(competitor.id, comp.id, e.target.value)}
                        className="w-20 px-2 py-1 text-center border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="-"
                      />
                    </td>
                  ))}
                  <td className="px-4 py-3 text-center">
                    {average > 0 ? (
                      <Badge variant={getScoreVariant(average)} size="lg">
                        {average.toFixed(1)}
                      </Badge>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Preencha as notas de cada competidor por competência
        </div>
        <div className="flex space-x-3">
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} isLoading={isSubmitting}>
            Salvar Notas
          </Button>
        </div>
      </div>
    </div>
  );
};
