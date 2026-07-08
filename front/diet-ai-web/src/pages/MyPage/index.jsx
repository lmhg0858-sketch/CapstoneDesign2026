import './MyPage.css'

function MyPage() {
  return (
    <section className="page mypage">
      <h1 className="page__title">마이페이지</h1>
      <div className="card mypage__card">
        <div className="row mypage__row">
          <div className="avatar" />
          <div className="list">
            <strong>회원 정보</strong>
            <span className="page__desc">프로필 사진 등록 및 정보 수정</span>
            <div className="row">
              <button className="ghost" type="button">수정</button>
              <button className="primary" type="button">저장</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default MyPage
