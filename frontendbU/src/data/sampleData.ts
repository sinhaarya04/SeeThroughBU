export interface CheckoutIssue {
  id: string;
  icon: string;
  text: string;
  type: "fee" | "trial" | "prechecked" | "domain";
  severity: "high" | "medium" | "low";
}

export const sampleIssues: CheckoutIssue[] = [
  {
    id: "1",
    icon: "💳",
    text: 'Hidden "processing fee" detected · +$3.99',
    type: "fee",
    severity: "high"
  },
  {
    id: "2",
    icon: "⏱️",
    text: "Auto-renewal in 7 days (trial)",
    type: "trial",
    severity: "high"
  },
  {
    id: "3",
    icon: "☑️",
    text: 'Pre-checked add-on: "Purchase Protection Plus"',
    type: "prechecked",
    severity: "medium"
  },
  {
    id: "4",
    icon: "🎭",
    text: "Suspicious domain: tradinginterview.co",
    type: "domain",
    severity: "high"
  }
];

export interface ImpactStats {
  feesAvoided: number;
  subsPaused: number;
  riskScore: number;
}

export const initialImpactStats: ImpactStats = {
  feesAvoided: 0,
  subsPaused: 0,
  riskScore: 0
};
