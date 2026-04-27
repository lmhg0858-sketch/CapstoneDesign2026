import { createBrowserRouter } from 'react-router-dom'
import RootLayout from './RootLayout'
import Home from '../pages/Home'
import Login from '../pages/Login'
import Signup from '../pages/Signup'
import Diet from '../pages/Diet'
import Ranking from '../pages/Ranking'
import MyPage from '../pages/MyPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'login', element: <Login /> },
      { path: 'signup', element: <Signup /> },
      { path: 'diet', element: <Diet /> },
      { path: 'ranking', element: <Ranking /> },
      { path: 'mypage', element: <MyPage /> },
    ],
  },
])
