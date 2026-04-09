import { Link } from 'react-router-dom'

function FoodAnalyze() {
  return (
    <section className="page">
      <h1 className="page__title">음식 사진 분석</h1>
      <div className="grid">
        <div className="card">음식 사진</div>
        <div className="card">AI 조언</div>
      </div>
      <div className="row">
        <button className="primary" type="button">음식 분석</button>
        <Link className="ghost button-link" to="/diet">
          돌아가기
        </Link>
      </div>
    </section>
  )
}

export default FoodAnalyze