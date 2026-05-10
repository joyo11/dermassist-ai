"use client";

import { useState, useCallback, useRef } from "react";
import { Upload, X, Image as ImageIcon, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ImageUploadProps {
  onAnalyze: (imageFile: File) => void;
  isAnalyzing: boolean;
}

export function ImageUpload({ onAnalyze, isAnalyzing }: ImageUploadProps) {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback((file: File) => {
    if (file && (file.type === "image/jpeg" || file.type === "image/png")) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );

  const handleClear = useCallback(() => {
    setSelectedImage(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, []);

  const handleAnalyzeClick = useCallback(() => {
    if (selectedImage) {
      onAnalyze(selectedImage);
    }
  }, [selectedImage, onAnalyze]);

  return (
    <section id="upload" className="bg-muted/30 py-16 sm:py-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold tracking-tight text-foreground">
            Upload Image for Analysis
          </h2>
          <p className="mt-4 text-muted-foreground">
            Upload a clear image of the skin lesion for AI-assisted risk
            screening
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-sm">
          {!preview ? (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-colors cursor-pointer",
                isDragging
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50 hover:bg-muted/50"
              )}
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <p className="text-lg font-medium text-foreground">
                Upload a skin lesion image
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                Drag and drop or click to browse
              </p>
              <p className="mt-4 text-xs text-muted-foreground">
                Accepted formats: JPG, PNG
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleInputChange}
                className="hidden"
              />
            </div>
          ) : (
            <div className="space-y-6">
              <div className="relative">
                <div className="aspect-video overflow-hidden rounded-xl bg-muted">
                  <img
                    src={preview}
                    alt="Preview of uploaded skin lesion"
                    className="h-full w-full object-contain"
                  />
                </div>
                <button
                  onClick={handleClear}
                  disabled={isAnalyzing}
                  className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-foreground/80 text-background transition-colors hover:bg-foreground disabled:opacity-50"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3">
                <div className="flex items-center gap-3">
                  <ImageIcon className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {selectedImage?.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {selectedImage &&
                        (selectedImage.size / 1024 / 1024).toFixed(2)}{" "}
                      MB
                    </p>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleAnalyzeClick}
                disabled={isAnalyzing}
                className="w-full"
                size="lg"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing image...
                  </>
                ) : (
                  "Analyze Image"
                )}
              </Button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
