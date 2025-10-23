import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId
    
    console.log('Next.js API 路由收到 status 請求:', sessionId)
    console.log('轉發到後端:', `${BACKEND_URL}/api/inspire/status/${sessionId}`)
    
    const response = await fetch(`${BACKEND_URL}/api/inspire/status/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const error = await response.text()
      console.error('後端 API 錯誤:', response.status, error)
      return NextResponse.json(
        { error: '後端 API 調用失敗', details: error },
        { status: response.status }
      )
    }

    const data = await response.json()
    console.log('後端 API 響應:', data)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Next.js API 路由錯誤:', error)
    return NextResponse.json(
      { error: '內部服務器錯誤', details: error instanceof Error ? error.message : '未知錯誤' },
      { status: 500 }
    )
  }
}
