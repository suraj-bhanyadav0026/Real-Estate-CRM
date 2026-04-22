import { Lead } from '../types/lead'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { MoreHorizontal, Phone, Mail, Edit3, Trash2, ArrowRight } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

interface LeadTableProps {
  leads: Lead[]
  onStatusUpdate: (id: number, status: string) => void
  onDelete: (id: number) => void
  isLoading: boolean
}

const statusColors: Record<string, string> = {
  new: 'bg-yellow-100 text-yellow-800',
  contacted: 'bg-blue-100 text-blue-800',
  qualified: 'bg-green-100 text-green-800',
  // ...
  'closed_won': 'bg-emerald-100 text-emerald-800',
  'closed_lost': 'bg-red-100 text-red-800',
  default: 'bg-gray-100 text-gray-800',
}

const LeadsTable = ({ leads, onStatusUpdate, onDelete, isLoading }: LeadTableProps) => {
  const { user } = useAuth()

  if (isLoading) return <div className="animate-pulse">Loading...</div>

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Name</th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Phone</th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Score</th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Assigned</th>
            <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {leads.map((lead) => (
            <tr key={lead.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{lead.name}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <a href={`tel:${lead.phone}`} className="text-primary-600 hover:text-primary-500 text-sm">
                  {lead.phone}
                </a>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="w-16 bg-gradient-to-r from-green-400 to-blue-500 rounded-full p-1 text-white text-xs font-bold text-center">
                  {lead.score}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Badge className={statusColors[lead.status] || statusColors.default}>
                  {lead.status.replace('_', ' ').toUpperCase()}
                </Badge>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {lead.assigned_to?.email || 'Unassigned'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end space-x-2">
                  <Button variant="ghost" size="sm" onClick={() => onStatusUpdate(lead.id, 'contacted')}>
                    Contacted <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onDelete(lead.id)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default LeadsTable

