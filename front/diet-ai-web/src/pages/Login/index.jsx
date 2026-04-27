import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { login } from '../../lib/api'
import { notifyAuthStateChanged, saveAuthSession } from '../../lib/auth'
import authImage from '../../assets/login_signup.jpg'
import './Login.css'

function Login() {
  const navigate = useNavigate()
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!id.trim() || !password.trim()) {
      const message = 'ID와 비밀번호를 모두 입력해 주세요.'
      setError(message)
      alert(message)
      return
    }

    setIsLoading(true)

    try {
      const response = await login({
        id: id.trim(),
        password,
      })

      const isSuccess = Boolean(response?.token) && Boolean(response?.userId)
      const message = response?.message || (isSuccess ? '로그인에 성공했습니다.' : '로그인에 실패했습니다.')

      if (!isSuccess) {
        setError(message)
        alert(`로그인 실패: ${message}`)
        return
      }

      saveAuthSession({ token: response.token, userId: response.userId })
      notifyAuthStateChanged()

      alert(`로그인 성공: ${message}`)
      navigate('/')
    } catch (requestError) {
      const message = requestError.message || '로그인에 실패했습니다.'
      setError(message)
      alert(`로그인 실패: ${message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="auth-layout login-page">
      <div className="auth-panel">
        <h1 className="auth-title">로그인</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>아이디</span>
            <input
              onChange={(event) => setId(event.target.value)}
              placeholder="아이디를 입력하세요"
              type="text"
              value={id}
            />
          </label>
          <label className="field">
            <span>비밀번호</span>
            <input
              onChange={(event) => setPassword(event.target.value)}
              placeholder="비밀번호를 입력하세요"
              type="password"
              value={password}
            />
          </label>

          {error ? <p className="form-feedback error">{error}</p> : null}

          <button className="primary auth-submit" disabled={isLoading} type="submit">
            {isLoading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <p className="auth-switch">
          계정이 없다면 ? <Link to="/signup">회원가입</Link>
        </p>
      </div>

      <aside
        aria-hidden="true"
        className="auth-visual"
        style={{
          backgroundImage: `linear-gradient(145deg, rgba(255, 255, 255, 0.12), rgba(0, 0, 0, 0.03)), url(${authImage})`,
        }}
      />
    </section>
  )
}

export default Login
