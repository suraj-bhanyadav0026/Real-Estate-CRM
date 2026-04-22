export interface Lead {
  id: number
  name: string
  phone: string
  email?: string
  status: string
  score: number
  assigned_to?: {
    id: number
    email: string
    role: string
  }
  created_at: string
}

export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'site_visit_scheduled' | 'negotiation' | 'closed_won' | 'closed_lost'

