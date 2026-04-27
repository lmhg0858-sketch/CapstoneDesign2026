import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { clearAuthSession, isLoggedIn, notifyAuthStateChanged, subscribeAuthStateChange } from '../../lib/auth'
import heroImage from '../../assets/login_signup.jpg'
import './Home.css'

const DISEASE_OPTIONS = [
  { id: 'diabetes', label: '당뇨병' },
  { id: 'hypertension', label: '고혈압' },
  { id: 'hyperlipidemia', label: '고지혈증' },
]

const NUTRIENT_BY_DISEASE = {
  diabetes: [
    { name: '탄수화물', unit: 'g', target: 280, intake: 232 },
    { name: '식이섬유', unit: 'g', target: 25, intake: 18 },
    { name: '단백질', unit: 'g', target: 65, intake: 58 },
    { name: '나트륨', unit: 'mg', target: 2000, intake: 1620 },
    { name: '칼륨', unit: 'mg', target: 3500, intake: 2600 },
  ],
  hypertension: [
    { name: '나트륨', unit: 'mg', target: 1500, intake: 1280 },
    { name: '칼륨', unit: 'mg', target: 3500, intake: 2300 },
    { name: '칼슘', unit: 'mg', target: 700, intake: 520 },
    { name: '마그네슘', unit: 'mg', target: 350, intake: 270 },
    { name: '식이섬유', unit: 'g', target: 25, intake: 16 },
  ],
  hyperlipidemia: [
    { name: '포화지방', unit: 'g', target: 15, intake: 18 },
    { name: '식이섬유', unit: 'g', target: 25, intake: 14 },
    { name: '오메가3', unit: 'mg', target: 1000, intake: 620 },
    { name: '콜레스테롤', unit: 'mg', target: 300, intake: 220 },
    { name: '단백질', unit: 'g', target: 65, intake: 50 },
  ],
}

const RANKING_INFO = {
  tier: 'Silver',
  score: 87,
  rank: 32,
  percentile: '상위 8%',
}

const RECOMMENDATIONS = {
  diabetes: [
    '현미밥 + 두부구이 + 나물 2종',
    '그릭요거트 + 블루베리 + 견과류 소량',
    '저녁 간식은 방울토마토/오이로 대체',
  ],
  hypertension: [
    '저염 된장국 + 생선구이 + 채소반찬',
    '바나나, 아보카도, 시금치로 칼륨 보충',
    '가공식품/국물류는 오늘 1회 이하로 제한',
  ],
  hyperlipidemia: [
    '귀리 + 두유 + 과일 토핑 조합',
    '등푸른생선 또는 아마씨로 오메가3 보충',
    '튀김류 대신 구이/찜 조리법 선택',
  ],
}

function formatAmount(value, unit) {
  return `${value.toLocaleString()}${unit}`
}

function Home() {
  const navigate = useNavigate()
  const [selectedDisease, setSelectedDisease] = useState(DISEASE_OPTIONS[0].id)
  const [loggedIn, setLoggedIn] = useState(() => isLoggedIn())
  const rows = NUTRIENT_BY_DISEASE[selectedDisease]

  useEffect(() => subscribeAuthStateChange(setLoggedIn), [])

  const maxTarget = useMemo(() => rows.reduce((max, row) => Math.max(max, row.target), 1), [rows])

  const completionRate = useMemo(() => {
    const totalTarget = rows.reduce((sum, row) => sum + row.target, 0)
    const totalIntake = rows.reduce((sum, row) => sum + row.intake, 0)
    if (!totalTarget) return 0
    return Math.round((totalIntake / totalTarget) * 100)
  }, [rows])

  const deficientNutrients = useMemo(() => rows.filter((row) => row.intake < row.target).slice(0, 3), [rows])

  const handleLogout = () => {
    clearAuthSession()
    notifyAuthStateChanged()
    alert('로그아웃되었습니다.')
    navigate('/')
  }

  return (
    <section className="home-page-v2">
      <section className="home-hero-v2" style={{ backgroundImage: `url(${heroImage})` }}>
        <div className="home-hero-v2__overlay" />
        <div className="home-hero-v2__content">
          <header className="home-header-v2">
            <Link className="home-header-v2__brand" to="/">
              NutriGuide
            </Link>
            <nav className="home-header-v2__menu">
              <Link to="/mypage">마이페이지</Link>
              {!loggedIn ? <Link to="/signup">회원가입</Link> : null}
              {loggedIn ? (
                <button className="home-header-v2__login" onClick={handleLogout} type="button">
                  로그아웃
                </button>
              ) : (
                <Link className="home-header-v2__login" to="/login">
                  로그인
                </Link>
              )}
            </nav>
          </header>

          <div className="home-hero-v2__center">
            <h1>NutriGuide</h1>
            <p>만성질환자를 위한 맞춤 식단 관리와 AI 영양 분석 서비스를 제공합니다.</p>
            <Link className="home-hero-v2__cta" to="/diet">
              식단 기록하기
            </Link>
          </div>
        </div>
      </section>

      <section className="home-dashboard">
        <article className="dashboard-card nutrient-card">
          <div className="dashboard-card__head">
            <h2>하루누적영양소</h2>
            <div className="disease-tabs" role="tablist" aria-label="질환 선택">
              {DISEASE_OPTIONS.map((item) => (
                <button
                  key={item.id}
                  className={item.id === selectedDisease ? 'tab tab--active' : 'tab'}
                  onClick={() => setSelectedDisease(item.id)}
                  type="button"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          <div className="nutrient-layout">
            <div className="target-chart" aria-label="하루 권장 섭취량 그래프">
              <h3>권장 섭취량</h3>
              <div className="target-chart__bars">
                {rows.map((row) => {
                  const height = Math.max(16, Math.round((row.target / maxTarget) * 100))
                  return (
                    <div className="target-bar" key={row.name}>
                      <div className="target-bar__track">
                        <div className="target-bar__fill" style={{ height: `${height}%` }} />
                      </div>
                      <span className="target-bar__label">{row.name}</span>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="intake-chart" aria-label="내 누적 섭취량 그래프">
              <h3>나의 누적 섭취량</h3>
              <ul>
                {rows.map((row) => {
                  const ratio = Math.max(0, Math.min(140, Math.round((row.intake / row.target) * 100)))
                  return (
                    <li key={`${row.name}-intake`}>
                      <div className="intake-chart__meta">
                        <strong>{row.name}</strong>
                        <span>
                          {formatAmount(row.intake, row.unit)} / {formatAmount(row.target, row.unit)}
                        </span>
                      </div>
                      <div className="intake-chart__track">
                        <div className="intake-chart__fill" style={{ width: `${Math.min(100, ratio)}%` }} />
                      </div>
                    </li>
                  )
                })}
              </ul>
              <p className="intake-chart__summary">오늘 목표 달성률: {completionRate}%</p>
            </div>
          </div>
        </article>

        <article className="dashboard-card ranking-card">
          <h2>랭킹</h2>
          <div className="ranking-badge" aria-hidden="true">
            🏅
          </div>
          <dl>
            <div>
              <dt>등급</dt>
              <dd>{RANKING_INFO.tier}</dd>
            </div>
            <div>
              <dt>점수</dt>
              <dd>{RANKING_INFO.score}점</dd>
            </div>
            <div>
              <dt>현재순위</dt>
              <dd>{RANKING_INFO.rank}위 ({RANKING_INFO.percentile})</dd>
            </div>
          </dl>
          <Link className="dashboard-link" to="/ranking">
            전체 랭킹 보기
          </Link>
        </article>

        <article className="dashboard-card recommend-card">
          <h2>식단추천</h2>
          <p className="recommend-subtitle">현재 부족한 영양소 우선으로 추천해드려요.</p>
          <div className="recommend-chips">
            {deficientNutrients.length ? (
              deficientNutrients.map((row) => <span key={`${row.name}-chip`}>{row.name}</span>)
            ) : (
              <span>모든 주요 영양소를 잘 채우고 있어요</span>
            )}
          </div>
          <ul className="recommend-list">
            {RECOMMENDATIONS[selectedDisease].map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <Link className="dashboard-link" to="/diet">
            오늘 식단 기록하러 가기
          </Link>
        </article>
      </section>
    </section>
  )
}

export default Home
