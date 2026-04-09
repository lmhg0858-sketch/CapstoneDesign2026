import { Link } from 'react-router-dom'
import './Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header__brand">
        <Link className="header__logo" to="/">
          Nutriguide
        </Link>
        <span className="header__tag">만성질환 맞춤 식단 관리</span>
      </div>
      <div className="header__right">
        <Link className="header__pill" to="/login">
          로그인
        </Link>
        <Link className="header__pill header__pill--dark" to="/signup">
          회원가입
        </Link>
      </div>
    </header>
  )
}

export default Header