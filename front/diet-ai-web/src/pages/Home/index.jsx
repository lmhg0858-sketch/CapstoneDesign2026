import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <section className="home-page">
      <section className="home-hero">
        <div className="home-hero__overlay" />
        <div className="home-hero__content">
          <header className="home-topbar">
            <Link className="home-topbar__brand" to="/">
              NutriGuide
            </Link>
            <nav className="home-topbar__menu">
              <Link to="/mypage">마이페이지</Link>
              <Link to="/signup">회원가입</Link>
              <Link className="home-topbar__login" to="/login">
                로그인
              </Link>
            </nav>
          </header>

          <div className="home-hero__center">
            <h1>NutriGuide</h1>
            <p>만성질환자를 위한 맞춤 식단 관리와 AI 영양 분석 서비스를 제공합니다.</p>
            <div className="row">
              <Link className="primary button-link" to="/diet">
                식단 기록하기
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="home-sections">
        <article className="home-card">
          <h2>식사 분석 및 기록</h2>
          <p>사진을 업로드해 식사 영양소를 확인하고 마음 편히 식사하세요!</p>
          <div className="row">
            <Link className="primary button-link" to="/analyze">
              분석하기
            </Link>
            <Link className="ghost button-link" to="/diet">
              기록 보기
            </Link>
          </div>
        </article>

        <article className="home-card">
          <h2>오늘의 목표</h2>
          <p>사용자들 중 나는 몇 순위 ?! 지금 확인해보세요!</p>
          <div className="row">
            <Link className="primary button-link" to="/ranking">
              순위 보기
            </Link>
            <Link className="ghost button-link" to="/mypage">
              내 정보
            </Link>
          </div>
        </article>

        <article className="home-card home-card--media">
          <h2>랭킹</h2>
          <p>전체 이용자의 4% 골드 등급이에요! 꾸준한 노력과 관리..! 정말 대단해요!!</p>
          <div className="medal-art" aria-hidden="true">🏅</div>
        </article>

        <article className="home-card home-card--media">
          <h2>식단 추천</h2>
          <p>오늘 후식으로는 부족한 비타민을 채우기 위한 과일 한 접시 어떠신가요?</p>
          <div className="fruit-art" aria-hidden="true" />
        </article>
      </section>
    </section>
  )
}

export default Home