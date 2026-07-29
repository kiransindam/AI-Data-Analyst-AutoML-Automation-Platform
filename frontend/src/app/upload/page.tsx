// frontend/src/app/upload/page.tsx
'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, FileJson, Database, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '@/services/api';
import { useStore } from '@/store/useStore';
import toast from 'react-hot-toast';

const ACCEPTED_TYPES = {
  'text/csv': ['.csv'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/json': ['.json'],
  'application/octet-stream': ['.parquet'],
};

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<any>(null);
  const { setDatasets } = useStore();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await api.uploadFile(file, `Uploaded on ${new Date().toLocaleDateString()}`);
      setUploadedFile(response.data);
      toast.success(`"${file.name}" uploaded successfully!`);

      // Refresh dataset list
      const { data: datasets } = await api.listDatasets();
      setDatasets(datasets);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: 500 * 1024 * 1024, // 500MB
    multiple: false,
  });

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Dataset</h1>
        <p className="text-gray-600 mb-8">
          Upload your data and let AI analyze it automatically.
        </p>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer
            transition-all duration-200
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
            ${isDragReject ? 'border-red-500 bg-red-50' : ''}
            ${uploading ? 'pointer-events-none opacity-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />

          {isDragActive ? (
            <p className="text-lg text-blue-600 font-medium">Drop your file here...</p>
          ) : (
            <>
              <p className="text-lg text-gray-700 font-medium mb-2">
                Drag & drop your dataset here, or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports CSV, Excel, JSON, Parquet (max 500MB)
              </p>
            </>
          )}
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="mt-6 bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full" />
              <span className="text-gray-700">Uploading and processing...</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Upload Success */}
        {uploadedFile && (
          <div className="mt-6 bg-white rounded-xl p-6 shadow-sm border border-green-200">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="h-6 w-6 text-green-500" />
              <h3 className="text-lg font-semibold text-gray-900">Upload Successful</h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <InfoCard label="Filename" value={uploadedFile.filename} />
              <InfoCard label="Type" value={uploadedFile.file_type?.toUpperCase()} />
              <InfoCard label="Rows" value={uploadedFile.row_count?.toLocaleString()} />
              <InfoCard label="Columns" value={uploadedFile.col_count} />
            </div>

            <div className="mt-6 flex gap-4">
              <a
                href={`/analysis/new?dataset=${uploadedFile.id}`}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Start Analysis →
              </a>
              <button
                onClick={() => setUploadedFile(null)}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
              >
                Upload Another
              </button>
            </div>
          </div>
        )}

        {/* Supported Formats */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
          <FormatCard icon={<FileSpreadsheet />} label="CSV" desc="Comma-separated" />
          <FormatCard icon={<FileSpreadsheet />} label="Excel" desc=".xlsx / .xls" />
          <FormatCard icon={<FileJson />} label="JSON" desc="Structured data" />
          <FormatCard icon={<Database />} label="Parquet" desc="Columnar format" />
        </div>
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: any }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-500 uppercase">{label}</p>
      <p className="text-sm font-semibold text-gray-900 mt-1">{value || 'N/A'}</p>
    </div>
  );
}

function FormatCard({ icon, label, desc }: { icon: React.ReactNode; label: string; desc: string }) {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
      <div className="text-blue-500 flex justify-center mb-2">{icon}</div>
      <p className="font-medium text-gray-900">{label}</p>
      <p className="text-xs text-gray-500">{desc}</p>
    </div>
  );
}
