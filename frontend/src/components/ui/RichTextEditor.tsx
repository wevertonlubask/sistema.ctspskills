import React, { useMemo } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { clsx } from 'clsx';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  className?: string;
  minHeight?: string;
}

export const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  placeholder = 'Digite aqui...',
  label,
  error,
  className,
  minHeight = '150px',
}) => {
  const modules = useMemo(
    () => ({
      toolbar: [
        ['bold', 'italic', 'underline', 'strike'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link'],
        ['clean'],
      ],
    }),
    []
  );

  const formats = ['bold', 'italic', 'underline', 'strike', 'list', 'bullet', 'link'];

  return (
    <div className={clsx('rich-text-editor', className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
        </label>
      )}
      <div
        className={clsx(
          'rounded-lg border bg-white dark:bg-gray-700',
          error
            ? 'border-red-500 dark:border-red-400'
            : 'border-gray-300 dark:border-gray-600'
        )}
      >
        <ReactQuill
          theme="snow"
          value={value || ''}
          onChange={onChange}
          placeholder={placeholder}
          modules={modules}
          formats={formats}
          style={{ minHeight }}
        />
      </div>
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}

      <style>{`
        .rich-text-editor .ql-container {
          font-family: inherit;
          font-size: 0.875rem;
          min-height: ${minHeight};
        }
        .rich-text-editor .ql-editor {
          min-height: ${minHeight};
        }
        .rich-text-editor .ql-editor.ql-blank::before {
          color: #9ca3af;
          font-style: normal;
        }
        .dark .rich-text-editor .ql-toolbar {
          background-color: #374151;
          border-color: #4b5563;
        }
        .dark .rich-text-editor .ql-container {
          border-color: #4b5563;
        }
        .dark .rich-text-editor .ql-editor {
          color: #f3f4f6;
        }
        .dark .rich-text-editor .ql-editor.ql-blank::before {
          color: #6b7280;
        }
        .dark .rich-text-editor .ql-stroke {
          stroke: #9ca3af;
        }
        .dark .rich-text-editor .ql-fill {
          fill: #9ca3af;
        }
        .dark .rich-text-editor .ql-picker-label {
          color: #9ca3af;
        }
        .dark .rich-text-editor .ql-picker-options {
          background-color: #374151;
          border-color: #4b5563;
        }
        .dark .rich-text-editor .ql-picker-item {
          color: #f3f4f6;
        }
        .rich-text-editor .ql-toolbar {
          border-top-left-radius: 0.5rem;
          border-top-right-radius: 0.5rem;
          border-bottom: 1px solid;
        }
        .rich-text-editor .ql-container {
          border-bottom-left-radius: 0.5rem;
          border-bottom-right-radius: 0.5rem;
          border-top: none;
        }
      `}</style>
    </div>
  );
};

interface RichTextDisplayProps {
  content: string;
  className?: string;
}

export const RichTextDisplay: React.FC<RichTextDisplayProps> = ({ content, className }) => {
  if (!content) return null;

  return (
    <div
      className={clsx(
        'rich-text-display prose prose-sm dark:prose-invert max-w-none',
        'text-gray-700 dark:text-gray-300',
        className
      )}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
};
