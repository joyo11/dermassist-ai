"use client";

import { useState, useCallback, useRef } from "react";
import { DisclaimerBanner } from "@/components/disclaimer-banner";
import { Hero } from "@/components/hero";
import { ImageUpload } from "@/components/image-upload";
import { ResultsCard, type AnalysisResult } from "@/components/results-card";
import { HowItWorks } from "@/components/how-it-works";
import { TechStack } from "@/components/tech-stack";
import { Roadmap } from "@/components/roadmap";
import { Footer } from "@/components/footer";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  process.env.VITE_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const uploadRef = useRef<HTMLDivElement>(null);
  const howItWorksRef = useRef<HTMLDivElement>(null);

  const handleUploadClick = useCallback(() => {
    uploadRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const handleHowItWorksClick = useCallback(() => {
    howItWorksRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const handleAnalyze = useCallback(async (imageFile: File) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisError(null);

    try {
      const formData = new FormData();
      formData.append("file", imageFile);
      formData.append("include_gradcam", "true");

      const res = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const message = await res.text().catch(() => "");
        throw new Error(
          message?.trim()
            ? `Backend error (${res.status}): ${message}`
            : `Backend error (${res.status}).`
        );
      }

      const data = (await res.json()) as AnalysisResult;
      setAnalysisResult(data);
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing the image.";
      setAnalysisError(
        `${msg} If the backend isn’t running, start it on http://localhost:8000.`
      );
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Hero Section */}
      <Hero
        onUploadClick={handleUploadClick}
        onHowItWorksClick={handleHowItWorksClick}
      />

      {/* Image Upload Section */}
      <div ref={uploadRef}>
        <ImageUpload onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
      </div>

      {/* Error Section - shown if analysis failed */}
      {analysisError && (
        <section className="bg-muted/30 py-10">
          <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
            <div className="rounded-2xl border border-destructive/30 bg-card p-5 sm:p-6 shadow-sm">
              <p className="text-sm font-medium text-foreground">
                Unable to analyze image
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                {analysisError}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Results Section - shown after analysis */}
      {analysisResult && <ResultsCard result={analysisResult} />}

      {/* How It Works Section */}
      <div ref={howItWorksRef}>
        <HowItWorks />
      </div>

      {/* Technology Stack Section */}
      <TechStack />

      {/* Research Roadmap Section */}
      <Roadmap />

      {/* Footer */}
      <Footer />
    </div>
  );
}
