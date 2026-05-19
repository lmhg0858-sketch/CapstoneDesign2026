const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_API_BASE_URL || 'http://localhost:8080'
const AI_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8000'

const API_PATHS = {
  login: '/api/auth/login',
  signup: '/api/auth/signup',
  analyzeMeal: import.meta.env.VITE_AI_ANALYZE_PATH || '/analyze',
  me: '/api/users/me',
  recentMeals: '/api/meals/recent',
  meals: '/api/meals',
  cumulativeRiskNutrients:
    import.meta.env.VITE_CUMULATIVE_RISK_NUTRIENTS_PATH || '/api/meals/dashboard',
}

function joinApiUrl(baseUrl, path) {
  const normalizedBase = baseUrl.replace(/\/+$/, '')
  let normalizedPath = path.startsWith('/') ? path : `/${path}`

  // Prevent duplicated /api when base URL already includes it.
  if (normalizedBase.endsWith('/api') && normalizedPath.startsWith('/api/')) {
    normalizedPath = normalizedPath.slice(4)
  }

  return `${normalizedBase}${normalizedPath}`
}

async function request(baseUrl, path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  const response = await fetch(joinApiUrl(baseUrl, path), {
    ...options,
    headers,
  })

  let data = null

  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const message = data?.message || 'Request failed'
    const error = new Error(message)
    error.status = response.status
    error.url = joinApiUrl(baseUrl, path)
    throw error
  }

  return data
}

export function login(payload) {
  return request(BACKEND_BASE_URL, API_PATHS.login, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function signup(payload) {
  return request(BACKEND_BASE_URL, API_PATHS.signup, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function analyzeFoodImage(payload) {
  const options = {
    method: 'POST',
    body: JSON.stringify(payload),
  }

  return request(AI_BASE_URL, API_PATHS.analyzeMeal, options).catch((error) => {
    const fallbackPath = '/api/meals/analyze'

    if (error.status === 404 && API_PATHS.analyzeMeal !== fallbackPath) {
      return request(AI_BASE_URL, fallbackPath, options)
    }

    throw error
  })
}

export function getMyProfile() {
  return request(BACKEND_BASE_URL, API_PATHS.me)
}

export function updateMyProfile(payload) {
  return request(BACKEND_BASE_URL, API_PATHS.me, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function getRecentMeals() {
  return request(BACKEND_BASE_URL, API_PATHS.recentMeals)
}

export function createMeal(payload) {
  return request(BACKEND_BASE_URL, API_PATHS.meals, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getCumulativeRiskNutrients({ userId, date }) {
  const params = new URLSearchParams({
    userId: `${userId}`,
    date,
  })

  return request(BACKEND_BASE_URL, `${API_PATHS.cumulativeRiskNutrients}?${params.toString()}`)
}
