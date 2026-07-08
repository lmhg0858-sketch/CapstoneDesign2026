import { useEffect, useMemo, useState } from 'react'
import rankingMedalImage from '../../assets/ranking-medal.png'
import { getAuthUserId, isLoggedIn } from '../../lib/auth'
import { getRankings } from '../../lib/api'
import './Ranking.css'

const podiumDisplayOrder = [2, 1, 3]

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

function getPodiumTone(rank) {
  if (rank === 1) return 'gold'
  if (rank === 2) return 'silver'
  return 'bronze'
}

function getPodiumHeight(rank) {
  if (rank === 1) return 220
  if (rank === 2) return 160
  return 120
}

function Ranking() {
  const [rankingEntries, setRankingEntries] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const loggedIn = isLoggedIn()
  const authUserId = getAuthUserId()

  useEffect(() => {
    let isMounted = true

    const loadRankings = async () => {
      setIsLoading(true)
      setError('')

      try {
        const response = await getRankings()

        if (!isMounted) return
        setRankingEntries(normalizeRankingEntries(response?.ranking))
      } catch (requestError) {
        if (!isMounted) return
        setRankingEntries([])
        setError(requestError.message || '랭킹 정보를 불러오지 못했습니다.')
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadRankings()

    return () => {
      isMounted = false
    }
  }, [])

  const topThree = useMemo(
    () =>
      podiumDisplayOrder
        .map((rank) => rankingEntries.find((entry) => entry.rank === rank))
        .filter(Boolean),
    [rankingEntries]
  )

  const currentUser = useMemo(
    () => rankingEntries.find((entry) => entry.userId === authUserId) || null,
    [authUserId, rankingEntries]
  )

  return (
    <section className="page ranking-page-v2">
      <header className="ranking-page-v2__hero card card--soft">
        <div className="ranking-page-v2__hero-copy">
          <span className="ranking-page-v2__eyebrow">Leaderboard</span>
          <h1 className="page__title">전체 랭킹</h1>
          <p className="page__desc">
            상위 유저 포디움과 전체 순위를 확인하고, 내 현재 평균 점수와 순위를 한 화면에서 볼 수 있습니다.
          </p>
        </div>

        <div className="ranking-page-v2__hero-medal" aria-hidden="true">
          <img alt="" src={rankingMedalImage} />
        </div>
      </header>

      <section className="ranking-podium card">
        <div className="ranking-podium__topline">
          <span className="dashboard-card__eyebrow">Podium</span>
        </div>

        {error ? <p className="form-feedback error">{error}</p> : null}

        {isLoading ? (
          <div className="ranking-empty">
            <h3>랭킹을 불러오는 중입니다.</h3>
            <p>전체 유저의 평균 점수를 정리하고 있어요.</p>
          </div>
        ) : topThree.length ? (
          <div className="ranking-podium__stage">
            {topThree.map((entry) => (
              <article className={`podium-slot podium-slot--${getPodiumTone(entry.rank)}`} key={entry.rank}>
                {entry.rank === 1 ? (
                  <div className="podium-slot__star" aria-hidden="true">
                    ★
                  </div>
                ) : null}
                <div className="podium-slot__nickname">{entry.nickname}</div>
                <div className="podium-slot__score">{formatRankingScore(entry.averageScore)}점</div>
                <div className="podium-slot__block" style={{ height: `${getPodiumHeight(entry.rank)}px` }}>
                  <span className="podium-slot__place">{entry.rank}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="ranking-empty">
            <h3>로그인 후 확인할 수 있습니다.</h3>
            
          </div>
        )}
      </section>

      <section className="ranking-layout">
        <div className="ranking-list card">
          <div className="ranking-list__head">
            <div>
              <span className="dashboard-card__eyebrow">All Users</span>
              <h2>전체 순위</h2>
            </div>
            <span className="ranking-list__count">총 {rankingEntries.length}명</span>
          </div>

          {isLoading ? (
            <div className="ranking-empty">
              <h3>전체 순위를 불러오는 중입니다.</h3>
              <p>잠시만 기다려 주세요.</p>
            </div>
          ) : rankingEntries.length ? (
            <div className="ranking-table" role="table" aria-label="전체 유저 랭킹">
              <div className="ranking-table__head" role="row">
                <span role="columnheader">순위</span>
                <span role="columnheader">닉네임</span>
                <span role="columnheader">평균 점수</span>
              </div>

              <div className="ranking-table__body">
                {rankingEntries.map((entry) => (
                  <div
                    className={currentUser?.userId === entry.userId ? 'ranking-row ranking-row--me' : 'ranking-row'}
                    key={`${entry.rank}-${entry.userId}`}
                    role="row"
                  >
                    <span className="ranking-row__rank">{entry.rank}</span>
                    <span className="ranking-row__nickname">
                      {entry.nickname}
                      {currentUser?.userId === entry.userId ? <em>ME</em> : null}
                    </span>
                    <strong className="ranking-row__score">{formatRankingScore(entry.averageScore)}</strong>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="ranking-empty">
              <h3>로그인 후 확인할 수 있습니다.</h3>
              
            </div>
          )}
        </div>

        <aside className="ranking-sidebar">
          <article className="card ranking-my-card">
            <span className="dashboard-card__eyebrow">My Ranking</span>
            <h2>내 순위</h2>

            {!loggedIn ? (
              <div className="ranking-empty ranking-empty--compact">
                <h3>로그인 후 확인할 수 있습니다.</h3>
                
              </div>
            ) : currentUser ? (
              <>
                <div className="ranking-my-card__stats">
                  <div>
                    <span>현재순위</span>
                    <strong>{currentUser.rank}위</strong>
                  </div>
                  <div>
                    <span>평균 점수</span>
                    <strong>{formatRankingScore(currentUser.averageScore)}점</strong>
                  </div>
                  <div>
                    <span>누적 식사 수</span>
                    <strong>{currentUser.mealCount}회</strong>
                  </div>
                </div>

                <p className="ranking-my-card__desc">
                  {currentUser.nickname}님의 현재 랭킹입니다. 평균 점수와 식사 수를 기준으로 순위가 계산됩니다.
                </p>
              </>
            ) : (
              <div className="ranking-empty ranking-empty--compact">
                <h3>내 랭킹 정보가 없습니다.</h3>
                <p>현재 로그인한 사용자 ID와 일치하는 랭킹 데이터가 아직 없습니다.</p>
              </div>
            )}
          </article>
        </aside>
      </section>
    </section>
  )
}

export default Ranking
