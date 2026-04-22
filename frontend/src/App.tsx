import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner' // Later or use toast
import Sidebar from './components/Sidebar'
import LeadsPage from './pages/LeadsPage'
import { useAuth } from './contexts/AuthContext'
import LoginPage from './pages/LoginPage'

function App() {
  const { user, token } = useAuth()

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {token ? (
          <div className="flex">
            <Sidebar />
            <main className="flex-1 p-8">
              <Routes>
                <Route path="/" element={<Navigate to="/leads" />} />
                <Route path="/leads" element={<LeadsPage />} />
                <Route path="/login" element={<Navigate to="/leads" />} />
              </Routes>
            </main>
          </div>
        ) : (
          <LoginPage />
        )}
        <Toaster />
      </div>
    </Router>
  )
}

export default App

