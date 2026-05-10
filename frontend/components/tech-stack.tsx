"use client";

import {
  Code2,
  Server,
  Brain,
  Database,
  Eye,
  MessageSquare,
} from "lucide-react";

const technologies = [
  {
    icon: Code2,
    title: "React Frontend",
    description:
      "Modern React application with TypeScript for type-safe, component-driven UI development.",
  },
  {
    icon: Server,
    title: "FastAPI Backend",
    description:
      "High-performance Python backend with automatic API documentation and async support.",
  },
  {
    icon: Brain,
    title: "PyTorch Model",
    description:
      "Deep learning classification model trained on dermatological image datasets.",
  },
  {
    icon: Database,
    title: "ISIC / HAM10000 Dataset",
    description:
      "Trained and validated using publicly available skin lesion image datasets.",
  },
  {
    icon: Eye,
    title: "Grad-CAM Explainability",
    description:
      "Visual explanations highlighting regions influencing model predictions.",
  },
  {
    icon: MessageSquare,
    title: "LLM Explanation Support",
    description:
      "LLMs may be used only to generate educational summaries and simplify model explanations. The actual image classification is performed by the computer vision model.",
  },
];

export function TechStack() {
  return (
    <section className="bg-muted/30 py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Technology Stack
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Built with modern, reliable technologies for research-grade
            performance
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {technologies.map((tech) => {
            const Icon = tech.icon;
            return (
              <div
                key={tech.title}
                className="group rounded-2xl border border-border bg-card p-6 transition-all hover:border-primary/50 hover:shadow-md"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">
                  {tech.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {tech.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
