import { NavLink } from 'react-router-dom'
import './NavBar.css'

const links = [
  { to: '/', label: '홈' },
  { to: '/diet', label: '식단 기록' },
  { to: '/ranking', label: '랭킹 대시보드' },
  { to: '/mypage', label: '마이페이지' },
]

function NavBar() {
  return (
    <nav className="nav">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            isActive ? 'nav__link nav__link--active' : 'nav__link'
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default NavBar