import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { signup } from '../../lib/api'
import authImage from '../../assets/login_signup.jpg'
import './Signup.css'

const DISEASE_OPTIONS = [
  { value: 'HYPERTENSION', label: '고혈압' },
  { value: 'HYPERLIPIDEMIA', label: '고지혈증' },
  { value: 'DIABETES', label: '당뇨' },
  { value: 'KIDNEY_DISEASE', label: '신장질환' },
]

function Signup() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [gender, setGender] = useState('')
  const [age, setAge] = useState('')
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [chronicDiseases, setChronicDiseases] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleDiseaseChange = (event) => {
    const { value, checked } = event.target

    setChronicDiseases((prev) => {
      if (checked) {
        return [...prev, value]
      }

      return prev.filter((item) => item !== value)
    })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')

    if (!name.trim() || !gender.trim() || !age.trim() || !id.trim() || !password.trim()) {
      setError('기본 정보를 모두 입력해 주세요.')
      return
    }

    if (!height.trim() || !weight.trim()) {
      setError('키와 몸무게를 입력해 주세요.')
      return
    }

    const parsedAge = Number(age)
    const parsedHeight = Number(height)
    const parsedWeight = Number(weight)

    if (
      !Number.isFinite(parsedAge) ||
      !Number.isFinite(parsedHeight) ||
      !Number.isFinite(parsedWeight)
    ) {
      setError('나이, 키, 몸무게는 숫자로 입력해 주세요.')
      return
    }

    setIsLoading(true)

    try {
      await signup({
        name: name.trim(),
        gender: gender.trim(),
        age: parsedAge,
        height: parsedHeight,
        weight: parsedWeight,
        desease: chronicDiseases,
        id: id.trim(),
        password,
      })

      setMessage('회원가입 성공! 로그인 페이지로 이동합니다.')
      navigate('/login')
    } catch (requestError) {
      setError(requestError.message || '회원가입에 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="auth-layout signup-page">
      <div className="auth-panel">
        <h1 className="auth-title">회원가입</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>이름</span>
            <input
              onChange={(event) => setName(event.target.value)}
              placeholder="이름을 입력하세요"
              type="text"
              value={name}
            />
          </label>

          <div className="auth-row-2">
            <label className="field">
              <span>성별</span>
              <select onChange={(event) => setGender(event.target.value)} value={gender}>
                <option value="">선택</option>
                <option value="MALE">남성</option>
                <option value="FEMALE">여성</option>
              </select>
            </label>
            <label className="field">
              <span>나이</span>
              <input
                min="0"
                onChange={(event) => setAge(event.target.value)}
                placeholder="25"
                type="number"
                value={age}
              />
            </label>
          </div>

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

          <div className="auth-row-2">
            <label className="field">
              <span>키(cm)</span>
              <input
                min="0"
                onChange={(event) => setHeight(event.target.value)}
                placeholder="170"
                step="0.1"
                type="number"
                value={height}
              />
            </label>
            <label className="field">
              <span>몸무게(kg)</span>
              <input
                min="0"
                onChange={(event) => setWeight(event.target.value)}
                placeholder="65"
                step="0.1"
                type="number"
                value={weight}
              />
            </label>
          </div>

          <fieldset className="disease-box">
            <legend>만성질환</legend>
            <div className="disease-grid">
              {DISEASE_OPTIONS.map((option) => (
                <label className="disease-item" key={option.value}>
                  <input
                    checked={chronicDiseases.includes(option.value)}
                    onChange={handleDiseaseChange}
                    type="checkbox"
                    value={option.value}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </fieldset>

          {message ? <p className="form-feedback success">{message}</p> : null}
          {error ? <p className="form-feedback error">{error}</p> : null}

          <button className="primary auth-submit" disabled={isLoading} type="submit">
            {isLoading ? '가입 중...' : '회원가입'}
          </button>
        </form>

        <p className="auth-switch">
          이미 계정이 있다면 ? <Link to="/login">로그인</Link>
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

export default Signup