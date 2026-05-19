import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  clearAuthSession,
  getAuthUserId,
  isLoggedIn,
  notifyAuthStateChanged,
  subscribeAuthStateChange,
} from '../../lib/auth'
import { getCumulativeRiskNutrients } from '../../lib/api'
import heroImage from '../../assets/login_signup.jpg'
import './Home.css'

const DISEASE_LABELS = {
  DIABETES: '당뇨',
  HYPERTENSION: '고혈압',
  HYPERLIPIDEMIA: '고지혈증',
  KIDNEY_DISEASE: '신장질환',
}

const RANKING_INFO = {
  tier: 'Silver',
  score: 87,
  rank: 32,
  percentile: '상위 8%',
}

const GENERIC_RECOMMENDATIONS = [
  '부족한 영양소가 많은 식사는 다음 끼니에서 보완하도록 구성해 보세요.',
  '적정량을 초과한 영양소는 국물류, 가공식품, 디저트 섭취를 줄이면서 조절해 보세요.',
  '오늘 기록을 계속 쌓아두면 질환 맞춤 추천 정확도가 더 좋아집니다.',
]

function formatAmount(value, unit) {
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return `- ${unit}`

  return `${numericValue.toLocaleString()}${unit}`
}

function formatTodayDate() {
  return new Date().toISOString().slice(0, 10)
}

function formatDisplayDate(value) {
  if (!value) return '오늘'

  const [year, month, day] = value.split('-')
  if (!year || !month || !day) return value

  return `${year}.${month}.${day}`
}

function getDiseaseLabel(disease) {
  return DISEASE_LABELS[disease] || disease
}

function normalizeNutrients(items) {
  if (!Array.isArray(items)) return []

  return items
    .map((item) => {
      const recommendedDailyLimit = Number(item?.recommended_daily_limit)
      const cumulativeValue = Number(item?.cumulative_value)

      return {
        nutrientKey: item?.nutrient_key || item?.nutrient_name || 'unknown',
        nutrientName: item?.nutrient_name || item?.nutrient_key || '영양소',
        unit: item?.unit || '',
        recommendedDailyLimit: Number.isFinite(recommendedDailyLimit) ? recommendedDailyLimit : 0,
        cumulativeValue: Number.isFinite(cumulativeValue) ? cumulativeValue : 0,
      }
    })
    .filter((item) => item.nutrientName)
}

function buildChartTicks(maxValue, steps = 4) {
  const safeMax = Math.max(maxValue, 1)
  const roundedMax = Math.ceil(safeMax / steps) * steps

  return Array.from({ length: steps + 1 }, (_, index) => {
    const value = Math.round((roundedMax / steps) * index)
    return {
      value,
      percent: (index / steps) * 100,
    }
  })
}

function Home() {
  const navigate = useNavigate()
  const [loggedIn, setLoggedIn] = useState(() => isLoggedIn())
  const [dashboardData, setDashboardData] = useState(null)
  const [isDashboardLoading, setIsDashboardLoading] = useState(false)
  const [dashboardError, setDashboardError] = useState('')

  useEffect(() => subscribeAuthStateChange(setLoggedIn), [])

  useEffect(() => {
    const userId = getAuthUserId()

    if (!loggedIn || !userId) {
      setDashboardData(null)
      setDashboardError('')
      setIsDashboardLoading(false)
      return
    }

    let isMounted = true

    const loadDashboard = async () => {
      setIsDashboardLoading(true)
      setDashboardError('')

      try {
        const response = await getCumulativeRiskNutrients({
          userId,
          date: formatTodayDate(),
        })

        if (!isMounted) return
        setDashboardData(response)
      } catch (requestError) {
        if (!isMounted) return
        setDashboardData(null)
        setDashboardError(requestError.message || '영양소 대시보드를 불러오지 못했습니다.')
      } finally {
        if (isMounted) {
          setIsDashboardLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      isMounted = false
    }
  }, [loggedIn])

  const nutrientRows = useMemo(
    () => normalizeNutrients(dashboardData?.cumulative_risk_nutrients),
    [dashboardData]
  )

  const maxNutrientValue = useMemo(() => {
    if (!nutrientRows.length) return 1

    return nutrientRows.reduce((max, row) => {
      const candidate = Math.max(row.recommendedDailyLimit, row.cumulativeValue)
      return Math.max(max, candidate, 1)
    }, 1)
  }, [nutrientRows])

  const chartTicks = useMemo(() => buildChartTicks(maxNutrientValue), [maxNutrientValue])

  const completionRate = useMemo(() => {
    const totalLimit = nutrientRows.reduce((sum, row) => sum + row.recommendedDailyLimit, 0)
    const totalIntake = nutrientRows.reduce((sum, row) => sum + row.cumulativeValue, 0)

    if (!totalLimit) return 0

    return Math.round((totalIntake / totalLimit) * 100)
  }, [nutrientRows])

  const deficientNutrients = useMemo(
    () =>
      nutrientRows
        .filter((row) => row.cumulativeValue < row.recommendedDailyLimit)
        .sort((a, b) => {
          const gapA = a.recommendedDailyLimit - a.cumulativeValue
          const gapB = b.recommendedDailyLimit - b.cumulativeValue
          return gapB - gapA
        })
        .slice(0, 4),
    [nutrientRows]
  )

  const exceededNutrients = useMemo(
    () => nutrientRows.filter((row) => row.cumulativeValue > row.recommendedDailyLimit).slice(0, 4),
    [nutrientRows]
  )

  const heroHighlights = nutrientRows.slice(0, 3)
  const userDiseaseLabels = (dashboardData?.user_diseases || []).map(getDiseaseLabel)
  const dashboardDateLabel = formatDisplayDate(dashboardData?.date)
  const hasDashboardData = nutrientRows.length > 0

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
        <div className="home-hero-v2__ambient home-hero-v2__ambient--left" />
        <div className="home-hero-v2__ambient home-hero-v2__ambient--right" />
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
            <span className="home-hero-v2__eyebrow">Personal Nutrition Intelligence</span>
            <h1>NutriGuide</h1>
            <p>만성질환자를 위한 맞춤 식단 관리와 AI 영양 분석 서비스를 제공합니다.</p>
            <div className="home-hero-v2__actions">
              <Link className="home-hero-v2__cta" to="/diet">
                식단 기록하기
              </Link>
              <Link className="home-hero-v2__secondary" to="/ranking">
                내 랭킹 보기
              </Link>
            </div>
          </div>

          <div className="home-hero-v2__highlights">
            {heroHighlights.length ? (
              heroHighlights.map((row, index) => (
                <article
                  className="hero-highlight"
                  key={row.nutrientKey}
                  style={{ animationDelay: `${0.18 * index}s` }}
                >
                  <span className="hero-highlight__label">{row.nutrientName}</span>
                  <strong>{formatAmount(row.cumulativeValue, row.unit)}</strong>
                  <small>권장 {formatAmount(row.recommendedDailyLimit, row.unit)}</small>
                </article>
              ))
            ) : (
              <article className="hero-highlight hero-highlight--empty">
                <span className="hero-highlight__label">Nutrition Snapshot</span>
                <strong>{loggedIn ? '데이터 준비 중' : '로그인 필요'}</strong>
                <small>
                  {loggedIn
                    ? '대시보드가 연결되면 핵심 수치가 여기에 표시됩니다.'
                    : '개인 맞춤 영양소 대시보드를 보려면 로그인해 주세요.'}
                </small>
              </article>
            )}
          </div>
        </div>
      </section>

      <section className="home-dashboard home-dashboard--stacked">
        <article className="dashboard-card dashboard-card--feature dashboard-card--wide">
          <div className="dashboard-card__head">
            <span className="dashboard-card__eyebrow">Daily Focus</span>
            <h2>하루 누적 영양소</h2>
            <p className="dashboard-card__lead">
              영양소별 적정량과 실제 섭취량을 한 화면에서 비교할 수 있도록 가로형 그래프로 표시합니다.
            </p>
            <div className="dashboard-meta-row">
              <span className="dashboard-date">{dashboardDateLabel} 기준</span>
              <div className="dashboard-disease-chips">
                {userDiseaseLabels.length ? (
                  userDiseaseLabels.map((disease) => <span key={disease}>{disease}</span>)
                ) : (
                  <span>질환 정보 없음</span>
                )}
              </div>
            </div>
          </div>

          {dashboardError ? <p className="form-feedback error">{dashboardError}</p> : null}

          {!loggedIn ? (
            <div className="dashboard-empty">
              <h3>개인화 대시보드를 보려면 로그인해 주세요.</h3>
              <p>로그인한 사용자 `userId`와 오늘 날짜로 영양소 비교 대시보드를 불러옵니다.</p>
              <Link className="dashboard-link" to="/login">
                로그인하러 가기
              </Link>
            </div>
          ) : isDashboardLoading ? (
            <div className="dashboard-empty">
              <h3>영양소 대시보드를 불러오는 중입니다.</h3>
              <p>오늘 누적 영양소와 권장 섭취량을 정리하고 있어요.</p>
            </div>
          ) : hasDashboardData ? (
            <div className="nutrient-panel">
              <div className="nutrient-panel__top">
                <div className="comparison-legend" aria-label="그래프 범례">
                  <span>
                    <i className="comparison-legend__swatch comparison-legend__swatch--recommended" />
                    적정량
                  </span>
                  <span>
                    <i className="comparison-legend__swatch comparison-legend__swatch--actual" />
                    실제 섭취량
                  </span>
                </div>
                <div className="nutrient-panel__score">
                  <strong>{completionRate}%</strong>
                  <span>전체 적정량 대비</span>
                </div>
              </div>

              <div className="nutrient-chart">
                <div className="nutrient-chart__axis" aria-hidden="true">
                  <div className="nutrient-chart__axis-label" />
                  <div className="nutrient-chart__ticks">
                    {chartTicks.map((tick) => (
                      <span
                        className="nutrient-chart__tick"
                        key={`tick-${tick.value}`}
                        style={{ left: `${tick.percent}%` }}
                      >
                        {tick.value.toLocaleString()}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="nutrient-chart__body">
                  {nutrientRows.map((row, index) => {
                    const recommendedWidth = (row.recommendedDailyLimit / maxNutrientValue) * 100
                    const actualWidth = (row.cumulativeValue / maxNutrientValue) * 100
                    const intakeRatio = row.recommendedDailyLimit
                      ? Math.round((row.cumulativeValue / row.recommendedDailyLimit) * 100)
                      : 0
                    const actualClassName =
                      row.cumulativeValue > row.recommendedDailyLimit
                        ? 'nutrient-bar__fill nutrient-bar__fill--warning'
                        : 'nutrient-bar__fill nutrient-bar__fill--actual'

                    return (
                      <article
                        className="nutrient-row"
                        key={row.nutrientKey}
                        style={{ animationDelay: `${0.06 * index}s` }}
                      >
                        <div className="nutrient-row__label">
                          <strong>{row.nutrientName}</strong>
                          <small>{row.unit}</small>
                        </div>

                        <div className="nutrient-row__chart">
                          <div className="nutrient-bar">
                            <span className="nutrient-bar__name">적정량</span>
                            <div className="nutrient-bar__track">
                              {chartTicks.map((tick) => (
                                <span
                                  className="nutrient-bar__gridline"
                                  key={`${row.nutrientKey}-recommended-${tick.value}`}
                                  style={{ left: `${tick.percent}%` }}
                                />
                              ))}
                              <div
                                className="nutrient-bar__fill nutrient-bar__fill--recommended"
                                style={{ width: `${Math.min(100, recommendedWidth)}%` }}
                              />
                            </div>
                            <strong className="nutrient-bar__value">
                              {formatAmount(row.recommendedDailyLimit, row.unit)}
                            </strong>
                          </div>

                          <div className="nutrient-bar">
                            <span className="nutrient-bar__name">실제</span>
                            <div className="nutrient-bar__track">
                              {chartTicks.map((tick) => (
                                <span
                                  className="nutrient-bar__gridline"
                                  key={`${row.nutrientKey}-actual-${tick.value}`}
                                  style={{ left: `${tick.percent}%` }}
                                />
                              ))}
                              <div
                                className={actualClassName}
                                style={{ width: `${Math.min(100, actualWidth)}%` }}
                              />
                            </div>
                            <strong className="nutrient-bar__value">
                              {formatAmount(row.cumulativeValue, row.unit)}
                            </strong>
                          </div>
                        </div>

                        <div className="nutrient-row__ratio">
                          {Number.isFinite(intakeRatio) ? `${intakeRatio}%` : '0%'}
                        </div>
                      </article>
                    )
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="dashboard-empty">
              <h3>오늘 표시할 영양소 데이터가 없습니다.</h3>
              <p>백엔드에서 `cumulative_risk_nutrients`가 오면 이 영역에 영양소별 비교 그래프가 생성됩니다.</p>
            </div>
          )}
        </article>

        <article className="dashboard-card recommend-card dashboard-card--wide">
          <span className="dashboard-card__eyebrow">Recommendation</span>
          <h2>식단추천</h2>
          <p className="recommend-subtitle">오늘 부족하거나 초과한 영양소를 기준으로 다음 식사를 조정해 보세요.</p>
          <div className="recommend-chips">
            {deficientNutrients.length ? (
              deficientNutrients.map((row) => <span key={`${row.nutrientKey}-chip`}>{row.nutrientName}</span>)
            ) : (
              <span>현재는 부족 영양소가 없습니다</span>
            )}
          </div>
          <div className="recommend-sections">
            <section className="recommend-section">
              <h3>보완이 필요한 영양소</h3>
              {deficientNutrients.length ? (
                <ul className="recommend-list">
                  {deficientNutrients.map((row) => (
                    <li key={`${row.nutrientKey}-deficit`}>
                      {row.nutrientName}: {formatAmount(row.cumulativeValue, row.unit)} /{' '}
                      {formatAmount(row.recommendedDailyLimit, row.unit)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="recommend-empty">현재 부족한 영양소는 없습니다.</p>
              )}
            </section>
            <section className="recommend-section">
              <h3>다음 식사 팁</h3>
              <ul className="recommend-list">
                {GENERIC_RECOMMENDATIONS.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </section>
          </div>
          <Link className="dashboard-link" to="/diet">
            오늘 식단 기록하러 가기
          </Link>
        </article>

        <article className="dashboard-card ranking-card dashboard-card--wide">
          <span className="dashboard-card__eyebrow">Momentum</span>
          <h2>랭킹</h2>
          <p className="dashboard-card__lead">지속적인 기록과 균형 잡힌 식단이 순위로 이어집니다.</p>
          <div className="ranking-grid">
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
                <dd>
                  {RANKING_INFO.rank}위 ({RANKING_INFO.percentile})
                </dd>
              </div>
              <div>
                <dt>초과 영양소 수</dt>
                <dd>{exceededNutrients.length}개</dd>
              </div>
            </dl>
          </div>
          <Link className="dashboard-link" to="/ranking">
            전체 랭킹 보기
          </Link>
        </article>
      </section>
    </section>
  )
}

export default Home
