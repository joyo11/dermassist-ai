"use client";

import { Upload, Sparkles, FileCheck, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeroProps {
  onUploadClick: () => void;
  onHowItWorksClick: () => void;
}

export function Hero({ onUploadClick, onHowItWorksClick }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-background py-20 sm:py-28">
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-1/4 top-0 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute right-1/4 bottom-0 h-96 w-96 rounded-full bg-accent/5 blur-3xl" />
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          {/* Left Content */}
          <div className="text-center lg:text-left">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-secondary px-4 py-1.5 text-sm text-secondary-foreground">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
              </span>
              Research Prototype • Not a Medical Diagnosis
            </div>

            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl text-balance">
              DermAssist AI
            </h1>

            <p className="mt-6 text-lg leading-relaxed text-muted-foreground max-w-xl mx-auto lg:mx-0 text-pretty">
              AI-assisted early skin lesion risk screening for research and
              educational use. Leveraging computer vision to support clinical
              research workflows.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button
                size="lg"
                onClick={onUploadClick}
                className="gap-2"
              >
                <Upload className="h-4 w-4" />
                Upload Image
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={onHowItWorksClick}
                className="gap-2"
              >
                View How It Works
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Right Content - Process Cards */}
          <div className="relative">
            <div className="grid gap-4">
              {/* Card 1 - Upload */}
              <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-all hover:shadow-md">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Upload className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-card-foreground">
                      Image Upload
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Securely upload skin lesion images in JPG or PNG format
                    </p>
                  </div>
                </div>
              </div>

              {/* Card 2 - Analysis */}
              <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-all hover:shadow-md ml-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-accent/10">
                    <Sparkles className="h-6 w-6 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-card-foreground">
                      AI Analysis
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Computer vision model processes visual patterns
                    </p>
                  </div>
                </div>
              </div>

              {/* Card 3 - Results */}
              <div className="rounded-xl border border-border bg-card p-5 shadow-sm transition-all hover:shadow-md">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-success/10">
                    <FileCheck className="h-6 w-6 text-success" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-card-foreground">
                      Risk Screening Result
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Receive categorized risk assessment for clinician review
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
