"use client";

import { Activity } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <Activity className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xl font-bold text-foreground">
              DermAssist AI
            </span>
          </div>

          {/* Disclaimer */}
          <p className="text-center text-sm text-muted-foreground max-w-lg">
            DermAssist AI is a research prototype and not a medical device. This
            tool is intended for educational and research purposes only and
            should not be used for clinical diagnosis.
          </p>

          {/* Links */}
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <a
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Privacy Policy
            </a>
            <a
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Terms of Use
            </a>
            <a
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Research Documentation
            </a>
            <a
              href="#"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Contact
            </a>
          </div>

          {/* Copyright */}
          <div className="pt-6 border-t border-border w-full text-center">
            <p className="text-xs text-muted-foreground">
              © {new Date().getFullYear()} DermAssist AI Research Project. All
              rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
