"use client";

import { AlertTriangle } from "lucide-react";

export function DisclaimerBanner() {
  return (
    <div className="bg-secondary/80 border-b border-border">
      <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center gap-3">
          <AlertTriangle className="h-4 w-4 shrink-0 text-warning" />
          <p className="text-sm text-secondary-foreground">
            This tool is for educational and research purposes only. It does not
            provide medical diagnosis. Always consult a licensed healthcare
            professional.
          </p>
        </div>
      </div>
    </div>
  );
}
