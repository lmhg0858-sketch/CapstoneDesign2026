import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { clearAuthSession, isLoggedIn, notifyAuthStateChanged, subscribeAuthStateChange } from '../../lib/auth'
import './Header.css'

function Header() {
  const navigate = useNavigate()
  const [loggedIn, setLoggedIn] = useState(() => isLoggedIn())

  useEffect(() => subscribeAuthStateChange(setLoggedIn), [])

  const handleLogout = () => {
    clearAuthSession()
    notifyAuthStateChanged()
    alert('로그아웃되었습니다.')
    navigate('/')
  }

  return (
    <header className="header">
      <div className="header__brand">
        <Link className="header__logo" to="/">
          Nutriguide
        </Link>
        <span className="header__tag">만성질환 맞춤 식단 관리</span>
      </div>
      <div className="header__right">
        {loggedIn ? (
          <button className="header__pill header__pill--dark" onClick={handleLogout} type="button">
            로그아웃
          </button>
        ) : (
          <>
            <Link className="header__pill" to="/login">
              로그인
            </Link>
            <Link className="header__pill header__pill--dark" to="/signup">
              회원가입
            </Link>
          </>
        )}
      </div>
    </header>
  )
}

export default Header
