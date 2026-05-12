import './Ranking.css'

function Ranking() {
  return (
    <section className="page ranking-page">
      <h1 className="page__title">랭킹 대시보드</h1>
      <div className="grid">
        <div className="card ranking-card-box">회원 랭킹</div>
        <div className="card ranking-card-box">랭킹 상세</div>
      </div>
    </section>
  )
}

export default Ranking
