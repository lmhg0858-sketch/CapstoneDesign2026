import { useMemo, useState } from 'react'
import { analyzeFoodImage } from '../../lib/api'
import './Diet.css'

const RISK_LABEL_MAP = {
  safe: '안전',
  warning: '주의',
  danger: '위험',
}

const DEFAULT_NUTRITION_KEYS = [
  '열량(kcal)',
  '탄수화물(g)',
  '단백질(g)',
  '지방(g)',
  '나트륨(mg)',
]

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error('이미지 파일을 읽는 데 실패했습니다.'))

    reader.readAsDataURL(file)
  })
}

function normalizeRiskLevel(riskLevel) {
  if (riskLevel === 'safe' || riskLevel === 'SAFE') return 'safe'
  if (riskLevel === 'warning' || riskLevel === 'WARNING') return 'warning'
  if (riskLevel === 'danger' || riskLevel === 'DANGER') return 'danger'
  if (riskLevel === '안전') return 'safe'
  if (riskLevel === '주의') return 'warning'
  if (riskLevel === '위험') return 'danger'

  return 'warning'
}

function calcScore(items) {
  if (!items.length) return 0

  const score = items.reduce((acc, item) => {
    const risk = normalizeRiskLevel(item.risk_level)

    if (risk === 'safe') return acc + 33
    if (risk === 'warning') return acc + 22

    return acc + 10
  }, 0)

  return Math.max(0, Math.min(100, Math.round(score / items.length * 3)))
}

function normalizeCoordinate(value) {
  if (typeof value === 'number') return value
  const parsed = Number(value)

  return Number.isFinite(parsed) ? parsed : 0
}

function getPositionPercent(x, y, naturalWidth, naturalHeight) {
  if (!naturalWidth || !naturalHeight) {
    return { xPercent: 50, yPercent: 50 }
  }

  // Handle both normalized(0~1) and pixel coordinates.
  const normX = x <= 1 ? x : x / naturalWidth
  const normY = y <= 1 ? y : y / naturalHeight

  return {
    xPercent: Math.max(0, Math.min(100, normX * 100)),
    yPercent: Math.max(0, Math.min(100, normY * 100)),
  }
}

function Diet() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [imageNaturalSize, setImageNaturalSize] = useState({ width: 0, height: 0 })

  const detectedItems = result?.data?.detected_items || []
  const aiAdvice = result?.data?.ai_evaluation?.content || result?.data?.ai_evaluation?.contents || ''
  const score = useMemo(() => calcScore(detectedItems), [detectedItems])

  const nutritionRows = useMemo(() => {
    if (!detectedItems.length) return []

    return detectedItems.map((item) => {
      const nutrition = item.nutrition || {}

      return {
        foodName: item.food_name,
        values: DEFAULT_NUTRITION_KEYS.map((key) => ({
          key,
          value: nutrition[key] ?? '-',
        })),
      }
    })
  }, [detectedItems])

  const handleFileChange = async (event) => {
    const selected = event.target.files?.[0]

    if (!selected) return

    setError('')
    setResult(null)
    setFile(selected)

    try {
      const dataUrl = await readFileAsDataUrl(selected)
      setPreviewUrl(dataUrl)
    } catch (fileError) {
      setError(fileError.message)
    }
  }

  const handleAnalyze = async () => {
    if (!file || !previewUrl) {
      setError('먼저 사진을 업로드해 주세요.')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      const response = await analyzeFoodImage({
        mime_type: file.type || 'image/jpeg',
        image_base64: previewUrl,
      })

      setResult(response)
    } catch (requestError) {
      setError(requestError.message || 'AI 분석 요청에 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="diet-page">
      <h1 className="page__title">식단 기록</h1>

      <div className="diet-upload card">
        <label className="diet-upload__dropzone" htmlFor="diet-image-input">
          {previewUrl ? (
            <img alt="업로드한 음식 사진" src={previewUrl} />
          ) : (
            <span>사진을 업로드해 주세요.</span>
          )}
        </label>
        <input
          accept="image/png,image/jpeg"
          id="diet-image-input"
          onChange={handleFileChange}
          type="file"
        />
        <button className="primary diet-upload__button" onClick={handleAnalyze} type="button">
          AI 분석
        </button>
      </div>

      {error ? <p className="form-feedback error">{error}</p> : null}

      {isLoading ? (
        <div className="diet-loading card" role="status">
          <div className="diet-loading__spinner" />
          <p>AI가 음식 이미지를 분석하고 있어요...</p>
        </div>
      ) : null}

      {!isLoading && result ? (
        <section className="diet-result card">
          <div className="diet-result__top">
            <div className="diet-result__image-wrap">
              <img
                alt="분석된 음식"
                onLoad={(event) => {
                  setImageNaturalSize({
                    width: event.currentTarget.naturalWidth,
                    height: event.currentTarget.naturalHeight,
                  })
                }}
                src={previewUrl}
              />
              {detectedItems.map((item, index) => {
                const coordinate = item.coordinates || item.coordinate || {}
                const x = normalizeCoordinate(coordinate.x)
                const y = normalizeCoordinate(coordinate.y)
                const { xPercent, yPercent } = getPositionPercent(
                  x,
                  y,
                  imageNaturalSize.width,
                  imageNaturalSize.height
                )
                const riskClass = normalizeRiskLevel(item.risk_level)

                return (
                  <div
                    className={`diet-marker diet-marker--${riskClass}`}
                    key={`${item.food_name}-${index}`}
                    style={{ left: `${xPercent}%`, top: `${yPercent}%` }}
                  >
                    <strong>{item.food_name}</strong>
                    <span>{RISK_LABEL_MAP[riskClass]}</span>
                  </div>
                )
              })}
            </div>

            <div className="diet-result__summary">
              <div className="diet-score">
                <h2>점수</h2>
                <p className="diet-score__value">{score}점</p>
                <small>점수 API 연동 전 임시 계산값</small>
              </div>

              <div className="diet-advice">
                <h2>AI 조언</h2>
                <p>{aiAdvice || 'AI 조언 정보가 없습니다.'}</p>
              </div>
            </div>
          </div>

          <div className="diet-result__bottom">
            <h2>인식된 음식 영양 정보</h2>
            {nutritionRows.length ? (
              <div className="diet-nutrition-list">
                {nutritionRows.map((row) => (
                  <article className="diet-nutrition-card" key={row.foodName}>
                    <h3>{row.foodName}</h3>
                    <ul>
                      {row.values.map((item) => (
                        <li key={item.key}>
                          <span>{item.key}</span>
                          <strong>{item.value}</strong>
                        </li>
                      ))}
                    </ul>
                  </article>
                ))}
              </div>
            ) : (
              <p>영양 정보 API 연동 전입니다. 현재는 음식명만 표시됩니다.</p>
            )}
          </div>
        </section>
      ) : null}
    </section>
  )
}

export default Diet
