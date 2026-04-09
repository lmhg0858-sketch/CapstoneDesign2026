import { Outlet, useLocation } from 'react-router-dom'
import Header from '../components/Header/Header'
import NavBar from '../components/NavBar/NavBar'

function RootLayout() {
  const location = useLocation()
  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup'
  const isHomePage = location.pathname === '/'
  const hideDefaultNav = isAuthPage || isHomePage

  const contentClassName = [
    'app-content',
    isAuthPage ? 'app-content--auth' : '',
    isHomePage ? 'app-content--home' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className="app-shell">
      {!hideDefaultNav ? <Header /> : null}
      {!hideDefaultNav ? <NavBar /> : null}
      <main className={contentClassName}>
        <Outlet />
      </main>
    </div>
  )
}

export default RootLayout