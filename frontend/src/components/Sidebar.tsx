import { LayoutDashboard, Users, MapPin, FileText, BarChart3, User, LogOut } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../lib/utils'

const Sidebar = () => {
  const { user, logout } = useAuth()

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-screen p-4 flex flex-col">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-navy-900 mb-2">AgnaYI</h2>
        <p className="text-sm text-gray-500">Real Estate CRM</p>
      </div>
      <nav className="flex-1 space-y-2">
        <Link to="/leads" className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-100 transition-colors">
          <Users className="w-5 h-5" />
          <span>Leads</span>
        </Link>
        {/* More modules */}
      </nav>
      <div className="mt-auto pt-4 border-t">
        <div className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-100 cursor-pointer" onClick={logout}>
          <User className="w-5 h-5" />
          <span>{user?.email}</span>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

