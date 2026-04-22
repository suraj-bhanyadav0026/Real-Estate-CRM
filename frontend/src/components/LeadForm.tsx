import { useState } from 'react'
import { LeadStatus } from '../types/lead'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@radix-ui/react-select'

interface LeadFormProps {
  onSuccess: () => void
  initialData?: Partial<Lead>
}

const LeadForm = ({ onSuccess, initialData }: LeadFormProps) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    budget_min: '',
    source: 'website',
    status: 'new' as LeadStatus,
    ...initialData,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Call mutation or emit
    onSuccess()
    console.log('Create lead', formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Name</label>
          <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Phone</label>
          <Input value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} required />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">Email</label>
        <Input value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} type="email" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Budget Min</label>
          <Input type="number" value={formData.budget_min} onChange={(e) => setFormData({...formData, budget_min: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Source</label>
          <Select value={formData.source} onValueChange={(v) => setFormData({...formData, source: v})}>
            <SelectTrigger>
              <SelectValue placeholder="Select source" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="website">Website</SelectItem>
              <SelectItem value="ads">Ads</SelectItem>
              <SelectItem value="referral">Referral</SelectItem>
              <SelectItem value="whatsapp">WhatsApp</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <Button type="submit" className="w-full">
        Save Lead
      </Button>
    </form>
  )
}

export default LeadForm

