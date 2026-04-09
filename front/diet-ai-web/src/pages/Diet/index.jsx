import { Link } from 'react-router-dom'

function Diet() {
  return (
    <section className="page">
      <h1 className="page__title">식단 기록</h1>
      <div className="grid">
        <div className="card">사진 입력</div>
        <div className="card">텍스트 입력</div>
        <Link className="card button-link" to="/analyze">
          AI 음식인식 시작
        </Link>
        <Link className="card button-link" to="/ranking">
          평가 시작
        </Link>
      </div>
      <div className="panel">
        <h2>이전 식단 요약</h2>
        <p>최근 기록된 식단을 카드 형태로 표시</p>
      </div>
    </section>
  )
}

export default Diet