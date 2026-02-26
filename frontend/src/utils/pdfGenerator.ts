/**
 * PDF Generator utility using jsPDF.
 * Creates styled PDF reports with a consistent header (logo, title, date/time).
 */
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

// Extend jsPDF type for autotable
declare module 'jspdf' {
  interface jsPDF {
    lastAutoTable: { finalY: number };
  }
}

export interface PDFHeaderOptions {
  title: string;
  subtitle?: string;
  logoUrl?: string | null;
  platformName?: string;
}

export interface TableColumn {
  header: string;
  dataKey: string;
  width?: number;
}

export interface TableRow {
  [key: string]: string | number;
}

const COLORS = {
  headerBg: [0, 51, 102] as [number, number, number],      // Dark blue
  headerText: [255, 255, 255] as [number, number, number],  // White
  accent: [0, 102, 204] as [number, number, number],        // Blue accent
  tableHeader: [0, 51, 102] as [number, number, number],    // Dark blue
  tableHeaderText: [255, 255, 255] as [number, number, number],
  tableStripe: [240, 245, 255] as [number, number, number], // Light blue stripe
  textDark: [33, 33, 33] as [number, number, number],
  textMuted: [120, 120, 120] as [number, number, number],
  border: [200, 200, 200] as [number, number, number],
};

/**
 * Load an image from URL and return as base64 data URL.
 */
async function loadImageAsBase64(url: string): Promise<{ data: string; width: number; height: number } | null> {
  try {
    const response = await fetch(url);
    const blob = await response.blob();
    const dataUrl: string = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = () => reject();
      reader.readAsDataURL(blob);
    });

    // Load into an Image to get natural dimensions
    const dims: { width: number; height: number } = await new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve({ width: img.naturalWidth, height: img.naturalHeight });
      img.onerror = () => resolve({ width: 1, height: 1 });
      img.src = dataUrl;
    });

    return { data: dataUrl, width: dims.width, height: dims.height };
  } catch {
    return null;
  }
}

/**
 * Format a date to Brazilian format.
 */
function formatDateTime(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('pt-BR');
}

/**
 * Create a new PDF document with the styled header.
 */
export async function createPDF(options: PDFHeaderOptions): Promise<jsPDF> {
  const doc = new jsPDF('portrait', 'mm', 'a4');
  const pageWidth = doc.internal.pageSize.getWidth();
  const now = new Date();

  // Draw header background
  doc.setFillColor(...COLORS.headerBg);
  doc.rect(0, 0, pageWidth, 38, 'F');

  // Draw accent line below header
  doc.setFillColor(...COLORS.accent);
  doc.rect(0, 38, pageWidth, 1.5, 'F');

  // Add logo if available
  const headerHeight = 38;
  const maxLogoHeight = 30;
  const maxLogoWidth = 36;
  let logoEndX = 8; // fallback if no logo
  if (options.logoUrl) {
    const logoImg = await loadImageAsBase64(options.logoUrl);
    if (logoImg) {
      try {
        const aspect = logoImg.width / logoImg.height;
        let logoW = maxLogoHeight * aspect;
        let logoH = maxLogoHeight;
        if (logoW > maxLogoWidth) {
          logoW = maxLogoWidth;
          logoH = maxLogoWidth / aspect;
        }
        const logoY = (headerHeight - logoH) / 2;
        doc.addImage(logoImg.data, 'PNG', 8, logoY, logoW, logoH);
        logoEndX = 8 + logoW;
      } catch {
        // Logo failed to load, skip it
      }
    }
  }

  // Text area starts after logo and is centered in remaining space
  const textStartX = logoEndX + 6;
  const textAreaWidth = pageWidth - textStartX - 10;
  const textCenterX = textStartX + textAreaWidth / 2;

  // Platform name (centered)
  doc.setTextColor(...COLORS.headerText);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text(options.platformName || 'SPSkills', textCenterX, 10, { align: 'center' });

  // Report title (centered)
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text(options.title.toUpperCase(), textCenterX, 20, { align: 'center' });

  // Subtitle (centered)
  if (options.subtitle) {
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(options.subtitle, textCenterX, 27, { align: 'center' });
  }

  // Date/time (centered)
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  const dateText = `Gerado em: ${formatDateTime(now)}`;
  doc.text(dateText, textCenterX, 34, { align: 'center' });

  return doc;
}

/**
 * Add a section title to the PDF.
 */
export function addSectionTitle(doc: jsPDF, title: string, y: number): number {
  const pageWidth = doc.internal.pageSize.getWidth();

  doc.setFillColor(...COLORS.accent);
  doc.rect(10, y, pageWidth - 20, 8, 'F');

  doc.setTextColor(...COLORS.headerText);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.text(title, 14, y + 5.5);

  return y + 12;
}

/**
 * Add a key-value info block.
 */
export function addInfoBlock(
  doc: jsPDF,
  items: Array<{ label: string; value: string | number }>,
  y: number,
  columns: number = 2
): number {
  const pageWidth = doc.internal.pageSize.getWidth();
  const usableWidth = pageWidth - 20;
  const colWidth = usableWidth / columns;
  let currentY = y;
  let col = 0;

  for (const item of items) {
    const x = 10 + col * colWidth;

    doc.setTextColor(...COLORS.textMuted);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.text(item.label, x, currentY);

    doc.setTextColor(...COLORS.textDark);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text(String(item.value), x, currentY + 5);

    col++;
    if (col >= columns) {
      col = 0;
      currentY += 12;
    }
  }

  if (col > 0) currentY += 12;
  return currentY;
}

/**
 * Add a table to the PDF.
 */
export function addTable(
  doc: jsPDF,
  columns: TableColumn[],
  rows: TableRow[],
  startY: number
): number {
  const pagePadding = 10;
  const pageWidth = doc.internal.pageSize.getWidth();
  const fullTableWidth = pageWidth - 2 * pagePadding;

  autoTable(doc, {
    startY,
    head: [columns.map((c) => c.header)],
    body: rows.map((row) => columns.map((c) => String(row[c.dataKey] ?? ''))),
    margin: { left: pagePadding, right: pagePadding },
    tableWidth: fullTableWidth,
    styles: {
      fontSize: 8,
      cellPadding: 2.5,
      textColor: COLORS.textDark,
      lineColor: COLORS.border,
      lineWidth: 0.1,
      halign: 'center',
    },
    headStyles: {
      fillColor: COLORS.tableHeader,
      textColor: COLORS.tableHeaderText,
      fontStyle: 'bold',
      fontSize: 8,
      halign: 'center',
    },
    alternateRowStyles: {
      fillColor: COLORS.tableStripe,
    },
  });

  return doc.lastAutoTable.finalY + 5;
}

/**
 * Add a simple horizontal bar chart to the PDF.
 */
export function addBarChart(
  doc: jsPDF,
  data: Array<{ label: string; value: number; color?: [number, number, number] }>,
  startY: number,
  maxValue?: number
): number {
  const pageWidth = doc.internal.pageSize.getWidth();
  const barHeight = 8;
  const labelWidth = 50;
  const barAreaWidth = pageWidth - 20 - labelWidth - 30;
  const max = maxValue || Math.max(...data.map((d) => d.value), 1);
  let y = startY;

  for (const item of data) {
    // Label
    doc.setTextColor(...COLORS.textDark);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.text(item.label, 10, y + 5);

    // Bar background
    doc.setFillColor(230, 230, 230);
    doc.rect(10 + labelWidth, y, barAreaWidth, barHeight, 'F');

    // Bar value
    const barWidth = (item.value / max) * barAreaWidth;
    doc.setFillColor(...(item.color || COLORS.accent));
    doc.rect(10 + labelWidth, y, barWidth, barHeight, 'F');

    // Value text
    doc.setTextColor(...COLORS.textDark);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text(
      String(typeof item.value === 'number' ? item.value.toFixed(1) : item.value),
      10 + labelWidth + barAreaWidth + 2,
      y + 5
    );

    y += barHeight + 3;
  }

  return y + 5;
}

/**
 * Add footer with page numbers.
 */
export function addFooter(doc: jsPDF): void {
  const pageCount = doc.getNumberOfPages();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);

    // Footer line
    doc.setDrawColor(...COLORS.border);
    doc.setLineWidth(0.3);
    doc.line(10, pageHeight - 15, pageWidth - 10, pageHeight - 15);

    // Page number
    doc.setTextColor(...COLORS.textMuted);
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.text(`Página ${i} de ${pageCount}`, pageWidth / 2, pageHeight - 10, {
      align: 'center',
    });

    // Confidential note
    doc.text('Documento gerado automaticamente - SPSkills', 10, pageHeight - 10);
  }
}

/**
 * Check if we need a new page and add one if needed.
 */
export function checkPageBreak(doc: jsPDF, currentY: number, neededSpace: number = 40): number {
  const pageHeight = doc.internal.pageSize.getHeight();
  if (currentY + neededSpace > pageHeight - 20) {
    doc.addPage();
    return 15;
  }
  return currentY;
}

/**
 * Save the PDF with footer and download it.
 */
export function savePDF(doc: jsPDF, filename: string): void {
  addFooter(doc);
  doc.save(filename);
}

// =====================================================================
// Report generators
// =====================================================================

export interface CompetitorReportData {
  competitor_name: string;
  modality_name?: string;
  trainings: Array<{
    date: string;
    hours: number;
    type: string;
    location?: string;
    status: string;
    description?: string;
  }>;
  totalHours: number;
  senaiHours: number;
  externalHours: number;
  approvedHours: number;
  pendingHours: number;
  grades: Array<{
    exam_name: string;
    competence_name: string;
    score: number;
    date: string;
  }>;
  averageGrade: number;
}

export async function generateCompetitorReport(
  data: CompetitorReportData,
  headerOptions: PDFHeaderOptions
): Promise<void> {
  const doc = await createPDF({
    ...headerOptions,
    title: 'Relatório por Competidor',
    subtitle: `Competidor: ${data.competitor_name}${data.modality_name ? ` | Modalidade: ${data.modality_name}` : ''}`,
  });

  let y = 45;

  // Summary section
  y = addSectionTitle(doc, 'RESUMO DO COMPETIDOR', y);
  y = addInfoBlock(doc, [
    { label: 'Competidor', value: data.competitor_name },
    { label: 'Modalidade', value: data.modality_name || 'Todas' },
    { label: 'Total de Horas', value: `${data.totalHours.toFixed(1)}h` },
    { label: 'Horas Aprovadas', value: `${data.approvedHours.toFixed(1)}h` },
    { label: 'Horas SENAI', value: `${data.senaiHours.toFixed(1)}h` },
    { label: 'Horas Externo', value: `${data.externalHours.toFixed(1)}h` },
    { label: 'Horas Pendentes', value: `${data.pendingHours.toFixed(1)}h` },
    { label: 'Média das Notas', value: data.averageGrade > 0 ? data.averageGrade.toFixed(1) : 'N/A' },
  ], y);

  // Training hours chart
  y = checkPageBreak(doc, y, 50);
  y = addSectionTitle(doc, 'DISTRIBUIÇÃO DE HORAS DE TREINAMENTO', y);
  y = addBarChart(doc, [
    { label: 'SENAI', value: data.senaiHours, color: [0, 102, 204] },
    { label: 'Externo', value: data.externalHours, color: [255, 153, 0] },
    { label: 'Aprovadas', value: data.approvedHours, color: [0, 153, 76] },
    { label: 'Pendentes', value: data.pendingHours, color: [255, 204, 0] },
  ], y, data.totalHours || 1);

  // Trainings table
  if (data.trainings.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'TREINAMENTOS REGISTRADOS', y);

    const typeLabels: Record<string, string> = {
      senai: 'SENAI',
      external: 'Externo',
      empresa: 'Empresa',
      autonomo: 'Autônomo',
    };
    const statusLabels: Record<string, string> = {
      pending: 'Pendente',
      approved: 'Aprovado',
      rejected: 'Rejeitado',
      validated: 'Validado',
    };

    y = addTable(
      doc,
      [
        { header: 'Data', dataKey: 'date', width: 22 },
        { header: 'Horas', dataKey: 'hours', width: 15 },
        { header: 'Tipo', dataKey: 'type', width: 22 },
        { header: 'Local', dataKey: 'location', width: 45 },
        { header: 'Status', dataKey: 'status', width: 22 },
      ],
      data.trainings.map((t) => ({
        date: formatDate(t.date),
        hours: t.hours.toFixed(1),
        type: typeLabels[t.type] || t.type,
        location: t.location || '-',
        status: statusLabels[t.status] || t.status,
      })),
      y
    );
  }

  // Grades table
  if (data.grades.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'NOTAS DE AVALIAÇÕES', y);
    y = addTable(
      doc,
      [
        { header: 'Avaliação', dataKey: 'exam_name', width: 50 },
        { header: 'Competência', dataKey: 'competence_name', width: 50 },
        { header: 'Nota', dataKey: 'score', width: 20 },
        { header: 'Data', dataKey: 'date', width: 25 },
      ],
      data.grades.map((g) => ({
        exam_name: g.exam_name,
        competence_name: g.competence_name,
        score: g.score.toFixed(1),
        date: formatDate(g.date),
      })),
      y
    );
  }

  savePDF(doc, `relatorio_competidor_${data.competitor_name.replace(/\s+/g, '_')}.pdf`);
}

export interface ModalityReportData {
  modality_name: string;
  modality_code: string;
  totalCompetitors: number;
  totalExams: number;
  averageGrade: number;
  totalTrainingHours: number;
  competitors: Array<{
    name: string;
    trainingHours: number;
    averageGrade: number;
    status: string;
  }>;
}

export async function generateModalityReport(
  data: ModalityReportData,
  headerOptions: PDFHeaderOptions
): Promise<void> {
  const doc = await createPDF({
    ...headerOptions,
    title: 'Relatório por Modalidade',
    subtitle: `Modalidade: ${data.modality_name} (${data.modality_code})`,
  });

  let y = 45;

  // Summary
  y = addSectionTitle(doc, 'RESUMO DA MODALIDADE', y);
  y = addInfoBlock(doc, [
    { label: 'Modalidade', value: `${data.modality_name} (${data.modality_code})` },
    { label: 'Total de Competidores', value: data.totalCompetitors },
    { label: 'Total de Avaliações', value: data.totalExams },
    { label: 'Média Geral das Notas', value: data.averageGrade > 0 ? data.averageGrade.toFixed(1) : 'N/A' },
    { label: 'Total Horas Treinamento', value: `${data.totalTrainingHours.toFixed(1)}h` },
  ], y);

  // Competitors table
  if (data.competitors.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'COMPETIDORES', y);
    y = addTable(
      doc,
      [
        { header: '#', dataKey: 'pos', width: 10 },
        { header: 'Competidor', dataKey: 'name', width: 60 },
        { header: 'Horas Treino', dataKey: 'hours', width: 25 },
        { header: 'Média Notas', dataKey: 'grade', width: 25 },
        { header: 'Status', dataKey: 'status', width: 25 },
      ],
      data.competitors.map((c, i) => ({
        pos: i + 1,
        name: c.name,
        hours: c.trainingHours.toFixed(1),
        grade: c.averageGrade > 0 ? c.averageGrade.toFixed(1) : 'N/A',
        status: c.status === 'active' ? 'Ativo' : 'Inativo',
      })),
      y
    );

    // Bar chart of hours
    y = checkPageBreak(doc, y, 60);
    y = addSectionTitle(doc, 'HORAS DE TREINAMENTO POR COMPETIDOR', y);
    y = addBarChart(
      doc,
      data.competitors
        .sort((a, b) => b.trainingHours - a.trainingHours)
        .slice(0, 15)
        .map((c) => ({
          label: c.name.length > 20 ? c.name.substring(0, 20) + '...' : c.name,
          value: c.trainingHours,
        })),
      y
    );
  }

  savePDF(doc, `relatorio_modalidade_${data.modality_code}.pdf`);
}

export interface AttendanceReportData {
  modality_name?: string;
  filterType: 'senai' | 'external' | 'all';
  startDate?: string;
  endDate?: string;
  trainings: Array<{
    competitor_name: string;
    date: string;
    hours: number;
    type: string;
    location?: string;
    status: string;
  }>;
  totalHours: number;
  totalSessions: number;
  byCompetitor: Array<{
    name: string;
    sessions: number;
    hours: number;
  }>;
}

export async function generateAttendanceReport(
  data: AttendanceReportData,
  headerOptions: PDFHeaderOptions
): Promise<void> {
  const filterLabels: Record<string, string> = {
    senai: 'SENAI',
    external: 'Externo',
    all: 'Todos',
  };

  const doc = await createPDF({
    ...headerOptions,
    title: 'Relatório de Presença',
    subtitle: `Tipo: ${filterLabels[data.filterType]}${data.modality_name ? ` | Modalidade: ${data.modality_name}` : ''}${data.startDate ? ` | Período: ${formatDate(data.startDate)} a ${formatDate(data.endDate || data.startDate)}` : ''}`,
  });

  let y = 45;

  // Summary
  y = addSectionTitle(doc, 'RESUMO DE PRESENÇA', y);
  y = addInfoBlock(doc, [
    { label: 'Total de Sessões', value: data.totalSessions },
    { label: 'Total de Horas', value: `${data.totalHours.toFixed(1)}h` },
    { label: 'Tipo Filtrado', value: filterLabels[data.filterType] },
    { label: 'Competidores Envolvidos', value: data.byCompetitor.length },
  ], y);

  // By competitor summary
  if (data.byCompetitor.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'RESUMO POR COMPETIDOR', y);
    y = addTable(
      doc,
      [
        { header: 'Competidor', dataKey: 'name', width: 70 },
        { header: 'Sessões', dataKey: 'sessions', width: 25 },
        { header: 'Horas', dataKey: 'hours', width: 25 },
      ],
      data.byCompetitor
        .sort((a, b) => b.hours - a.hours)
        .map((c) => ({
          name: c.name,
          sessions: c.sessions,
          hours: c.hours.toFixed(1),
        })),
      y
    );
  }

  // Detailed sessions
  if (data.trainings.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'DETALHAMENTO DE SESSÕES', y);

    const typeLabels: Record<string, string> = {
      senai: 'SENAI',
      external: 'Externo',
      empresa: 'Empresa',
      autonomo: 'Autônomo',
    };
    const statusLabels: Record<string, string> = {
      pending: 'Pendente',
      approved: 'Aprovado',
      rejected: 'Rejeitado',
      validated: 'Validado',
    };

    y = addTable(
      doc,
      [
        { header: 'Competidor', dataKey: 'competitor', width: 40 },
        { header: 'Data', dataKey: 'date', width: 22 },
        { header: 'Horas', dataKey: 'hours', width: 15 },
        { header: 'Tipo', dataKey: 'type', width: 20 },
        { header: 'Local', dataKey: 'location', width: 35 },
        { header: 'Status', dataKey: 'status', width: 20 },
      ],
      data.trainings.map((t) => ({
        competitor: t.competitor_name,
        date: formatDate(t.date),
        hours: t.hours.toFixed(1),
        type: typeLabels[t.type] || t.type,
        location: t.location || '-',
        status: statusLabels[t.status] || t.status,
      })),
      y
    );
  }

  savePDF(doc, `relatorio_presenca_${data.filterType}.pdf`);
}

export interface RankingReportData {
  modality_name: string;
  modality_code: string;
  entries: Array<{
    position: number;
    competitor_name: string;
    averageGrade: number;
    trainingHours: number;
  }>;
}

export async function generateRankingReport(
  data: RankingReportData,
  headerOptions: PDFHeaderOptions
): Promise<void> {
  const doc = await createPDF({
    ...headerOptions,
    title: 'Relatório de Ranking',
    subtitle: `Modalidade: ${data.modality_name} (${data.modality_code})`,
  });

  let y = 45;

  y = addSectionTitle(doc, 'RANKING DE COMPETIDORES', y);

  if (data.entries.length > 0) {
    y = addTable(
      doc,
      [
        { header: 'Posição', dataKey: 'position', width: 18 },
        { header: 'Competidor', dataKey: 'name', width: 65 },
        { header: 'Média Notas', dataKey: 'grade', width: 25 },
        { header: 'Horas Treino', dataKey: 'hours', width: 25 },
      ],
      data.entries.map((e) => ({
        position: `${e.position}º`,
        name: e.competitor_name,
        grade: e.averageGrade > 0 ? e.averageGrade.toFixed(1) : 'N/A',
        hours: e.trainingHours.toFixed(1),
      })),
      y
    );

    // Chart
    y = checkPageBreak(doc, y, 60);
    y = addSectionTitle(doc, 'MÉDIAS POR COMPETIDOR', y);
    y = addBarChart(
      doc,
      data.entries.slice(0, 15).map((e) => ({
        label: e.competitor_name.length > 20 ? e.competitor_name.substring(0, 20) + '...' : e.competitor_name,
        value: e.averageGrade,
        color: e.position <= 3 ? [0, 153, 76] : [0, 102, 204],
      })),
      y,
      100
    );
  }

  savePDF(doc, `relatorio_ranking_${data.modality_code}.pdf`);
}

export interface TrainingHoursReportData {
  modality_name?: string;
  startDate?: string;
  endDate?: string;
  competitors: Array<{
    name: string;
    senaiHours: number;
    externalHours: number;
    totalHours: number;
    approvedHours: number;
    pendingHours: number;
    sessions: number;
  }>;
  totalSenai: number;
  totalExternal: number;
  totalHours: number;
}

export async function generateTrainingHoursReport(
  data: TrainingHoursReportData,
  headerOptions: PDFHeaderOptions
): Promise<void> {
  const doc = await createPDF({
    ...headerOptions,
    title: 'Relatório de Horas de Treinamento',
    subtitle: `${data.modality_name ? `Modalidade: ${data.modality_name}` : 'Todas as Modalidades'}${data.startDate ? ` | Período: ${formatDate(data.startDate)} a ${formatDate(data.endDate || data.startDate)}` : ''}`,
  });

  let y = 45;

  // Summary
  y = addSectionTitle(doc, 'RESUMO GERAL', y);
  y = addInfoBlock(doc, [
    { label: 'Total de Horas', value: `${data.totalHours.toFixed(1)}h` },
    { label: 'Horas SENAI', value: `${data.totalSenai.toFixed(1)}h` },
    { label: 'Horas Externo', value: `${data.totalExternal.toFixed(1)}h` },
    { label: 'Total de Competidores', value: data.competitors.length },
  ], y);

  // Distribution chart
  y = checkPageBreak(doc, y, 40);
  y = addSectionTitle(doc, 'DISTRIBUIÇÃO POR TIPO', y);
  y = addBarChart(doc, [
    { label: 'SENAI', value: data.totalSenai, color: [0, 102, 204] },
    { label: 'Externo', value: data.totalExternal, color: [255, 153, 0] },
  ], y, data.totalHours || 1);

  // Per competitor table
  if (data.competitors.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'DETALHAMENTO POR COMPETIDOR', y);
    y = addTable(
      doc,
      [
        { header: 'Competidor', dataKey: 'name', width: 45 },
        { header: 'SENAI', dataKey: 'senai', width: 18 },
        { header: 'Externo', dataKey: 'external', width: 18 },
        { header: 'Total', dataKey: 'total', width: 18 },
        { header: 'Aprovado', dataKey: 'approved', width: 18 },
        { header: 'Pendente', dataKey: 'pending', width: 18 },
        { header: 'Sessões', dataKey: 'sessions', width: 18 },
      ],
      data.competitors
        .sort((a, b) => b.totalHours - a.totalHours)
        .map((c) => ({
          name: c.name,
          senai: c.senaiHours.toFixed(1),
          external: c.externalHours.toFixed(1),
          total: c.totalHours.toFixed(1),
          approved: c.approvedHours.toFixed(1),
          pending: c.pendingHours.toFixed(1),
          sessions: c.sessions,
        })),
      y
    );
  }

  savePDF(doc, `relatorio_horas_treinamento.pdf`);
}

export interface GeneralReportData {
  modalities: Array<{
    name: string;
    code: string;
    competitorCount: number;
    examCount: number;
    averageGrade: number;
    totalTrainingHours: number;
  }>;
  totalCompetitors: number;
  totalModalities: number;
  totalExams: number;
  overallAverage: number;
}

export async function generateGeneralReport(
  data: GeneralReportData,
  headerOptions: PDFHeaderOptions
): Promise<void> {
  const doc = await createPDF({
    ...headerOptions,
    title: 'Relatório Geral',
    subtitle: 'Visão geral de todas as modalidades',
  });

  let y = 45;

  // Summary
  y = addSectionTitle(doc, 'RESUMO GERAL DA PLATAFORMA', y);
  y = addInfoBlock(doc, [
    { label: 'Total de Modalidades', value: data.totalModalities },
    { label: 'Total de Competidores', value: data.totalCompetitors },
    { label: 'Total de Avaliações', value: data.totalExams },
    { label: 'Média Geral', value: data.overallAverage > 0 ? data.overallAverage.toFixed(1) : 'N/A' },
  ], y);

  // Modalities table
  if (data.modalities.length > 0) {
    y = checkPageBreak(doc, y, 30);
    y = addSectionTitle(doc, 'MODALIDADES', y);
    y = addTable(
      doc,
      [
        { header: 'Modalidade', dataKey: 'name', width: 50 },
        { header: 'Código', dataKey: 'code', width: 20 },
        { header: 'Competidores', dataKey: 'competitors', width: 25 },
        { header: 'Avaliações', dataKey: 'exams', width: 22 },
        { header: 'Média', dataKey: 'grade', width: 20 },
        { header: 'Horas Treino', dataKey: 'hours', width: 25 },
      ],
      data.modalities.map((m) => ({
        name: m.name,
        code: m.code,
        competitors: m.competitorCount,
        exams: m.examCount,
        grade: m.averageGrade > 0 ? m.averageGrade.toFixed(1) : 'N/A',
        hours: m.totalTrainingHours.toFixed(1),
      })),
      y
    );

    // Chart
    y = checkPageBreak(doc, y, 60);
    y = addSectionTitle(doc, 'COMPETIDORES POR MODALIDADE', y);
    y = addBarChart(
      doc,
      data.modalities.map((m) => ({
        label: m.name.length > 20 ? m.name.substring(0, 20) + '...' : m.name,
        value: m.competitorCount,
      })),
      y
    );
  }

  savePDF(doc, 'relatorio_geral.pdf');
}
