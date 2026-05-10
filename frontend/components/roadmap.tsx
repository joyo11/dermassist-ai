"use client";

import { CheckCircle, Circle } from "lucide-react";
import { cn } from "@/lib/utils";

const phases = [
  {
    phase: 1,
    title: "Public Dataset Testing",
    description:
      "Initial model training and validation using ISIC and HAM10000 public datasets.",
    status: "completed",
  },
  {
    phase: 2,
    title: "Model Comparison",
    description:
      "Benchmarking multiple architectures (ResNet, EfficientNet, ViT) for optimal performance.",
    status: "completed",
  },
  {
    phase: 3,
    title: "UI Prototype",
    description:
      "Development of user-friendly interface for research demonstration and testing.",
    status: "in-progress",
  },
  {
    phase: 4,
    title: "Clinical/Research Collaboration Proposal",
    description:
      "Preparing documentation and proposals for academic and clinical partnerships.",
    status: "upcoming",
  },
  {
    phase: 5,
    title: "Early-Stage Image Validation",
    description:
      "Expanded validation with diverse image sources and clinical feedback integration.",
    status: "upcoming",
  },
];

export function Roadmap() {
  return (
    <section className="bg-background py-16 sm:py-24">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Research Roadmap
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Our phased approach to developing and validating this research tool
          </p>
        </div>

        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border md:left-1/2 md:-translate-x-0.5" />

          <div className="space-y-8">
            {phases.map((item, index) => {
              const isCompleted = item.status === "completed";
              const isInProgress = item.status === "in-progress";
              const isEven = index % 2 === 0;

              return (
                <div
                  key={item.phase}
                  className={cn(
                    "relative flex items-start gap-6 md:gap-0",
                    isEven ? "md:flex-row" : "md:flex-row-reverse"
                  )}
                >
                  {/* Timeline Dot */}
                  <div className="absolute left-4 md:left-1/2 -translate-x-1/2 z-10">
                    {isCompleted ? (
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-success text-success-foreground">
                        <CheckCircle className="h-5 w-5" />
                      </div>
                    ) : isInProgress ? (
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                        <div className="h-3 w-3 rounded-full bg-primary-foreground animate-pulse" />
                      </div>
                    ) : (
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-muted-foreground border-2 border-border">
                        <Circle className="h-4 w-4" />
                      </div>
                    )}
                  </div>

                  {/* Content Card */}
                  <div
                    className={cn(
                      "ml-14 md:ml-0 md:w-[calc(50%-2rem)]",
                      isEven ? "md:pr-8 md:text-right" : "md:pl-8 md:text-left"
                    )}
                  >
                    <div
                      className={cn(
                        "rounded-xl border bg-card p-5 transition-all hover:shadow-md",
                        isCompleted && "border-success/30",
                        isInProgress && "border-primary/50 shadow-sm",
                        !isCompleted && !isInProgress && "border-border"
                      )}
                    >
                      <div
                        className={cn(
                          "inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium mb-3",
                          isCompleted && "bg-success/10 text-success",
                          isInProgress && "bg-primary/10 text-primary",
                          !isCompleted &&
                            !isInProgress &&
                            "bg-muted text-muted-foreground"
                        )}
                      >
                        Phase {item.phase}
                        {isInProgress && (
                          <span className="relative flex h-2 w-2">
                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                            <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-card-foreground mb-2">
                        {item.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {item.description}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
