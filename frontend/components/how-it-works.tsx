"use client";

import { Upload, Settings, Brain, UserCheck } from "lucide-react";

const steps = [
  {
    icon: Upload,
    title: "Upload Image",
    description:
      "Upload a clear image of the skin lesion. Supported formats include JPG and PNG for optimal analysis.",
    step: 1,
  },
  {
    icon: Settings,
    title: "Image Preprocessing",
    description:
      "The image is preprocessed and normalized to ensure consistent input for the computer vision model.",
    step: 2,
  },
  {
    icon: Brain,
    title: "Computer Vision Model Analysis",
    description:
      "A trained deep learning model analyzes visual patterns and features associated with various lesion types.",
    step: 3,
  },
  {
    icon: UserCheck,
    title: "Risk Result + Clinician Review",
    description:
      "Results are categorized by risk level and should be reviewed by a licensed healthcare professional.",
    step: 4,
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-background py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            A simple four-step process from image upload to risk assessment
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className="group relative rounded-2xl border border-border bg-card p-6 transition-all hover:border-primary/50 hover:shadow-lg"
              >
                {/* Step Number */}
                <div className="absolute -top-3 -left-3 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
                  {item.step}
                </div>

                {/* Icon */}
                <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <Icon className="h-7 w-7 text-primary" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold text-card-foreground mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {item.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
