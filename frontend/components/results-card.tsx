"use client";

import { AlertCircle, CheckCircle, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export interface AnalysisResult {
  prediction: string;
  risk_category: "Low Risk" | "Medium Risk" | "High Risk";
  confidence: number;
  explanation: string;
  disclaimer: string;
  /** Base64 PNG from Grad-CAM overlay (no data-URL prefix); absent without checkpoint or when disabled. */
  gradcam_image_base64?: string | null;
  attention_heatmap_label?: string | null;
  attention_heatmap_disclaimer?: string | null;
}

interface ResultsCardProps {
  result: AnalysisResult;
}

const riskConfig = {
  "Low Risk": {
    icon: CheckCircle,
    bgColor: "bg-success/10",
    textColor: "text-success",
    borderColor: "border-success/30",
    badgeBg: "bg-success",
    badgeText: "text-success-foreground",
  },
  "Medium Risk": {
    icon: AlertTriangle,
    bgColor: "bg-warning/10",
    textColor: "text-warning",
    borderColor: "border-warning/30",
    badgeBg: "bg-warning",
    badgeText: "text-warning-foreground",
  },
  "High Risk": {
    icon: AlertCircle,
    bgColor: "bg-destructive/10",
    textColor: "text-destructive",
    borderColor: "border-destructive/30",
    badgeBg: "bg-destructive",
    badgeText: "text-destructive-foreground",
  },
};

export function ResultsCard({ result }: ResultsCardProps) {
  const config = riskConfig[result.risk_category];
  const Icon = config.icon;

  return (
    <section className="bg-muted/30 py-16 sm:py-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold tracking-tight text-foreground">
            Analysis Results
          </h2>
          <p className="mt-4 text-muted-foreground">
            AI-generated risk assessment for clinician review
          </p>
        </div>

        <div
          className={cn(
            "rounded-2xl border-2 bg-card p-6 sm:p-8 shadow-sm",
            config.borderColor
          )}
        >
          {/* Risk Category Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
            <div className="flex items-center gap-4">
              <div
                className={cn(
                  "flex h-14 w-14 items-center justify-center rounded-full",
                  config.bgColor
                )}
              >
                <Icon className={cn("h-7 w-7", config.textColor)} />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Risk Category
                </p>
                <p className={cn("text-2xl font-bold", config.textColor)}>
                  {result.risk_category}
                </p>
              </div>
            </div>
            <div
              className={cn(
                "inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold",
                config.badgeBg,
                config.badgeText
              )}
            >
              {result.risk_category}
            </div>
          </div>

          {/* Results Grid */}
          <div className="grid gap-6 sm:grid-cols-2 mb-8">
            <div className="rounded-xl bg-muted/50 p-5">
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Confidence Score
              </p>
              <div className="flex items-end gap-2">
                <span className="text-3xl font-bold text-foreground">
                  {Math.round(result.confidence * 100)}%
                </span>
              </div>
              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className={cn("h-full rounded-full", config.badgeBg)}
                  style={{ width: `${result.confidence * 100}%` }}
                />
              </div>
            </div>

            <div className="rounded-xl bg-muted/50 p-5">
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Model Output
              </p>
              <p className="text-xl font-semibold text-foreground">
                {result.prediction}
              </p>
            </div>
          </div>

          {/* Explanation */}
          <div className="rounded-xl bg-muted/50 p-5 mb-6">
            <p className="text-sm font-medium text-muted-foreground mb-2">
              Explanation
            </p>
            <p className="whitespace-pre-wrap text-foreground leading-relaxed">
              {result.explanation}
            </p>
          </div>

          {/* Grad-CAM overlay (optional; requires DERMASSIST_CHECKPOINT + include_gradcam) */}
          {result.gradcam_image_base64 ? (
            <div className="rounded-xl border border-border bg-muted/30 p-5 mb-6">
              <p className="text-sm font-semibold text-foreground mb-3">
                {result.attention_heatmap_label ?? "Model Attention Heatmap"}
              </p>
              <div className="overflow-hidden rounded-lg border border-border bg-background">
                <img
                  alt=""
                  className="mx-auto max-h-80 w-auto max-w-full object-contain"
                  src={`data:image/png;base64,${result.gradcam_image_base64}`}
                />
              </div>
              <p className="mt-3 text-xs text-muted-foreground leading-relaxed">
                {result.attention_heatmap_disclaimer ??
                  "This heatmap shows model attention, not medical evidence."}
              </p>
            </div>
          ) : null}

          {/* Disclaimer */}
          <div className="flex items-start gap-3 rounded-lg bg-info/10 border border-info/30 p-4">
            <Info className="h-5 w-5 shrink-0 text-info mt-0.5" />
            <div>
              <p className="text-sm font-medium text-foreground">
                Important Notice
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                {result.disclaimer} AI output is not a diagnosis. This result
                should be reviewed by a licensed clinician.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
