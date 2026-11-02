# 261102_todolist

Python Flask로 만든 할일 관리 앱입니다.

## 기능
- 할일 추가 (우선순위: 높음/보통/낮음, 마감일)
- 완료/미완료 전환, 수정, 삭제, 완료 항목 일괄 삭제
- 전체/진행중/완료 필터, 제목 검색
- 진행률 표시, 마감일 지난 항목 강조
- 저장소: 환경변수 `DATABASE_URL`이 있으면 Supabase(Postgres), 없으면 로컬 SQLite(`todos.db`)

## Supabase 연결
1. Supabase 프로젝트 생성 후 **Connect → Transaction pooler** 연결 문자열 복사
2. Vercel 프로젝트 **Settings → Environment Variables**에 `DATABASE_URL`로 등록 후 Redeploy
3. 로컬에서 쓰려면 `.env.example`을 `.env`로 복사해 값 입력
4. `todos` 테이블은 앱 시작 시 자동 생성 (`schema.sql`로 직접 만들어도 됨)

## 실행 방법
```bash
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe app.py
```
브라우저에서 http://127.0.0.1:5001 접속
