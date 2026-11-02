# 261102_todolist

Python Flask로 만든 할일 관리 앱입니다.

## 기능
- 할일 추가 (우선순위: 높음/보통/낮음, 마감일)
- 완료/미완료 전환, 수정, 삭제, 완료 항목 일괄 삭제
- 전체/진행중/완료 필터, 제목 검색
- 진행률 표시, 마감일 지난 항목 강조
- SQLite(`todos.db`)에 저장

## 실행 방법
```bash
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe app.py
```
브라우저에서 http://127.0.0.1:5001 접속
