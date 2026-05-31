export type AuditLog = {
  id: number;
  trace_id: string;
  timestamp: string;
  user_request: {
    customer_id?: string;
    claim_type?: string;
    claim_amount?: number;
    claim_text?: string;
  };
  agent_name: string;
  action_requested: string;
  agent_output: {
    recommended_action?: string;
    reasoning?: string;
    confidence_score?: number;
    evidence?: string[];
    [key: string]: unknown;
  };
  governance_decision: string;
  policy_reasons: string[];
  risk_score: number;
  risk_level: string;
  prompt_injection_detected: boolean;
  approval_status: string;
  final_status: string;
};

export type TraceEvent = {
  trace_id: string;
  event_type: string;
  payload: Record<string, unknown>;
};
