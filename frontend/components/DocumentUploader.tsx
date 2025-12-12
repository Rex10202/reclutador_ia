// components/DocumentUploader.tsx
'use client';

import { useCallback, useState } from 'react';
import { Upload, FileText, X, AlertCircle, CheckCircle2 } from 'lucide-react';
import { UploadedDocument } from '@/lib/types';

interface DocumentUploaderProps {
  documents: UploadedDocument[];
  onDocumentsChange: (documents: UploadedDocument[]) => void;
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
  minFiles?: number;
  disabled?: boolean;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_TYPES = ['application/pdf'];

export function DocumentUploader({
  documents,
  onDocumentsChange,
  onFilesSelected,
  maxFiles = 10,
  minFiles = 2,
  disabled = false,
}: DocumentUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFiles = useCallback((files: File[]): { valid: File[]; errors: string[] } => {
    const valid: File[] = [];
    const errors: string[] = [];

    for (const file of files) {
      if (!ACCEPTED_TYPES.includes(file.type)) {
        errors.push(`"${file.name}" no es un archivo PDF válido`);
        continue;
      }
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`"${file.name}" excede el tamaño máximo de 10MB`);
        continue;
      }
      valid.push(file);
    }

    const totalFiles = documents.length + valid.length;
    if (totalFiles > maxFiles) {
      errors.push(`Máximo ${maxFiles} archivos permitidos`);
      valid.splice(maxFiles - documents.length);
    }

    return { valid, errors };
  }, [documents.length, maxFiles]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    const { valid, errors } = validateFiles(files);
    
    if (errors.length > 0) {
      setError(errors.join('. '));
      setTimeout(() => setError(null), 5000);
    }
    
    if (valid.length > 0) {
      onFilesSelected(valid);
    }
  }, [disabled, validateFiles, onFilesSelected]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    const { valid, errors } = validateFiles(files);
    
    if (errors.length > 0) {
      setError(errors.join('. '));
      setTimeout(() => setError(null), 5000);
    }
    
    if (valid.length > 0) {
      onFilesSelected(valid);
    }
    
    // Reset input
    e.target.value = '';
  }, [validateFiles, onFilesSelected]);

  const removeDocument = useCallback((documentId: string) => {
    onDocumentsChange(documents.filter(d => d.id !== documentId));
  }, [documents, onDocumentsChange]);

  const getStatusIcon = (status: UploadedDocument['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'ready':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusText = (status: UploadedDocument['status']) => {
    switch (status) {
      case 'uploading': return 'Subiendo...';
      case 'processing': return 'Procesando...';
      case 'ready': return 'Listo';
      case 'error': return 'Error';
    }
  };

  const canAddMore = documents.length < maxFiles;
  const hasMinimum = documents.filter(d => d.status === 'ready').length >= minFiles;

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
          ${isDragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileInput}
          disabled={disabled || !canAddMore}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />
        
        <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} />
        
        <p className="text-lg font-medium text-gray-700 mb-1">
          {isDragging ? 'Suelta los archivos aquí' : 'Arrastra y suelta tus hojas de vida'}
        </p>
        <p className="text-sm text-gray-500 mb-3">
          o haz clic para seleccionar archivos
        </p>
        <p className="text-xs text-gray-400">
          PDF únicamente • Máximo 10MB por archivo • {minFiles} a {maxFiles} archivos
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Validation Status */}
      {documents.length > 0 && !hasMinimum && (
        <div className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>Sube al menos {minFiles} hojas de vida para iniciar el análisis</span>
        </div>
      )}

      {/* Document List */}
      {documents.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">
            Documentos cargados ({documents.length}/{maxFiles})
          </p>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className={`
                  flex items-center gap-3 p-3 rounded-lg border transition-colors
                  ${doc.status === 'error' 
                    ? 'bg-red-50 border-red-200' 
                    : 'bg-white border-gray-200 hover:border-blue-300'
                  }
                `}
              >
                <FileText className={`w-5 h-5 flex-shrink-0 ${doc.status === 'error' ? 'text-red-500' : 'text-blue-500'}`} />
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.fileName}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(doc.fileSize / 1024).toFixed(1)} KB • {getStatusText(doc.status)}
                    {doc.errorMessage && ` - ${doc.errorMessage}`}
                  </p>
                </div>
                
                <div className="flex items-center gap-2">
                  {getStatusIcon(doc.status)}
                  <button
                    onClick={() => removeDocument(doc.id)}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                    title="Eliminar"
                  >
                    <X className="w-4 h-4 text-gray-400 hover:text-red-500" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
