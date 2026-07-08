import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  clearAuthSession,
  getAuthUserId,
  isLoggedIn,
  notifyAuthStateChanged,
  subscribeAuthStateChange,
} from '../../lib/auth'
import { getCumulativeRiskNutrients, getDayRecommendation, getRankings } from '../../lib/api'
import heroImage from '../../assets/login_signup.jpg'
import rankingMedalImage from '../../assets/ranking-medal.png'
import './Home.css'

const DISEASE_LABELS = {
  DIABETES: '당뇨',
  HYPERTENSION: '고혈압',
  HYPERLIPIDEMIA: '고지혈증',
  KIDNEY_DISEASE: '신장질환',
}

const TRAFFIC_LIGHT_STATES = [
  { key: 'danger', label: '빨강' },
  { key: 'warning', label: '노랑' },
  { key: 'safe', label: '초록' },
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

  return Array.from({ length: steps + 1 }, (_, index) => ({
    value: Math.round((roundedMax / steps) * index),
    percent: (index / steps) * 100,
  }))
}

function normalizeRiskLevel(value) {
  if (!value) return 'warning'

  const normalized = `${value}`.trim().toLowerCase()

  if (normalized === '위험' || normalized === 'danger' || normalized === 'red') return 'danger'
  if (normalized === '주의' || normalized === 'warning' || normalized === 'yellow') return 'warning'
  if (normalized === '안전' || normalized === 'safe' || normalized === 'green') return 'safe'

  return 'warning'
}

function normalizeRecommendation(data) {
  const evaluation = data?.day_evaluation || {}
  const recommendations = Array.isArray(data?.day_recom) ? data.day_recom : []

  return {
    riskLevel: normalizeRiskLevel(evaluation.risk_level),
    riskLabel: evaluation.risk_level || '주의',
    evaluationContent: evaluation.evaluation_content || '아직 평가 코멘트가 없습니다.',
    foods: recommendations.map((item, index) => ({
      id: item?.id || `${item?.food_name || 'food'}-${index}`,
      foodName: item?.food_name || '이름 없는 음식',
      content: item?.content || '',
    })),
  }
}

function normalizeRankingEntries(items) {
  if (!Array.isArray(items)) return []

  return items
    .map((item) => {
      const rank = Number(item?.rank)
      const averageScore = Number(item?.averageScore)
      const mealCount = Number(item?.mealCount)

      return {
        rank: Number.isFinite(rank) ? rank : null,
        userId: item?.userId ? `${item.userId}` : '',
        nickname: item?.nickname ? `${item.nickname}` : '이름 없음',
        averageScore: Number.isFinite(averageScore) ? averageScore : 0,
        mealCount: Number.isFinite(mealCount) ? mealCount : 0,
      }
    })
    .filter((item) => item.rank !== null)
    .sort((a, b) => a.rank - b.rank)
}

function formatRankingScore(value) {
  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) return '-'
  if (Number.isInteger(numericValue)) return `${numericValue}`

  return numericValue.toFixed(1)
}

function Home() {
  const navigate = useNavigate()
  const [loggedIn, setLoggedIn] = useState(() => isLoggedIn())
  const [dashboardData, setDashboardData] = useState(null)
  const [isDashboardLoading, setIsDashboardLoading] = useState(false)
  const [dashboardError, setDashboardError] = useState('')
  const [recommendationData, setRecommendationData] = useState(null)
  const [isRecommendationLoading, setIsRecommendationLoading] = useState(false)
  const [recommendationError, setRecommendationError] = useState('')
  const [rankingEntries, setRankingEntries] = useState([])
  const [isRankingLoading, setIsRankingLoading] = useState(false)
  const [rankingError, setRankingError] = useState('')

  useEffect(() => subscribeAuthStateChange(setLoggedIn), [])

  useEffect(() => {
    const userId = getAuthUserId()
    const date = formatTodayDate()

    if (!loggedIn || !userId) {
      setDashboardData(null)
      setDashboardError('')
      setIsDashboardLoading(false)
      setRecommendationData(null)
      setRecommendationError('')
      setIsRecommendationLoading(false)
      return
    }

    let isMounted = true

    const loadDashboard = async () => {
      setIsDashboardLoading(true)
      setDashboardError('')

      try {
        const response = await getCumulativeRiskNutrients({ userId, date })

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

    const loadRecommendation = async () => {
      setIsRecommendationLoading(true)
      setRecommendationError('')

      try {
        const response = await getDayRecommendation({ userId, date })

        if (!isMounted) return
        setRecommendationData(response)
      } catch (requestError) {
        if (!isMounted) return
        setRecommendationData(null)
        setRecommendationError(requestError.message || '식단 추천을 불러오지 못했습니다.')
      } finally {
        if (isMounted) {
          setIsRecommendationLoading(false)
        }
      }
    }

    loadDashboard()
    loadRecommendation()

    return () => {
      isMounted = false
    }
  }, [loggedIn])

  useEffect(() => {
    let isMounted = true

    const loadRankings = async () => {
      setIsRankingLoading(true)
      setRankingError('')

      try {
        const response = await getRankings()

        if (!isMounted) return
        setRankingEntries(normalizeRankingEntries(response?.ranking))
      } catch (requestError) {
        if (!isMounted) return
        setRankingEntries([])
        setRankingError(requestError.message || '랭킹 정보를 불러오지 못했습니다.')
      } finally {
        if (isMounted) {
          setIsRankingLoading(false)
        }
      }
    }

    loadRankings()

    return () => {
      isMounted = false
    }
  }, [])

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
  const recommendation = useMemo(() => normalizeRecommendation(recommendationData), [recommendationData])

  const heroHighlights = nutrientRows.slice(0, 3)
  const userDiseases = dashboardData?.user_diseases || dashboardData?.userDiseases || []
  const userDiseaseLabels = userDiseases.map(getDiseaseLabel)
  const dashboardDateLabel = formatDisplayDate(dashboardData?.date)
  const hasDashboardData = nutrientRows.length > 0
  const hasRecommendations = recommendation.foods.length > 0
  const authUserId = getAuthUserId()
  const currentRanking = useMemo(
    () => rankingEntries.find((entry) => entry.userId === authUserId) || null,
    [authUserId, rankingEntries]
  )
  const topRankingEntry = rankingEntries[0] || null

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
              <p>로그인한 사용자의 섭취 영양소 비교 대시보드를 불러옵니다.</p>
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
          <div className="recommend-card__head">
            <span className="dashboard-card__eyebrow">Recommendation</span>
            <h2>식단추천</h2>
            <p className="recommend-subtitle">AI가 하루 식단 상태를 평가하고 추천 음식을 정리해 보여줍니다.</p>
          </div>

          {recommendationError ? <p className="form-feedback error">{recommendationError}</p> : null}

          {!loggedIn ? (
            <div className="dashboard-empty">
              <h3>식단 추천을 보려면 로그인해 주세요.</h3>
              <p>로그인한 사용자 기준으로 AI 일일 평가와 추천 음식 목록을 가져옵니다.</p>
            </div>
          ) : isRecommendationLoading ? (
            <div className="dashboard-empty">
              <h3>식단 추천을 불러오는 중입니다.</h3>
              <p>오늘 식단 상태를 평가하고 추천 음식 목록을 정리하고 있어요.</p>
            </div>
          ) : recommendationData ? (
            <div className="recommend-layout">
              <section className="recommend-foods">
                <h3>추천 음식</h3>
                {hasRecommendations ? (
                  <ul className="recommend-food-list">
                    {recommendation.foods.map((item) => (
                      <li className="recommend-food-item" key={item.id}>
                        <div className="recommend-food-item__bullet" aria-hidden="true" />
                        <div className="recommend-food-item__content">
                          <strong>{item.foodName}</strong>
                          <p>{item.content || '추천 내용이 없습니다.'}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="recommend-empty">추천 음식 데이터가 없습니다.</p>
                )}
              </section>

              <section className="recommend-evaluation">
                <div className="traffic-signal" aria-label={`위험도 ${recommendation.riskLabel}`}>
                  {TRAFFIC_LIGHT_STATES.map((state) => (
                    <div
                      className={
                        recommendation.riskLevel === state.key
                          ? `traffic-light traffic-light--${state.key} traffic-light--active`
                          : `traffic-light traffic-light--${state.key}`
                      }
                      key={state.key}
                    />
                  ))}
                </div>

                <div className="evaluation-comment">
                  <span className="evaluation-comment__label">평가 코멘트</span>
                  <p>{recommendation.evaluationContent}</p>
                </div>
              </section>
            </div>
          ) : (
            <div className="dashboard-empty">
              <h3>식단 추천 데이터가 없습니다.</h3>
              <p>AI 응답에서 `day_evaluation`과 `day_recom`이 오면 이 카드에 표시됩니다.</p>
            </div>
          )}
        </article>

        <article className="dashboard-card ranking-card dashboard-card--wide">
          <div className="ranking-sketch">
            <div className="ranking-sketch__title-wrap">
              <div className="ranking-sketch__head">
                <span className="dashboard-card__eyebrow">Momentum</span>
                <Link className="ranking-sketch__button" to="/ranking">
                  전체 랭킹 보기
                </Link>
              </div>

              <div className="ranking-sketch__header">
                <h2>랭킹</h2>
              </div>
              <p className="dashboard-card__lead">
                꾸준한 식단관리를 돕도록 랭킹 시스템을 제공합니다.
              </p>
            </div>

            {rankingError ? <p className="form-feedback error">{rankingError}</p> : null}

            <div className="ranking-sketch__body">
              <div className="ranking-sketch__left">
                <div className="ranking-medal">
                  <img alt="랭킹 메달" className="ranking-medal__image" src={rankingMedalImage} />
                </div>
                {topRankingEntry ? (
                  <div className="ranking-sketch__top-user">
                    <span>현재 1위</span>
                    <strong>{topRankingEntry.nickname}</strong>
                  </div>
                ) : null}
              </div>

              <div className="ranking-stat ranking-stat--rank">
                <span className="ranking-stat__label">현재순위</span>
                {!loggedIn ? (
                  <>
                    <p className="ranking-stat__value ranking-stat__value--empty">-</p>
                    <span className="ranking-stat__meta">로그인 후 내 순위를 확인할 수 있습니다.</span>
                  </>
                ) : isRankingLoading ? (
                  <>
                    <p className="ranking-stat__value ranking-stat__value--empty">...</p>
                    <span className="ranking-stat__meta">랭킹 불러오는 중</span>
                  </>
                ) : currentRanking ? (
                  <>
                    <p className="ranking-stat__value">
                      {currentRanking.rank}
                      <small>위</small>
                    </p>
                    <span className="ranking-stat__meta">{currentRanking.nickname}</span>
                  </>
                ) : (
                  <>
                    <p className="ranking-stat__value ranking-stat__value--empty">-</p>
                    <span className="ranking-stat__meta">현재 사용자 랭킹 정보가 없습니다.</span>
                  </>
                )}
              </div>

              <div className="ranking-stat ranking-stat--score">
                <span className="ranking-stat__label">점수</span>
                {!loggedIn ? (
                  <>
                    <p className="ranking-stat__value ranking-stat__value--empty">-</p>
                    <span className="ranking-stat__meta">로그인 후 내 평균 점수를 확인할 수 있습니다.</span>
                  </>
                ) : isRankingLoading ? (
                  <>
                    <p className="ranking-stat__value ranking-stat__value--empty">...</p>
                    <span className="ranking-stat__meta">랭킹 불러오는 중</span>
                  </>
                ) : currentRanking ? (
                  <>
                    <p className="ranking-stat__value">
                      {formatRankingScore(currentRanking.averageScore)}
                    </p>
                    <span className="ranking-stat__meta">식사 {currentRanking.mealCount}회 기준 평균 점수</span>
                  </>
                ) : (
                  <>
                    <p className="ranking-stat__value ranking-stat__value--empty">-</p>
                    <span className="ranking-stat__meta">현재 사용자 점수 정보가 없습니다.</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </article>
      </section>
    </section>
  )
}

export default Home
